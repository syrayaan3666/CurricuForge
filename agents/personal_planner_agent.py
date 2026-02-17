from services.llm_client import call_llm

PERSONAL_PLANNER_PROMPT = """
You are an AI Learner Persona Architect.

Analyze the learner inputs and create a structured learner_profile.

Return STRICT JSON:

{
  "persona_type": "",
  "content_bias": "",
  "pacing_strategy": "",
  "innovation_index": "",
  "learning_style": "",
  "risk_tolerance": "",
  "assessment_preference": "",
  "collaboration_level": "",
  "career_alignment": "",
  "difficulty_preference": "",
  "research_intensity": "",
  "industry_orientation": ""
}
"""

async def personal_planner_agent(data: dict):
    result = await call_llm(PERSONAL_PLANNER_PROMPT, data)
    return result
