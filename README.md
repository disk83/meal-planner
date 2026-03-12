# Meal Planner (AI-assisted project)

This is a learning project to build a small web app that generates a weekly dinner plan using AI.

The goal is to learn AI-assisted software development step by step.

## Current Features

- Generate weekly dinner suggestions using Claude
- Recipes stored in Supabase
- Add and edit recipes from the UI
- Basic ingredient management

## Tech Stack

Frontend:
- HTML

Backend:
- Python
- FastAPI
- Uvicorn

Database:
- Supabase (PostgreSQL)

AI:
- Claude API

## Project Structure

meal-planner
│
├── backend
│   ├── main.py
│   └── test_main.py
│
├── frontend
│   └── index.html
│
├── requirements.txt
└── README.md

## Running the project locally

Run the backend:
uvicorn backend.main:app --reload


Then open `frontend/index.html` in the browser.

## Status

This is currently an MVP used for learning and experimentation.