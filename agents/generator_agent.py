from services.llm_client import call_llm



GENERATOR_SYSTEM_PROMPT = """
You are a curriculum generation agent.

Use the provided curriculum plan to generate a structured
semester-wise academic program.

IMPORTANT RULES:
- Follow the difficulty progression from the plan.
- Generate courses, topics, and learning outcomes.
- Output STRICT JSON only.
- Do not include explanations.

Return format:

{
  "program_title": "",
  "semesters": [
    {
      "semester": 1,
      "courses": [
        {
          "title": "",
          "topics": [],
          "learning_outcomes": []
        }
      ]
    }
  ]
}
"""


async def generator_agent(plan: dict):

    result = await call_llm(
        GENERATOR_SYSTEM_PROMPT,
        plan
    )

    return result
