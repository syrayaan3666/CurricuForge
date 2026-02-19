import os
import json
import requests
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

from services.logger import get_logger
logger = get_logger("llm_client")

# ================= CONFIG =================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ================= CIRCUIT BREAKER (Quota Fallback) =================
# Once Gemini quota fails, skip Gemini for all subsequent requests
gemini_quota_exhausted = False

# ==========================================


def extract_json(text: str):
    """
    Cleans model output and extracts ONLY JSON body.
    Handles markdown fences, truncation, and brace balancing.
    """
    if not text:
        raise Exception("Empty model response")

    text = text.strip()

    # remove markdown fences if present
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) > 1:
            # prefer the fenced block content
            text = parts[1].strip()

    # find first JSON object start
    start = text.find("{")
    if start == -1:
        raise Exception("No JSON detected in model response")

    # balance braces to find the matching closing brace
    depth = 0
    end = -1
    in_string = False
    escape_next = False
    
    for i in range(start, len(text)):
        ch = text[i]
        
        # Track string boundaries to avoid counting braces inside strings
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        
        # Count braces only outside strings
        if not in_string:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break

    if end == -1:
        # JSON is truncated; try to repair by closing open braces/brackets
        candidate = text[start:]
        
        # Count unclosed braces and brackets
        unclosed_braces = 0
        unclosed_brackets = 0
        in_string = False
        escape_next = False
        
        for ch in candidate:
            if escape_next:
                escape_next = False
                continue
            if ch == '\\':
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if not in_string:
                if ch == '{':
                    unclosed_braces += 1
                elif ch == '}':
                    unclosed_braces -= 1
                elif ch == '[':
                    unclosed_brackets += 1
                elif ch == ']':
                    unclosed_brackets -= 1
        
        # Close unclosed structures
        repair = candidate
        if unclosed_brackets > 0:
            repair += ']' * unclosed_brackets
        if unclosed_braces > 0:
            repair += '}' * unclosed_braces
        
        return repair
    
    candidate = text[start:end + 1]
    return candidate


def detect_truncation(json_str: str) -> bool:
    """
    Checks if JSON appears to be truncated (incomplete).
    Returns True if truncation is likely detected.
    """
    if not json_str:
        return True
    
    json_str = json_str.strip()
    
    # Count unclosed braces and brackets
    unclosed_braces = 0
    unclosed_brackets = 0
    in_string = False
    escape_next = False
    
    for ch in json_str:
        if escape_next:
            escape_next = False
            continue
        if ch == '\\':
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == '{':
                unclosed_braces += 1
            elif ch == '}':
                unclosed_braces -= 1
            elif ch == '[':
                unclosed_brackets += 1
            elif ch == ']':
                unclosed_brackets -= 1
    
    # If there are still unclosed structures after auto-repair, it's likely truncated
    if unclosed_braces > 0 or unclosed_brackets > 0:
        return True
    
    return False
# =====================================================

async def call_llm(system_prompt: str, payload: dict):

    user_prompt = f"""
Input Data:
{json.dumps(payload)}

Return ONLY valid JSON.
No explanations.
No markdown.
"""

    full_prompt = system_prompt + "\n" + user_prompt

    global gemini_quota_exhausted

    # =================================================
    # 1️⃣ TRY GEMINI FIRST — SKIP IF QUOTA EXHAUSTED
    # =================================================
    if not gemini_quota_exhausted:
        try:
            logger.info("Using Gemini provider: Gemini")

            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=[{
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }],
            )

            text = response.text
            logger.debug("LLM raw preview (Gemini): %s", (text or '')[:2000])
            cleaned = extract_json(text)
            logger.debug("Extracted JSON preview (Gemini): %s", (cleaned or '')[:2000])
            
            # Check for truncation
            if detect_truncation(cleaned):
                logger.warning("Gemini output appears truncated (may be incomplete)")

                try:
                    parsed = json.loads(cleaned)
                    logger.info("Gemini success")
                    return parsed
                except json.JSONDecodeError as e:
                    logger.warning("Gemini returned malformed JSON: %s", e)
                # One-time repair attempt: ask the model to correct its previous output
                repair_prompt = system_prompt + "\n" + user_prompt + "\n\nYour previous reply was not valid JSON. Here is the exact text you returned:\n" + (text or '') + "\n\nPlease return ONLY the corrected JSON object matching the expected format. No explanations."

                try:
                    repair_resp = gemini_client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=[{
                            "role": "user",
                            "parts": [{"text": repair_prompt}]
                        }],
                    )
                    text2 = repair_resp.text
                    logger.debug("LLM raw preview (Gemini retry): %s", (text2 or '')[:2000])
                    cleaned2 = extract_json(text2)
                    logger.debug("Extracted JSON preview (Gemini retry): %s", (cleaned2 or '')[:2000])
                    
                    # Check for truncation in retry
                    if detect_truncation(cleaned2):
                        logger.warning("Gemini retry output also appears truncated")
                    
                    parsed2 = json.loads(cleaned2)
                    logger.info("Gemini repair success")
                    return parsed2
                except Exception:
                    logger.warning("Gemini repair failed; falling back to Groq")
                    # fall through to Groq fallback
                    pass

        except Exception as e:
            error_text = str(e)
            logger.error("Gemini failed: %s", error_text)

            # If quota exhausted → mark circuit breaker and go to Groq
            if "RESOURCE_EXHAUSTED" in error_text:
                logger.warning("Gemini quota hit — switching to Groq-only mode...")
                gemini_quota_exhausted = True
    else:
        logger.info("Gemini quota exhausted — skipping to Groq")

    # =================================================
    # 2️⃣ FALLBACK → GROQ PROVIDER
    # =================================================
    try:
        logger.info("Using Groq provider")

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        groq_payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 8000
        }

        response = requests.post(GROQ_URL, headers=headers, json=groq_payload)

        if response.status_code != 200:
            logger.warning("Groq Raw Response: %s", response.text)
            raise Exception(f"Groq HTTP Error: {response.status_code}")

        result = response.json()

        # ===== SAFE PARSING =====
        if isinstance(result, dict):
            # Groq returns standard OpenAI format
            if "error" in result:
                raise Exception(f"Groq Error: {result['error']}")
            elif "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0].get("message", {}).get("content", "")
            else:
                raise Exception(f"Unexpected Groq response: {result}")
        else:
            raise Exception("Invalid Groq response format")

        logger.debug("LLM raw preview (Groq): %s", (text or '')[:2000])
        cleaned = extract_json(text)
        logger.debug("Extracted JSON preview (Groq): %s", (cleaned or '')[:2000])
        
        # Check for truncation
        if detect_truncation(cleaned):
            logger.warning("Groq output appears truncated (may be incomplete)")

        try:
            parsed = json.loads(cleaned)
            logger.info("Groq success")
            return parsed
        except json.JSONDecodeError as e:
            logger.warning("Groq returned malformed JSON: %s", e)
            # One-time repair attempt via Groq
            repair_payload = groq_payload.copy()
            repair_payload["messages"] = [
                {"role": "user", "content": system_prompt + "\n" + user_prompt + "\n\nPrevious output:\n" + (text or '') + "\n\nReturn ONLY corrected JSON."}
            ]

            try:
                repair_resp = requests.post(GROQ_URL, headers=headers, json=repair_payload)
                if repair_resp.status_code == 200:
                    repair_result = repair_resp.json()
                    text2 = repair_result.get("choices", [])[0].get("message", {}).get("content", "")
                    logger.debug("LLM raw preview (Groq retry): %s", (text2 or '')[:2000])
                    cleaned2 = extract_json(text2)
                    logger.debug("Extracted JSON preview (Groq retry): %s", (cleaned2 or '')[:2000])
                    
                    # Check for truncation in retry
                    if detect_truncation(cleaned2):
                        logger.warning("Groq retry output also appears truncated")
                    
                    parsed2 = json.loads(cleaned2)
                    logger.info("Groq repair success")
                    return parsed2
            except Exception:
                logger.error("Groq repair failed")
                raise

    except Exception as e:
        logger.exception("All LLM providers failed: %s", repr(e))
        raise Exception(f"All LLM providers failed → {repr(e)}")
