📖 CurricuForge AI — Generative Curriculum Design System

CurricuForge AI is a **semi-agentic Generative AI platform** that designs structured academic curricula using multi-agent orchestration.
Built for hackathon environments, the system demonstrates how AI can automate curriculum planning, generate industry-aligned courses, and support adaptive learning design.

---

## 🧠 Overview

CurricuForge transforms educational requirements into structured semester plans through an AI-driven workflow.

The platform simulates an **Agentic Curriculum Designer** using multiple AI agents that collaborate to:

* Analyze requirements
* Plan curriculum structure
* Generate course content
* Validate academic alignment
* Format final output for delivery

The goal is to show how AI can augment educators with scalable curriculum intelligence.

---

## ✨ Key Features

* Multi-Agent Architecture (Planner → Generator → Validator → Formatter)
* Semi-Agentic pipeline with upgrade path to feedback loops
* Curriculum generation in structured JSON format
* Hackathon-ready futuristic UI
* Persona Planner + Semester Planner support
* Fallback AI provider (Gemini → HuggingFace)
* Modular backend using FastAPI

---

## 🏗️ Architecture

### Agent Pipeline Flow

```
User Input
    ↓
Profile Agent (Learner Persona Builder)
    ↓
Planner Agent (Curriculum Structure)
    ↓
Generator Agent (Courses + Topics + Outcomes)
    ↓
Validator Agent (Quality + Alignment Check)
    ↓
Formatter Agent (Final UI JSON)
```

This sequential orchestration makes it easy to extend into a fully agentic feedback loop later.

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Async Orchestrator
* Multi-Agent Design Pattern

### AI Services

* Gemini API
* HuggingFace (fallback inference)

### Frontend

* HTML
* CSS (Glassmorphism AI Dashboard)
* Vanilla JavaScript

---

## 📁 Project Structure

```
curricuforge/
│
├── agents/          # AI agent logic (planner, generator, validator, formatter, profile)
├── orchestrator/    # Agent pipeline workflow
├── services/        # AI client integrations (Gemini / HuggingFace)
├── models/          # Data schemas
├── templates/       # HTML UI
├── static/          # CSS + JS
├── main.py          # FastAPI entry point
```

---

API Endpoint:

### POST `/generate`

Input Payload:

```json
{
  "mode": "semester",
  "skill": "Artificial Intelligence",
  "level": "Masters",
  "semesters": 4,
  "weekly_hours": 20,
  "industry_focus": "Research"
}
```

Response:

Structured curriculum JSON containing semesters, courses, topics, and learning outcomes.

---

UI Integration Contract:

The frontend communicates with the backend using fixed element IDs:

```
mode
skill
level
semesters
hours
focus
profile
planner
generator
validator
result
```

These IDs must remain unchanged because `app.js` depends on them.

---

AI Provider Strategy:

CurricuForge uses a resilient AI architecture:

1. Try Gemini API
2. If quota/service fails → fallback to HuggingFace
3. Return structured JSON regardless of provider

This ensures stable demos during hackathons.

---

Future Improvements:

* Full agentic feedback loop
* Real learner analytics ingestion
* Adaptive learning paths
* Admin dashboard
* LMS integration

---

Author Notes:

This project was built as a hackathon prototype to demonstrate how AI can:

* Automate curriculum planning
* Personalize education at scale
* Support educators with intelligent tooling

The current implementation is **semi-agentic**, but the architecture is designed to evolve into a fully autonomous curriculum design system.

---

**CurricuForge AI — Designing the future of learning with intelligent agents.**
