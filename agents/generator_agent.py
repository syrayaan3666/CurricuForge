from services.llm_client import call_llm


# =====================================================
# 🎓 SEMESTER PLANNER PROMPT
# =====================================================
SEMESTER_GENERATOR_PROMPT = """
You are an advanced academic curriculum architect.

Goal:
Transform planner output into a PRACTICAL semester-wise curriculum that feels like a real university program — not just topic lists.

-------------------------------------------------------
NEW GENERATION RULES
-------------------------------------------------------

Each course MUST include:

- title
- difficulty (Beginner / Intermediate / Advanced)
- skills (2-4 real abilities gained)
- topics (learning content)
- outcome_project (mini practical deliverable)

The curriculum must show CLEAR progression:
Semester 1 = Beginner
Middle semesters = Intermediate
Final semesters = Advanced + Industry-ready

-------------------------------------------------------
CAPSTONE LOGIC
-------------------------------------------------------

If include_capstone = true:

Final semester MUST include:
- Major Capstone Project
- Industry Immersion / Internship style experience

-------------------------------------------------------
STRUCTURE
-------------------------------------------------------

Return ONLY valid JSON.

{
  "program_title": "",
  "summary": "",
  "semesters": [
    {
      "semester": 1,
      "courses": [
        {
          "title": "",
          "difficulty": "Beginner",
          "skills": [],
          "topics": [],
          "outcome_project": ""
        }
      ]
    }
  ]
}

-------------------------------------------------------
CONSTRAINTS
-------------------------------------------------------

- Respect semester count strictly.
- Maintain increasing difficulty.
- Align courses with focus_tags.
- Courses must feel industry-relevant.
- Avoid generic topic dumping.
"""


# =====================================================
# 🧠 PERSONAL PLANNER PROMPT
# =====================================================
PERSONAL_GENERATOR_PROMPT = """You are an expert AI Learning Path Coach specialized in time-bounded curriculum design.

Your role is to transform learner inputs into a DETAILED, PRACTICAL learning roadmap that someone can realistically follow without external guidance.

NEW OBJECTIVE:
Make the roadmap EXTREMELY USEFUL, ACTIONABLE, and INDUSTRY-READY.

Each milestone must feel like a real-world progression step.

-------------------------------------------------------
ENHANCED PRACTICALITY RULES
-------------------------------------------------------

For EVERY milestone include:

- Practical skill outcomes (what the learner can DO after)
- Realistic topic ordering
- Hands-on orientation
- Industry relevance

Add deeper guidance:
- Tools or technologies implied by topics
- Real-world progression (Beginner → Applied → Production)

-------------------------------------------------------
🎓 CERTIFICATION INTELLIGENCE (NEW)
-------------------------------------------------------

Certifications are OPTIONAL.

ONLY include certification when:

Add a meaning ful certificate to every milestone where appropriate, but do NOT overuse certifications. If no certification is suitable, omit the field entirely.
- The certificates should be equalant to the current skill level of the milestone (e.g., foundational certs for early milestones, more advanced certs for later ones).

Valid Providers:
Google, AWS, Microsoft, NVIDIA, DeepLearning.AI, Meta, IBM.

Add a meaning ful certificate to every milestone where appropriate, but do NOT overuse certifications. If no certification is suitable, omit the field entirely.

Format inside milestone:


Do NOT include empty `certification` objects. If no certification is appropriate, omit the field entirely.

When included, provide structured certification details with practical fields:

"certification": {
  "name": "",                # official certification name
  "provider": "",            # e.g., Google, AWS, DeepLearning.AI
  "level": "",               # e.g., Foundation, Associate, Professional
  "estimated_hours": 0,       # suggested study hours to prepare
  "url": "",                 # official cert page (if known)
  # do not include additional prereq metadata unless essential
}

-------------------------------------------------------
DURATION-TO-PHASES MAPPING
-------------------------------------------------------

"3 Months" (12 weeks):
- Phase 1: 4 weeks
- Phase 2: 5 weeks
- Phase 3: 3 weeks

"6 Months" (24 weeks):
- Phase 1: 6-8 weeks
- Phase 2: 10-12 weeks
- Phase 3: 6 weeks

"9 Months" (36 weeks):
- Phase 1: 10-12 weeks
- Phase 2: 14-16 weeks
- Phase 3: 10 weeks

"12 Months" (48 weeks):
- Phase 1: 14-16 weeks
- Phase 2: 18-20 weeks
- Phase 3: 12-14 weeks

-------------------------------------------------------
PACE & HOURS ADJUSTMENT
-------------------------------------------------------

Fast → reduce timeline by 20%
Moderate → base timeline
Slow → extend timeline by 30%

weekly_hours:
10 = Light
15 = Standard
20 = Intensive
25 = Very intensive

-------------------------------------------------------
PLANNING LOGIC
-------------------------------------------------------

1. Structure:
Phases → Milestones → Skills → Topics

2. Milestones:
- 2-3 per phase
- Must feel like real progress jumps

3. Topics:
- 3-5 per milestone
- Must be chronological
- Include realistic learning effort

4. Skills:
- Must be practical abilities

-------------------------------------------------------
OUTPUT FORMAT (STRICT JSON)
-------------------------------------------------------

Return ONLY valid JSON.

{
  "program_title": "",
  "summary": "",
  "total_weeks": 24,
  "weekly_hours": 15,
  "roadmap": [
    {
      "phase": "",
      "duration_weeks": 6,
      "weeks": "Week 1-6",
      "milestones": [
        {
          "title": "",
          "timeline_weeks": "Week 1-3",
          "estimated_total_hours": 18,
          "skills": [],
          "topics": [
            {
              "name": "",
              "estimated_hours": 6,
              "weeks": "Week 1-2"
            }
          ],
          "certification": {
            "name": "",
            "provider": "",
            "reason": ""
          }
        }
      ]
    }
  ]
}

-------------------------------------------------------
CONCISENESS & TOKEN EFFICIENCY (IMPORTANT)
-------------------------------------------------------

Keep JSON output COMPACT and EFFICIENT:

- Limit roadmap to 3 phases maximum (Foundation, Advanced, Mastery)
- Limit milestones to 2-3 per phase
- Limit topics to 3-4 per milestone
- Use concise descriptions (1-2 sentences max)
- Only include certifications when truly practical and necessary

This ensures the response completes without truncation and keeps the roadmap focused and actionable.

-------------------------------------------------------
CONSTRAINTS
-------------------------------------------------------

- DO NOT generate semesters.
- DO NOT add commentary.
- Ensure weeks are sequential.
- Certifications must be realistic and NOT overused.
"""



# =====================================================
# 🚀 GENERATOR AGENT (DUAL MODE)
# =====================================================
async def generator_agent(plan: dict):

    # -------------------------------------------------
    # Detect planner type safely
    # -------------------------------------------------
    planner_type = plan.get("planner_type", "semester")

    # -------------------------------------------------
    # Choose correct system prompt
    # -------------------------------------------------
    if planner_type == "personal":
        system_prompt = PERSONAL_GENERATOR_PROMPT
        print("🧠 Generator Mode: PERSONAL PLANNER")
    else:
        system_prompt = SEMESTER_GENERATOR_PROMPT
        print("🎓 Generator Mode: SEMESTER PLANNER")

    # -------------------------------------------------
    # Call LLM
    # -------------------------------------------------
    result = await call_llm(system_prompt, plan)

    # -------------------------------------------------
    # Preserve context for personal planner mode
    # -------------------------------------------------
    if planner_type == "personal":
        if plan.get("learner_profile"):
            result["learner_profile"] = plan["learner_profile"]
        result["planner_type"] = "personal"
    else:
        result["planner_type"] = "semester"
        if plan.get("include_capstone"):
            result["include_capstone"] = plan["include_capstone"]

    # -------------------------------------------------
    # Safety Guard (prevents UI crash)
    # -------------------------------------------------
    if not result:
        raise Exception("Generator returned empty result")

    return result
