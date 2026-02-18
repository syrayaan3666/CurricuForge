import os
import json
import requests
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

# ================= CONFIG =================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://api-inference.huggingface.co/models/gpt2"

# Gemini client
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================


def extract_json(text: str):
    """
    Cleans model output and extracts ONLY JSON body.
    Handles markdown fences and extra tokens.
    """
    if not text:
        raise Exception("Empty model response")

    text = text.strip()

    # remove markdown fences
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) > 1:
            text = parts[1]

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise Exception("No JSON detected in model response")

    return text[start:end + 1]


# =====================================================
# MAIN PROVIDER ROUTER
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

    # =================================================
    # 1️⃣ TRY GEMINI FIRST (PRIMARY PROVIDER)
    # =================================================
    try:
        print("🤖 Using Gemini provider")

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[{
                "role": "user",
                "parts": [{"text": full_prompt}]
            }],
        )

        text = response.text
        cleaned = extract_json(text)

        print("✅ Gemini success")
        return json.loads(cleaned)

    except Exception as e:

        error_text = str(e)
        print("⚠ Gemini failed:", error_text)

        # If quota exhausted → wait once before fallback
        if "RESOURCE_EXHAUSTED" in error_text:
            print("⏳ Gemini quota hit — waiting 5 seconds before fallback...")
            await asyncio.sleep(5)

    # =================================================
    # 2️⃣ FALLBACK → HUGGINGFACE PROVIDER
    # =================================================
    try:
        print("🧠 Switching to HuggingFace fallback")

        headers = {
            "Authorization": f"Bearer {HF_API_KEY}"
        }

        hf_payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 1500,
                "temperature": 0.3
            }
        }

        response = requests.post(HF_URL, headers=headers, json=hf_payload)

        if response.status_code != 200:
            print("⚠ HF Raw Response:", response.text)
            raise Exception(f"HF HTTP Error: {response.status_code}")

        result = response.json()

        # ===== SAFE PARSING =====
        if isinstance(result, list) and len(result) > 0:
            text = result[0].get("generated_text", "")

        elif isinstance(result, dict):
            # HF often returns loading / rate limit errors
            if "error" in result:
                raise Exception(f"HuggingFace Error: {result['error']}")
            else:
                raise Exception(f"Unexpected HF response: {result}")

        else:
            raise Exception("Invalid HuggingFace response format")

        cleaned = extract_json(text)

        print("✅ HuggingFace success")
        return json.loads(cleaned)

    except Exception as e:
        raise Exception(f"All LLM providers failed → {repr(e)}")
