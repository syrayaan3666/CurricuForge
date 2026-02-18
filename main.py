from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from orchestrator.pipeline import run_agent_pipeline
from agents import refine_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent
from fastapi import HTTPException

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate_curriculum(data: dict):
    result = await run_agent_pipeline(data)
    return result


@app.post("/refine-plan")
async def refine_plan(data: dict):
    instruction = data.get("instruction")
    current = data.get("current_plan")

    if not instruction or not current:
        raise HTTPException(status_code=400, detail="Both 'instruction' and 'current_plan' are required")

    try:
        # 1) Obtain refined curriculum from the refine agent
        refined = await refine_agent.refine_agent(current, instruction)

        # 2) Validate the refined curriculum (same flow as generation pipeline)
        validation = await validator_agent(refined)

        # 3) Format the refined curriculum with validation metadata
        final_output = await formatter_agent(refined, validation)

        return final_output

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
