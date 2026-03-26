# AGENTS.md

## 1. Purpose of this repository

This repository contains a learning project for an AI-driven meal planner web app.

Current characteristics:
- FastAPI backend (Python)
- Simple frontend
- Supabase-backed recipe storage
- AI-generated weekly meal plans
- MVP-level scope, intentionally simple

Primary goal:
Learn AI-assisted and agent-driven software development step by step.

This is not a production system.
Clarity, safety, and maintainability are more important than speed or cleverness.

---

## 2. Development philosophy

Always prioritize:
- small, incremental changes
- readable code
- predictable behavior
- easy human review
- preserving working functionality

Avoid:
- large speculative refactors
- unnecessary abstractions
- heavy new frameworks
- mixing unrelated changes in one PR
- changing architecture without clear need

Preferred mindset:
- make the smallest safe change that solves the requested problem
- keep changes beginner-friendly and easy to understand
- prefer explicit code over “smart” code

---

## 3. Current architecture

Backend:
- `backend/app/main.py` → FastAPI app entrypoint and router wiring
- `backend/app/routers/` → HTTP/API endpoints grouped by domain
  - `frontend.py`
  - `recipes.py`
  - `meal_plan.py`
  - `tags.py`
  - `health.py`
- `backend/app/services/` → business logic and integration logic
- `backend/test_main.py` → pytest tests

Frontend:
- `frontend/index.html`

General rules:
- routers handle HTTP concerns
- services handle reusable logic / orchestration
- `main.py` wires the application together
- prefer extending the existing structure before creating new layers

---

## 4. Source of truth and branch policy

The `main` branch is the single source of truth and must remain stable.

Mandatory rules:
- NEVER commit directly to `main`
- ALWAYS work from a feature/fix/refactor branch
- ALWAYS use a Pull Request
- CI must pass before merge
- Human review is required before merge

Branch naming:
- `feature/<short-description>`
- `fix/<short-description>`
- `refactor/<short-description>`

Examples:
- `feature/add-ping-endpoint`
- `fix/delete-nonexistent-recipe-404`
- `refactor/split-recipe-service`

---

## 5. Standard workflow

For any requested change, follow this sequence:

1. inspect the relevant files
2. understand the smallest safe implementation
3. create a branch
4. implement the change
5. add or update tests
6. run tests
7. commit with a clear message
8. push branch
9. open a PR
10. summarize what changed, what was tested, and any assumptions

Do not skip validation.
Do not bypass PR review.
Do not mix unrelated cleanup into the same change.
Before proposing exact code changes, inspect the target files that will be modified
If the task asks for exact paste-ready code, inspect the target files first; otherwise clearly state that the result is a proposed patch and not exact repo-verified code

## Pull Request Rules

- All PRs MUST be created as DRAFT
- Do NOT mark PR as ready for review
- Human will decide when to move to review

---

## 6. Commands

Use these commands unless the repository structure changes.

Install dependencies:
`pip install -r requirements.txt`

Run backend tests:
`cd backend && pytest test_main.py`

Run backend app locally:
`cd backend && uvicorn app.main:app --reload`

Notes:
- If a command fails because the repo evolves, inspect the current repo and adjust conservatively
- Do not invent new tooling unless explicitly requested

---

## 7. Environment and secrets

Rules:
- `.env` is local only and must never be committed
- never commit secrets, API keys, tokens, or credentials
- do not modify secret handling unless explicitly requested
- do not print or expose environment variable values in commits, PRs, logs, or comments

Assume:
- some app features may depend on external services
- tests should remain runnable without requiring new secrets whenever possible

If a change would require a new secret or environment variable:
- do not implement silently
- document it clearly in the PR
- prefer mock-based or test-safe approaches when possible

---

## 8. Code placement rules

When implementing features:

### Routers
Use `backend/app/routers/` for endpoints and HTTP-layer behavior.
Examples:
- request handling
- status codes
- endpoint paths
- response shaping

### Services
Use `backend/app/services/` for business logic or reusable non-HTTP logic.
Examples:
- recipe-related logic
- meal generation orchestration
- external service interaction
- shared helper logic that should not live inside route handlers

### Main app
Use `backend/app/main.py` for app creation and router inclusion.
Do not move business logic into `main.py`.

Preferred rule:
- if a new feature fits an existing router, extend that router
- only create a new router if the feature clearly deserves its own domain grouping

---

## 9. Testing conventions

Testing is required for meaningful behavior changes.

Current test location:
- `backend/test_main.py`

Preferred rules:
- keep using `backend/test_main.py` unless there is a clear reason to split tests
- match the style of existing tests
- add or update tests for new behavior
- do not remove tests unless explicitly requested and justified
- always inspect existing tests and follow the same patterns (e.g. how TestClient is created)
- do not introduce new pytest fixtures (e.g. `client`) unless they already exist in the codebase
- prefer copying an existing test pattern over inventing a new one
- when giving exact test code, first inspect the existing test file and match its pattern
- if the existing test file was not inspected, do not assume fixtures or local test helpers; state the assumption explicitly

At minimum:
- new endpoint → add endpoint tests
- changed behavior → update affected tests
- bug fix → add regression-style coverage when possible

Do not claim a change is complete if tests were not run.

If tests cannot be run:
- say so explicitly
- explain why
- do not pretend validation happened



---

## 10. API conventions

For API changes:
- follow existing FastAPI patterns
- keep endpoint naming explicit and consistent
- prefer predictable status codes
- keep responses simple and stable
- avoid embedding too much business logic inside route handlers

When in doubt:
- extend an existing router rather than creating a new pattern
- keep the implementation minimal
- preserve backward compatibility unless the change explicitly requires a behavior change

---

## 11. Refactoring rules

Refactoring is allowed only when:
- it is necessary for the requested feature or fix, OR
- it clearly improves readability with low risk

Rules:
- preserve current behavior unless behavior change is requested
- keep refactors small
- do not refactor unrelated areas opportunistically
- do not rename files/modules unless necessary
- do not combine broad refactors with feature work unless unavoidable

If a useful refactor is optional:
- mention it separately in the PR
- do not include it automatically

---

## 12. Safe actions the agent may take automatically

Allowed actions:
- create a branch
- edit existing Python files
- add small files within the current structure
- add/update tests
- run tests
- commit changes
- push branch
- open a PR

These are allowed only if they are directly relevant to the requested change.

---

## 13. Actions requiring explicit human approval

Do not do any of the following unless explicitly requested:

- modify GitHub Actions / CI workflows
- add or change dependencies
- change deployment configuration
- change secret or environment handling
- rename major files or modules
- delete files
- change database structure
- introduce a new framework
- perform large structural refactors
- change multiple unrelated areas in one PR

When approval is needed:
- stop at proposal level
- explain the reason clearly in the PR or summary

---

## 14. Protected areas / do-not-touch-by-default

Do not modify these unless the task explicitly requires it:
- `.github/workflows/`
- dependency manifests
- `.env` handling
- deployment/configuration files
- Supabase configuration
- external API configuration
- secret management code

Assume these areas are sensitive.

---

## 15. Change-size guardrails

Default expectations:
- keep PRs small and focused
- avoid touching many files for a simple request
- do not add a dependency for a small feature
- do not bundle cleanup with feature work

Preferred default:
- one feature/fix per branch
- one focused PR per change

If a task appears to require a larger change:
- choose the smallest viable increment
- document assumptions and follow-up work

---

## 16. Handling ambiguity

If a request is ambiguous:
- prefer the smallest reasonable implementation
- do not invent hidden requirements
- do not overbuild
- keep behavior aligned with existing patterns
- document assumptions clearly in the PR

Example rule:
If asked to “add a ping endpoint,” prefer adding it to the existing health router rather than inventing a new monitoring subsystem.

---

## 17. Definition of done

A task is complete only if:
- the requested behavior is implemented
- relevant tests exist or were updated
- tests were run and passed, or inability to run them was stated honestly
- no unrelated changes were bundled in
- the PR is clear and reviewable

---

## 18. PR format

Each PR should include:

### Summary
What changed and why

### Files changed
Brief list of touched files

### Testing
Exact tests/commands run

### Assumptions
Anything the agent assumed due to ambiguity

### Notes / follow-up
Optional future improvements, clearly separated from the current scope

PRs should be concise, explicit, and easy to review.

---

## 19. Commit message style

Use simple, clear commit messages.
- commit messages must reflect the actual change performed, not the original request

Examples:
- `Add /ping endpoint with UTC timestamp`
- `Return 404 when deleting nonexistent recipe`
- `Move recipe logic into service module`

Avoid vague messages like:
- `updates`
- `fix stuff`
- `changes`

---

## 20. Project-specific preferences

Current owner preferences:
- transparency over full automation
- browser/GitHub-friendly workflow
- minimal local tooling
- human review before merge
- incremental evolution toward agent-driven development

Agents should act conservatively and support these goals.

---

## 21. If uncertain

If uncertain:
- inspect the repo first
- choose the simplest working approach
- avoid guessing
- document assumptions
- prefer a small safe PR over a broad solution

When multiple valid implementations exist, prefer the one that:
- fits the current structure
- minimizes diff size
- is easiest to test
- is easiest for a human reviewer to understand
