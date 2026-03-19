# 🤝 Contributing Guidelines

This project follows a **simple, safe, and incremental workflow**.

The goal is to keep changes small, understandable, and easy to review.

---

## Workflow Overview

1. Create a new branch from `main`
2. Implement a small, focused change
3. Run tests locally
4. Push branch to GitHub
5. Open a Pull Request
6. CI runs tests automatically
7. Review and merge

---

## Branch Naming

Use descriptive names:

* `feature/add-ping-endpoint`
* `fix/delete-recipe-404`
* `refactor/split-main-router`

---

## Commit Messages

Keep them short and clear:

* `Add /ping endpoint`
* `Fix delete recipe 404 handling`
* `Refactor router structure`

---

## Pull Request Guidelines

Each PR should:

* Be **small and focused**
* Solve **one problem only**
* Include tests if applicable
* Pass CI checks
* Be easy to understand

---

## Testing Requirements

* All changes must pass existing tests
* New functionality should include tests
* Do not reduce test coverage

Run tests locally:

```bash
cd backend
pytest test_main.py
```

---

## Code Guidelines

* Follow existing structure and patterns
* Avoid unnecessary abstractions
* Do not introduce new services unless needed
* Prefer minimal, clear solutions

---

## What NOT to Do

* Do not commit directly to `main`
* Do not introduce large refactors without clear need
* Do not mix multiple features in one PR
* Do not break existing endpoints

---

## AI Agent Contributions

AI agents are expected to follow:

* `AGENTS.md` → rules and constraints
* `agent-playbook.md` → examples and patterns

Agents must:

* keep changes minimal
* respect project structure
* always work via branches and PRs

---

## Philosophy

* Small changes > big rewrites
* Clarity > cleverness
* Working code > perfect code
* Iteration > overengineering

---
