🔗 Frontend Repository
https://github.com/jwondeye/expense-tracker

# Expense Tracker Backend (FastAPI)

This repository contains the backend service for a full-stack expense tracker application.  
The backend is built with **FastAPI** and exposes RESTful endpoints for managing expenses, calculating monthly summaries, and supporting budget tracking.

---

## 🚀 Tech Stack
- FastAPI (Python)
- SQLAlchemy (ORM)
- SQLite (local development)
- Pydantic (data validation)
- Docker

---

## ✨ Features
- Full CRUD for expenses
- Filter expenses by month and year
- Monthly spending summary by category
- Budget comparison support
- Clean REST API design
- Dockerized backend service

---

## 📂 Project Structure
backend_expenses/
├── main.py
├── requirements.txt
├── Dockerfile
└── expenses.db (ignored)

## 🔌 API Endpoints

| Method | Endpoint | Description |
|------|---------|-------------|
| GET | `/health` | Health check |
| POST | `/expenses` | Create expense |
| GET | `/expenses?month=&year=` | Get expenses |
| PUT | `/expenses/{id}` | Update expense |
| DELETE | `/expenses/{id}` | Delete expense |
| GET | `/expenses/summary?month=&year=` | Monthly summary |

---

## 🐳 Run with Docker

```bash
docker build -t expense-backend .
docker run -p 8000:8000 expense-backend
http://localhost:8000/docs'
