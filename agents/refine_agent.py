import json
from typing import Dict, Any

from services.llm_client import call_llm


PERSONAL_REFINE_PROMPT = """
You are an AI curriculum refinement assistant.

You receive two inputs:
1) An existing curriculum JSON (the `current_plan`).
2) A user refinement instruction (plain English).

Your job:
- MODIFY the provided `current_plan` ONLY according to the user's instruction.
- Preserve the original JSON structure and top-level keys exactly (do NOT rename or wrap the object).
- Do NOT add explanations, commentary, or markdown — return ONLY the refined plan JSON object.

Important: The system that consumes your output expects one of two structured formats. When refining, keep the same top-level format the input used.

SEMESTER EXAMPLE (if input used semesters):
{
    "program_title": "",
    "summary": "",
    "semesters": [
        {
            "semester": 1,
            "courses": [
                {"title": "", "topics": [""]}
            ]
        }
    ]
}

ROADMAP EXAMPLE (if input used roadmap):
{
    "program_title": "",
    "summary": "",
    "total_weeks": 24,
    "weekly_hours": 15,
    "roadmap": [
        {
            "phase": "Phase 1",
            "duration_weeks": 6,
            "weeks": "Week 1-6",
            "milestones": [
                {
                    "title": "",
                    "timeline_weeks": "Week 1-3",
                    "estimated_total_hours": 18,
                    "skills": [""],
                    "topics": [{"name": "", "estimated_hours": 6, "weeks": "Week 1-2"}]
                }
            ]
        }
    ]
}

Constraints:
- Return ONLY the refined plan object with the same top-level keys as `current_plan`.
- If the user requests duration changes (compress/expand), proportionally adjust `duration_weeks`, `timeline_weeks`, `weeks`, and per-topic `estimated_hours`.
- Ensure total weeks and phase durations remain consistent (sum of phase `duration_weeks` must equal `total_weeks` when present).

Output: Return the full refined JSON object (no wrappers, no text).
"""


async def refine_agent(current_plan: Dict[str, Any], instruction: str) -> Dict[str, Any]:
    """Call the LLM to refine an existing curriculum plan.

    Args:
        current_plan: The curriculum JSON previously generated.
        instruction: Natural language instruction describing the refinement.

    Returns:
        The refined curriculum JSON (parsed).
    """

    # Align with other agents: merge instruction into the plan dict so
    # the LLM receives a flat, predictable payload (same style as generator_agent)
    payload = {}
    if isinstance(current_plan, dict):
        payload.update(current_plan)
    else:
        # fallback wrapper if current_plan is not a dict
        payload["current_plan"] = current_plan

    # place the user's refinement instruction under a clear key
    payload["refinement_instruction"] = instruction

    # call_llm will raise if providers fail; let caller handle exceptions
    result = await call_llm(PERSONAL_REFINE_PROMPT, payload)

    # Ensure result is a dict
    if not isinstance(result, dict):
        raise Exception("Refine agent returned invalid format")

    return result
