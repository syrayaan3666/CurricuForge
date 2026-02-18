from services.llm_client import call_llm

PERSONAL_PLANNER_PROMPT = """
You are an AI Learner Persona Architect.

Analyze the learner inputs and create a structured learner_profile.

INPUT FIELDS:
- study_domain: AI, Data Science, Cybersecurity, Software Engineering
- career_path: Job Ready, Research, Startup, Freelance
- experience: Beginner, Intermediate, Advanced
- pace: Fast, Moderate, Slow
- weekly_hours: 10, 15, 20, 25
- duration: 3 Months, 6 Months, 9 Months, 12 Months

Map these inputs to create a learner_profile with:
- persona_type: Based on career_path and study_domain
- content_bias: Based on study_domain (practical vs theoretical)
- pacing_strategy: Based on pace and weekly_hours
- innovation_index: Based on career_path
- learning_style: Based on pace
- risk_tolerance: Based on career_path
- assessment_preference: Based on career_path
- collaboration_level: Based on career_path
- career_alignment: Based on career_path and study_domain
- difficulty_preference: Based on experience
- research_intensity: Based on career_path
- industry_orientation: Based on study_domain

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
