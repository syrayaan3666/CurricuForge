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
    """
    Format and validate curriculum output.
    Ensures correct structure for frontend rendering.
    """
    
    # ===== MERGE CURRICULUM WITH VALIDATION =====
    formatted = curriculum.copy()
    
    # Add validation info if present
    if validation:
        formatted["validation_status"] = validation.get("status", "unknown")
        # Validator returns `issues` and `suggestions` — preserve both
        formatted["validation_issues"] = validation.get("issues", [])
        formatted["validation_suggestions"] = validation.get("suggestions", [])
        # optional structural warnings
        if "metadata_warnings" in validation:
            formatted["validation_metadata_warnings"] = validation.get("metadata_warnings", [])
    
    # ===== 🧠 Adaptive Pacing Hook =====
    learner_profile = formatted.get("learner_profile")
    
    formatted = apply_adaptive_pacing(
        formatted,
        learner_profile
    )
    
    return formatted
