from agents.personal_planner_agent import personal_planner_agent
from agents.planner_agent import planner_agent
from agents.generator_agent import generator_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent



async def run_agent_pipeline(data: dict):

    planner_type = data.get("plannerType", "semester")

    # ================= PERSONAL PLANNER =================
    if planner_type == "personal":

        learner_profile = await personal_planner_agent(data)

        curriculum = await generator_agent({
            "learner_profile": learner_profile
        })

    # ================= SEMESTER PLANNER =================
    else:

        plan = await planner_agent(data)

        curriculum = await generator_agent(plan)

    # ================= VALIDATION =================
    validation = await validator_agent(curriculum)

    # ✅ CORRECT CALL — TWO ARGUMENTS
    final_output = await formatter_agent(curriculum, validation)

    return final_output