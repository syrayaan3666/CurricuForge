from agents.personal_planner_agent import personal_planner_agent
from agents.planner_agent import planner_agent
from agents.generator_agent import generator_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent



async def run_agent_pipeline(data: dict):

    planner_type = data.get("planner_type", "semester")

    # ================= PERSONAL PLANNER =================
    if planner_type == "personal":

        learner_profile = await personal_planner_agent(data)

        # Pass original data fields to generator along with planner_type
        generator_input = {
            "planner_type": "personal",
            "study_domain": data.get("study_domain"),
            "career_path": data.get("career_path"),
            "experience": data.get("experience"),
            "pace": data.get("pace"),
            "weekly_hours": data.get("weekly_hours"),
            "duration": data.get("duration"),
            "learner_profile": learner_profile
        }
        
        curriculum = await generator_agent(generator_input)

    # ================= SEMESTER PLANNER =================
    else:

        plan = await planner_agent(data)
        plan["planner_type"] = "semester"

        curriculum = await generator_agent(plan)

    # ================= VALIDATION =================
    validation = await validator_agent(curriculum)

    # ✅ CORRECT CALL — TWO ARGUMENTS
    final_output = await formatter_agent(curriculum, validation)

    return final_output