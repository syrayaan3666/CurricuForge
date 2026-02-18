from services.llm_client import call_llm



PLANNER_SYSTEM_PROMPT = """
You are a curriculum planning agent.

Your job is to analyze educational requirements and produce
a structured curriculum strategy.

IMPORTANT RULES:
- Do NOT generate courses or topics.
- Only create a curriculum plan.
- Output STRICT JSON.
-You MUST adapt curriculum planning using learner_profile fields:
persona_type, pacing_strategy, research_intensity, industry_orientation.


Return format:

{
  "program_title": "",
  "difficulty_progression": "",
  "courses_per_semester": 0,
  "focus_tags": [],
  "include_capstone": true,
  "semesters": 0
}

"""


async def planner_agent(user_input: dict):

    result = await call_llm(
        PLANNER_SYSTEM_PROMPT,
        user_input
    )

    return result
