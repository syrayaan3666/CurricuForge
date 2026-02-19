from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from orchestrator.pipeline import run_agent_pipeline
from agents import refine_agent
from agents.validator_agent import validator_agent
from agents.formatter_agent import formatter_agent
from services.pdf_generator import generate_pdf_from_curriculum
from fastapi import HTTPException
from io import BytesIO

print("🔥 USING NEW PDF GENERATOR FILE")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate_curriculum(data: dict):
    result = await run_agent_pipeline(data)
    
    print("\n" + "="*60)
    print("GENERATE ENDPOINT RESPONSE")
    print("="*60)
    print(f"Response keys: {list(result.keys())}")
    if "semesters" in result and result["semesters"]:
        first_sem = result["semesters"][0]
        if "courses" in first_sem and first_sem["courses"]:
            first_course = first_sem["courses"][0]
            print(f"First course: {first_course}")
    print("="*60 + "\n")
    
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
        print("\n" + "="*60)
        print("EXPORT PDF REQUEST")
        print("="*60)
        print(f"Curriculum keys: {list(curriculum.keys())}")
        print(f"Has semesters: {'semesters' in curriculum}")
        
        # 1) Validate the curriculum
        validation = await validator_agent(curriculum)
        print(f"✓ Validation passed")
        
        # 2) Format the curriculum with validation metadata
        formatted_curriculum = await formatter_agent(curriculum, validation)
        print(f"✓ Formatting complete")
        print(f"Formatted curriculum keys: {list(formatted_curriculum.keys())}")
        
        # 3) Generate PDF from formatted curriculum
        print(f"Generating PDF...")
        pdf_bytes = generate_pdf_from_curriculum(formatted_curriculum)
        print(f"✓ PDF generated successfully ({len(pdf_bytes)} bytes)")
        print("="*60 + "\n")
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=curriculum.pdf"}
        )
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
