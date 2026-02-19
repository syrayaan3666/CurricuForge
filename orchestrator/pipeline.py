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

    # DEBUG: Log what's being returned to frontend
    print("\n" + "="*60)
    print("PIPELINE FINAL OUTPUT DEBUG")
    print("="*60)
    if "semesters" in final_output:
        print(f"Has semesters: {len(final_output['semesters'])}")
        if final_output["semesters"]:
            first_sem = final_output["semesters"][0]
            print(f"First semester has {len(first_sem.get('courses', []))} courses")
            if "courses" in first_sem and first_sem["courses"]:
                first_course = first_sem["courses"][0]
                print(f"First course keys: {list(first_course.keys())}")
                print(f"First course has skills: {'skills' in first_course}")
                print(f"First course has topics: {'topics' in first_course}")
                print(f"First course has outcome_project: {'outcome_project' in first_course}")
                print(f"First course sample: {first_course}")
    print("="*60 + "\n")

    return final_output