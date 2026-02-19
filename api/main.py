import sys
import os

# Ensure project root is on sys.path when running from the `api/` folder
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from orchestrator.pipeline import run_agent_pipeline
from agents import refine_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent
from services.pdf_generator import generate_pdf_from_curriculum
from services.logger import get_logger
from fastapi import HTTPException
from io import BytesIO
from main import app

app = FastAPI()

logger = get_logger("api")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate_curriculum(data: dict):
    result = await run_agent_pipeline(data)
    
    logger.info("GENERATE ENDPOINT RESPONSE")
    logger.debug("Response keys: %s", list(result.keys()))
    if "semesters" in result and result["semesters"]:
        first_sem = result["semesters"][0]
        if "courses" in first_sem and first_sem["courses"]:
            first_course = first_sem["courses"][0]
            logger.debug("First course: %s", first_course)
    
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



@app.post("/export-pdf")
async def export_pdf(data: dict):
    """
    Generate and return a PDF from curriculum data.
    Process through validator and formatter agents to ensure proper formatting.
    """
    curriculum = data.get("curriculum")
    
    if not curriculum:
        raise HTTPException(status_code=400, detail="'curriculum' field is required")
    
    try:
        logger.info("EXPORT PDF REQUEST")
        logger.debug("Curriculum keys: %s", list(curriculum.keys()))
        logger.debug("Has semesters: %s", 'semesters' in curriculum)

        # 1) Validate the curriculum
        validation = await validator_agent(curriculum)
        logger.debug("Validation result: %s", validation)

        # 2) Format the curriculum with validation metadata
        formatted_curriculum = await formatter_agent(curriculum, validation)
        logger.debug("Formatting complete. Keys: %s", list(formatted_curriculum.keys()))

        # 3) Generate PDF from formatted curriculum
        logger.info("Generating PDF")
        pdf_bytes = generate_pdf_from_curriculum(formatted_curriculum)
        logger.info("PDF generated successfully (%d bytes)", len(pdf_bytes))

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=curriculum.pdf"}
        )
    except Exception as e:
        logger.exception("PDF generation failed: %s", str(e))
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
