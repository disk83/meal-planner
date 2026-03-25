# 🍽️ Meal Planner (AI-assisted project)

## Overview

This is a learning project to build a small web app that generates a weekly dinner plan using AI.

The goal is to learn:

* AI-assisted software development
* backend API design with FastAPI
* clean development workflows (tests, CI, PRs)
* emerging **agent-driven development patterns**

---

## Current Features

* Generate weekly dinner suggestions using Claude
* Recipes stored in Supabase
* Add and edit recipes from the UI
* Basic ingredient management
* REST API with FastAPI
* pytest test suite
* GitHub Actions CI (runs tests on PR)

---

## Tech Stack

**Frontend**

* HTML

**Backend**

* Python
* FastAPI
* Uvicorn

**Database**

* Supabase (PostgreSQL)

**AI**

* Claude API

**Testing**

* pytest

---

## Project Structure

```text
meal-planner/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── frontend.py
│   │   │   ├── recipes.py
│   │   │   ├── meal_plan.py
│   │   │   ├── tags.py
│   │   │   └── health.py
│   │   └── services/
│   │
│   └── test_main.py
│
├── frontend/
│   └── index.html
│
├── requirements.txt
└── README.md
```

---

## Running the Project Locally

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the backend

```bash
uvicorn app.main:app --reload
```

API available at:

```
http://127.0.0.1:8000
```

### 3. Open frontend

Open in browser:

```
frontend/index.html
```

---

## Running Tests

```bash
cd backend
pytest test_main.py
```

---
## Deploy backend on Render

Use a **Render Web Service** for the FastAPI backend only. The frontend still contains local development API URLs, so this deployment step is intended to expose the backend API first and validate it with `/health`.

### Render service settings

* **Root directory:** `backend`
* **Build command:** `pip install -r requirements.txt`
* **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The `backend` directory is the correct Render root because it contains the FastAPI app package, the backend-only dependency file, and the existing test entrypoint.

### Required environment variables

The backend already reads runtime configuration from environment variables in `backend/app/config.py`. Set these in the Render dashboard:

* `SUPABASE_URL`
* `SUPABASE_ANON_KEY`
* `ANTHROPIC_API_KEY`

Do not commit these values to the repository.

### Validate the deployment

After the first deploy completes, open:

```text
https://<your-render-service>.onrender.com/health
```

Expected response:

```json
{"status": "ok"}
```

If you want to confirm the same setup locally with a production-style command, run:

```bash
cd backend
PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Then visit `http://127.0.0.1:8000/health`.

---

## Development Workflow

This project follows a **branch → PR → CI → merge** workflow:

1. Create a feature branch from `main`
2. Implement a small change
3. Run tests locally
4. Push branch to GitHub
5. Open Pull Request
6. CI runs tests automatically
7. Review and merge into `main`

See `CONTRIBUTING.md` for full guidelines.

---

## AI Agent Workflow (In Progress 🚧)

This project is evolving toward an **agent-driven development model**, where:

* Features are defined via GitHub Issues
* An AI agent proposes code changes
* The agent creates a Pull Request
* CI runs automatically
* A human reviews and merges

Repository-level instructions:

* `AGENTS.md` → rules and constraints for agents
* `agent-playbook.md` → examples of how tasks should be executed

---

## Status

This is currently an MVP used for **learning and experimentation**.

The focus is on:

* building incrementally
* keeping changes small and safe
* improving structure over time
* exploring AI-assisted and agent-based workflows

---

## Roadmap

* Improve backend structure (modularization)
* Expand test coverage
* Enhance meal planning logic
* Introduce agent-driven PR creation
* Improve frontend UX

---

## Purpose of the Project

This project is intentionally iterative.

It serves as a playground to:

* learn backend and API design
* explore AI-assisted development
* experiment with safe agent workflows
* understand how AI can contribute to real codebases

---

## Architecture
frontend repo/app deploys to Vercel on push to main
backend repo/app deploys to Render on push to main (vercel has only limited capability for fastAPI)
frontend calls deployed backend URL
backend uses Supabase credentials via environment variables
production is auto-updated from main
