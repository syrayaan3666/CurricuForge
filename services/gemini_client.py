import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


async def call_gemini(system_prompt: str, payload: dict):

    user_prompt = f"""
    Input Data:
    {json.dumps(payload)}

    Return ONLY valid JSON.
    No explanations.
    No markdown.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt + "\n" + user_prompt}],
                }
            ],
        )

        text = response.text
        cleaned = extract_json(text)

        data = json.loads(cleaned)
        return data

    except Exception as e:
        raise Exception(f"Gemini call failed: {str(e)}")
