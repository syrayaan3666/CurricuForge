from services.llm_client import call_llm


def apply_adaptive_pacing(curriculum: dict, learner_profile: dict):

    if not learner_profile:
        return curriculum

    pace = learner_profile.get("learning_pace", "balanced").lower()
    semesters = curriculum.get("semesters", [])

    if not semesters:
        return curriculum

    if pace == "fast":
        semesters.sort(key=lambda x: -x.get("semester", 0))

    elif pace == "slow":
        semesters.sort(key=lambda x: x.get("semester", 0))

    curriculum["semesters"] = semesters
    return curriculum


async def formatter_agent(curriculum: dict, validation: dict):

    system_prompt = """
    You are the Formatter Agent.

    Merge curriculum + validation output.
    Produce clean structured JSON.

    If learner_profile exists, keep it in final output.
    """

    payload = {
        "curriculum": curriculum,
        "validation": validation
    }

    formatted = await call_llm(system_prompt, payload)

    # ===== 🧠 Adaptive Pacing Hook =====
    learner_profile = formatted.get("learner_profile")

    formatted = apply_adaptive_pacing(
        formatted,
        learner_profile
    )

    return formatted
