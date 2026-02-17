import os
import json
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Gemini client
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

HF_API_KEY = os.getenv("HF_API_KEY")

HF_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"


def extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


async def call_llm(system_prompt: str, payload: dict):

    user_prompt = f"""
Input Data:
{json.dumps(payload)}

Return ONLY valid JSON.
No explanations.
No markdown.
"""

    full_prompt = system_prompt + "\n" + user_prompt

    # ========= TRY GEMINI FIRST =========
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[{
                "role": "user",
                "parts": [{"text": full_prompt}]
            }],
        )

        text = response.text
        cleaned = extract_json(text)
        return json.loads(cleaned)

    except Exception as e:
        print("⚠ Gemini failed → switching to HuggingFace fallback")
        print(str(e))

    # ========= FALLBACK TO HUGGINGFACE =========
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_KEY}"
        }

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 1500,
                "temperature": 0.3
            }
        }

        r = requests.post(HF_URL, headers=headers, json=payload)

        result = r.json()

        text = result[0]["generated_text"]
        cleaned = extract_json(text)

        return json.loads(cleaned)

    except Exception as e:
        raise Exception(f"All LLM providers failed: {str(e)}")
