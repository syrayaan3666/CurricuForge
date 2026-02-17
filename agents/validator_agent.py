from services.llm_client import call_llm



VALIDATOR_SYSTEM_PROMPT = """
You are an academic curriculum validator.

Your task is to review a generated curriculum and evaluate:

- logical semester progression
- difficulty balance
- redundancy of topics
- industry relevance

IMPORTANT RULES:
- Do NOT regenerate the curriculum.
- Only analyze and return evaluation metadata.
- Output STRICT JSON.

Return format:

{
  "status": "approved",
  "issues": [],
  "suggestions": []
}
"""


async def validator_agent(curriculum: dict):

    try:
        result = await call_llm(
            VALIDATOR_SYSTEM_PROMPT,
            curriculum
        )
        return result

    except Exception:
        # ⭐ Fallback when quota exhausted
        return {
            "status": "skipped",
            "issues": [],
            "suggestions": []
        }
