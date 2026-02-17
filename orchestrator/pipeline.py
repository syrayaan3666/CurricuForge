from agents.personal_planner_agent import personal_planner_agent
from agents.planner_agent import planner_agent
from agents.generator_agent import generator_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent


async def run_agent_pipeline(data: dict):

    pipeline_state = {
        "user_inputs": data
    }

    # STEP 1 — PERSONAL PROFILE
    learner_profile = await personal_planner_agent(data)
    pipeline_state["learner_profile"] = learner_profile

    # STEP 2 — SEMESTER PLANNER
    plan_output = await planner_agent({
        **data,
        "learner_profile": learner_profile
    })
    pipeline_state["plan_output"] = plan_output

    # STEP 3 — GENERATOR
    curriculum = await generator_agent(plan_output)
    pipeline_state["curriculum"] = curriculum

    # STEP 4 — VALIDATOR
    validation = await validator_agent(curriculum)
    pipeline_state["validation"] = validation

    # STEP 5 — FORMATTER
    final_output = await formatter_agent({
        **pipeline_state
    })

    return final_output
