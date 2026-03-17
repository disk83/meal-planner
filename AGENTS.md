# AGENTS.md

## 1. Project purpose

This is a learning project to build an AI-driven meal planner web app.

Current characteristics:
- FastAPI backend (Python)
- Simple HTML frontend
- Supabase database
- AI-generated weekly meal plans
- MVP-level, intentionally simple

Primary goal:
Learn AI-assisted and agent-driven software development step by step.

This is NOT a production system.
Clarity, safety, and learning are more important than speed or complexity.

---

## 2. Development philosophy

Always prioritize:
- small, incremental changes
- readability and simplicity
- preserving working behavior
- easy human review

Avoid:
- large refactors unless explicitly requested
- introducing heavy frameworks
- mixing unrelated changes
- “clever” or over-engineered solutions

---

## 3. Current architecture

Backend structure:

- `backend/app/main.py` → FastAPI app entrypoint
- `backend/app/routers/` → API endpoints grouped by domain
  - frontend
  - recipes
  - meal_plan
  - tags
  - health
- `backend/app/services/` → business logic
- `backend/test_main.py` → pytest tests

Frontend:
- `frontend/index.html`

General rules:
- routers = HTTP layer
- services = logic layer
- keep separation clear when possible

---

## 4. Git and workflow rules (CRITICAL)

The `main` branch is the single source of truth and must remain stable.

MANDATORY rules:
- NEVER commit directly to `main`
- ALWAYS use a feature branch
- ALWAYS open a Pull Request
- CI must pass before merge

Workflow:
1. create branch
2. implement change
3. run tests
4. commit
5. push
6. open PR
7. CI runs
8. human reviews
9. merge

Branch naming:
- `feature/<description>`
- `fix/<description>`
- `refactor/<description>`

Examples:
- `feature/add-ping-endpoint`
- `fix/delete-nonexistent-recipe-404`

---

## 5. Testing and validation

Tests are required for meaningful changes.

- Use pytest (`backend/test_main.py`)
- If adding behavior → add or update tests
- If modifying behavior → ensure existing tests still pass

Before PR:
- run tests locally if possible
- do not claim completion without validation

---

## 6. API and coding conventions

- Follow existing FastAPI patterns
- Keep endpoints consistent with current routers
- Avoid putting business logic in routers
- Prefer explicit and readable code

When adding functionality:
- extend existing routers when appropriate
- use services for logic reuse
- avoid duplicating logic

---

## 7. Refactoring rules

Refactoring is allowed ONLY if:
- it improves clarity, OR
- it is required for the requested change

Rules:
- preserve behavior unless explicitly changing it
- keep refactors small and isolated
- do not refactor unrelated areas

If a refactor is optional → suggest it, do not include it automatically

---

## 8. Agent operating protocol

When performing a task, follow this sequence:

1. Understand the request
2. Inspect relevant files
3. Identify smallest safe change
4. Implement change
5. Add/update tests
6. Run tests
7. Prepare PR

Agents must prefer:
- minimal diffs
- safe changes
- easy review

---

## 9. Definition of done

A change is complete ONLY if:
- requested behavior works
- tests pass
- no unintended behavior is broken
- PR is clear and reviewable

---

## 10. Safe vs unsafe actions

Safe actions:
- create feature branches
- edit Python files
- add small files
- update tests
- open PRs

Use caution:
- modifying project structure
- adding dependencies
- renaming files
- deleting code

Unsafe (never do unless explicitly asked):
- commit directly to `main`
- disable tests
- bypass CI
- large unrelated refactors
- modify secrets or environment config

---

## 11. If uncertain

If unsure:
- choose the simplest implementation
- do NOT guess hidden requirements
- document assumptions in PR
- ask for clarification instead of overbuilding

---

## 12. Project evolution context

This project is evolving toward agent-driven development.

Current preferences:
- transparency over automation
- human review before merge
- browser/GitHub-friendly workflow
- minimal local tooling

Agents should act conservatively and support this transition.