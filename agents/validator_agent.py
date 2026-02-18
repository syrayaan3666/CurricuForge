from services.llm_client import call_llm



VALIDATOR_SYSTEM_PROMPT = """
You are an academic curriculum validator.

Your task is to review a generated curriculum and evaluate quality.

The curriculum can be in ONE of two formats:

1. SEMESTER FORMAT (traditional academic):
   - Contains "semesters" array
   - Each semester has courses with:
     * title
     * difficulty (Beginner / Intermediate / Advanced)
     * skills (2-4 abilities)
     * topics (learning content)
     * outcome_project (practical deliverable)
   - Evaluate: logical progression, difficulty arc (Beginner → Advanced), skill coherence, practical relevance
   - Capstone detection: Final semester may have industry project or internship experience

2. ROADMAP FORMAT (personal learning paths):
   - Contains "roadmap" array
   - Each phase contains milestones with skills and topics
   - Evaluate: phase progression, skill practicality, topic coverage, realistic timeline
   - Additional accepted fields:
     * `estimated_total_hours` (number) on milestones
     * per-topic objects with `name`, `estimated_hours`, `weeks`
     * optional `certification` object inside milestones (may be empty)
     * optional metadata keys (resources, prerequisites)

For BOTH formats, assess:
- Logical progression (foundations before advanced)
- Difficulty balance and arc
- Redundancy or gaps in topics/skills
- Industry/career relevance
- Realistic time allocation
- (Semester only) Outcome projects are practical and achievable
- (Semester only) Capstone is industry-relevant or integrative

IMPORTANT RULES:
- Do NOT regenerate the curriculum.
- Only analyze and return evaluation metadata.
- Output STRICT JSON.

Return format:

{
  "status": "approved|needs_revision|rejected",
  "issues": [],
  "suggestions": [],
  "metadata_warnings": []
}

Examples:
- issues: ["Semester 1 courses jump from Beginner to Advanced difficulty"]
- suggestions: ["Add intermediate difficulty course in Semester 2 before advanced topics"]
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
