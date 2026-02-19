📖 CurricuForge AI — Generative Curriculum Design System

CurricuForge AI is a multi-agent, generative platform that turns simple learner or program inputs into structured, actionable curricula. It demonstrates robust LLM orchestration, resilient provider fallbacks, and a compact front-end for interactive refinement.

---

## 🧠 Overview

CurricuForge converts user inputs (semester program or personal learning goals) into strict, structured JSON curriculum artifacts. Small, focused agents plan, generate, validate, and format the output. A post-generation refinement loop allows users to iteratively improve plans using plain English instructions.

---

## ✨ Key Features

- Multi-agent pipeline: Planner → Generator → Validator → Formatter
- Two planner modes: Semester (university-style) and Personal (time-based roadmap)
- Post-generation refinement with `agents/refine_agent.py` and `/refine-plan` endpoint
- Robust LLM routing: Gemini primary, Groq fallback with circuit-breaker when Gemini quota is exhausted
- Resilient JSON parsing: brace-aware extractor, truncation detection, and one-time repair retry
- Prompt tuning and larger token budget for Groq to avoid truncation of long curricula
- Frontend: internal-scroll generation container, in-page refinement UI, JSON & PDF downloads (jsPDF)
- FastAPI backend for quick local demos

---

## Architecture (high level)

User Input → Planner Agent (structure) → Generator Agent (content) → Validator Agent (quality) → Formatter Agent (UI JSON)

Refinement: the refine agent accepts a current plan + an instruction, then returns a refined plan which is validated and formatted before being sent back to the frontend.

---

## Important Implementation Details

- `services/llm_client.py`
  - Central LLM router. Tries Gemini first (via Google GenAI). On quota/exhaustion it sets a circuit-breaker and falls back to Groq (OpenAI-compatible REST).
  - Improved JSON extraction: handles markdown fences, tracks strings/escapes, performs brace/bracket balancing, and can auto-close truncated responses.
  - Adds `detect_truncation()` and a one-time repair retry that asks the LLM to correct malformed JSON.
  - Groq calls use an increased `max_tokens` value to reduce truncation risk.

- `agents/generator_agent.py`
  - Dual prompts: `SEMESTER_GENERATOR_PROMPT` and `PERSONAL_GENERATOR_PROMPT` (time-based roadmap).
  - Semester prompt now requests `difficulty`, `skills`, `topics`, and `outcome_project` per course and honors `include_capstone`.
  - Personal prompt produces `roadmap` → phases → milestones → topics (with estimated_hours where appropriate).
  - Adds conciseness guidance to keep outputs within token limits and preserves `learner_profile` in the generator output.

- `agents/refine_agent.py` (new)
  - Accepts `{ instruction, current_plan }` and returns a modified curriculum JSON. The endpoint `/refine-plan` wires this into validation + formatting so the UI receives a production-ready plan.

- `agents/validator_agent.py` & `agents/formatter_agent.py`
  - Validator recognizes both `semesters` and `roadmap` formats and verifies new semester fields and capstone logic.
  - Formatter merges validation metadata (`issues`, `suggestions`, `metadata_warnings`) into the final object and applies optional adaptive pacing.

- Frontend (`templates/index.html`, `static/app.js`, `static/style.css`)
  - New in-page refinement UI (bottom of right panel) that posts to `/refine-plan`.
  - Generation container scrolls internally so the refinement box remains visible.
  - Download bar supports JSON & PDF export; PDF generation uses jsPDF (CDN included in template).
  - Layout and styling tweaks: difficulty badges, capstone indicator, compact form spacing.

---

## API Endpoints

- `POST /generate` — run the pipeline and return a formatted curriculum JSON.
  - Example semester payload:

```json
{
  "planner_type": "semester",
  "skill": "Artificial Intelligence",
  "level": "Masters",
  "semesters": 6,
  "weekly_hours": 15,
  "focus": "Industry",
  "include_capstone": true
}
```

  - Example personal payload:

```json
{
  "planner_type": "personal",
  "study_domain": "AI Research",
  "career_path": "Researcher",
  "experience": "intermediate",
  "pace": "moderate",
  "weekly_hours": 20,
  "duration": "9 Months"
}
```

- `POST /refine-plan` — accepts `{ instruction: string, current_plan: object }` and returns the refined, validated, formatted curriculum JSON.

---

## Setup & Run

1. Create and activate a Python virtualenv.
2. Install dependencies listed in `requirements.txt`.
3. Provide API keys via environment variables or a `.env` file:

```
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```

4. Start the server:

```bash
uvicorn main:app --reload
```

5. Open `http://127.0.0.1:8000` and use the UI.

---

## Tips & Troubleshooting

- If you see `ModuleNotFoundError: dotenv` install `python-dotenv`.
- Gemini quota errors (429 / RESOURCE_EXHAUSTED) will automatically switch the app to Groq and set a circuit-breaker so subsequent requests use Groq-only.
- If Groq output looks truncated: reduce prompt verbosity in `agents/generator_agent.py` and/or increase `max_tokens` in `services/llm_client.py`.
- To inspect full LLM responses, adjust debug `print()` preview lengths in `services/llm_client.py` (careful with very large logs).

---

## Notes

- This project is a demo/prototype intended for experimentation and demonstration. Consider adding stricter JSON schema validation (e.g., `jsonschema`) before using generated curricula in production systems.

---

CurricuForge AI — resilient LLM orchestration for practical curriculum design.
