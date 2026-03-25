# FlipFinder Hosted Starter

This is a starter project for a hosted FlipFinder beta.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Database: Postgres
- Collector: Python ingest process that writes directly to Postgres

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

### Collector

```bash
cd collector
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python collector.py
```
