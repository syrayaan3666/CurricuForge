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


async def inject_video_links(curriculum: dict):
    """
    Traverse curriculum and inject video links for all topics.
    Supports both semester and personal planner modes.
    """
    from services.video_service import get_video_link
    
    # ===== SEMESTER MODE =====
    if curriculum.get("semesters"):
        for semester in curriculum["semesters"]:
            for course in semester.get("courses", []):
                topics = course.get("topics", [])
                # Handle both list of strings and list of dicts
                processed_topics = []
                for topic in topics:
                    if isinstance(topic, dict):
                        # Already structured, add video_url if missing
                        if "video_url" not in topic or not topic["video_url"]:
                            topic_name = topic.get("name", "")
                            topic["video_url"] = await get_video_link(topic_name)
                        processed_topics.append(topic)
                    else:
                        # String topic, convert to dict
                        video_url = await get_video_link(str(topic))
                        processed_topics.append({
                            "name": str(topic),
                            "video_url": video_url
                        })
                course["topics"] = processed_topics
    
    # ===== PERSONAL PLANNER MODE =====
    if curriculum.get("roadmap"):
        for phase in curriculum["roadmap"]:
            for milestone in phase.get("milestones", []):
                topics = milestone.get("topics", [])
                processed_topics = []
                for topic in topics:
                    if isinstance(topic, dict):
                        # Already structured, add video_url if missing
                        if "video_url" not in topic or not topic["video_url"]:
                            topic_name = topic.get("name", "")
                            topic["video_url"] = await get_video_link(topic_name)
                        processed_topics.append(topic)
                    else:
                        # String topic, convert to dict
                        video_url = await get_video_link(str(topic))
                        processed_topics.append({
                            "name": str(topic),
                            "video_url": video_url
                        })
                milestone["topics"] = processed_topics
    
    return curriculum


async def formatter_agent(curriculum: dict, validation: dict):
    """
    Format and validate curriculum output.
    Ensures correct structure for frontend rendering.
    Injects video links for all topics.
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
    
    # ===== 🎥 Inject Video Links =====
    formatted = await inject_video_links(formatted)
    
    return formatted
