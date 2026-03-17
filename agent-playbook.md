# Agent Playbook

This document defines how to execute development tasks in this repository in a safe, consistent, and minimal way.

It provides concrete examples so that work follows the same patterns every time.

---

## 1. General execution flow

For any task, follow this exact sequence:

1. Understand the request
2. Identify the smallest possible implementation
3. Locate the correct files
4. Implement the change
5. Add or update tests
6. Run tests
7. Prepare a Pull Request

Always prefer:
- small changes
- minimal diff
- reuse of existing structure
- easy human review

---

## 2. Example: Add a simple endpoint

Request:
Add a `/ping` endpoint that returns a timestamp.

Interpretation:
- Small feature
- Belongs to health domain
- No new router needed
- No new dependencies needed

Implementation:

File: backend/app/routers/health.py

from datetime import datetime, UTC

@router.get("/ping")
def ping():
    return {
        "status": "ok",
        "timestamp": datetime.now(UTC).isoformat(),
    }

Test:

File: backend/test_main.py

def test_ping_returns_200(client):
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_returns_status_ok_and_timestamp(client):
    response = client.get("/ping")
    data = response.json()

    assert data["status"] == "ok"
    assert "timestamp" in data

    from datetime import datetime
    datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

Validation:

cd backend && pytest test_main.py

Branch name:
feature/add-ping-endpoint

Commit message:
Add /ping endpoint with UTC timestamp

PR summary:
- Added /ping endpoint
- Returns status and timestamp
- Added tests
- No structural changes

---

## 3. Example: Fix a bug

Request:
Deleting a nonexistent recipe should return 404.

Implementation steps:

1. Locate deletion logic (recipes router or service)
2. Add existence check
3. Return 404 if not found

Test:

def test_delete_nonexistent_recipe_returns_404(client):
    response = client.delete("/recipes/nonexistent-id")
    assert response.status_code == 404

Validation:

cd backend && pytest test_main.py

Branch:
fix/delete-nonexistent-recipe-404

PR summary:
- Added validation for missing resource
- Returns 404 correctly
- Added regression test

---

## 4. Example: Small refactor

Request:
Move logic out of router into service

When allowed:
- logic is reusable OR
- router is cluttered

Implementation:

Before:
@router.post("/recipes")
def create_recipe(...):
    # logic here

After:

Service (backend/app/services/recipe_service.py):
def create_recipe_service(...):
    # logic here

Router:
@router.post("/recipes")
def create_recipe(...):
    return create_recipe_service(...)

Validation:
- Run tests
- Ensure behavior unchanged

Branch:
refactor/move-recipe-logic-to-service

---

## 5. Example: Do NOT overengineer

Request:
Add a new endpoint

Bad approach:
- create new architecture layers
- introduce frameworks
- redesign routing

Good approach:
- extend existing router
- add minimal logic
- follow existing patterns

Rule:
Match the current project level. Do not overbuild.

---

## 6. Handling ambiguity

If the request is unclear:

Do NOT:
- redesign the system
- add new components blindly

Do:
- implement smallest useful improvement
- OR ask for clarification
- OR document assumptions in PR

---

## 7. PR template

Summary:
What changed and why

Files changed:
- list of modified files

Testing:
- commands executed
- results

Assumptions:
- anything inferred

Notes:
- optional follow-ups

---

## 8. Commit message guidelines

Good:
- Add /ping endpoint
- Fix delete 404 behavior
- Move logic to service

Bad:
- updates
- fix stuff
- changes

---

## 9. Common mistakes to avoid

- modifying unrelated files
- mixing refactor and feature
- not adding tests
- not running tests
- overengineering
- adding dependencies unnecessarily
- modifying CI/config

---

## 10. Golden rule

Always choose the smallest change that:
- works
- is tested
- is easy to review
- fits the current codebase

This project evolves incrementally.
