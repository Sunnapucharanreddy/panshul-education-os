# Panshul Sathi Seva — Education OS Backend

AI-first Education Operating System: personalized AI teacher, adaptive quizzes,
career guidance, mock interviews, spoken English coaching, and startup mentorship.

## Architecture

```
Clients (Flutter / Next.js)
        │
FastAPI (routes = thin I/O layer only)
        │
Services (business logic, transactions)
        │
AI Orchestrator (LangGraph) ──► Agents (Teacher / Quiz / Career / Interview / Startup)
        │
Provider layer (swappable): LLM · STT · TTS · Embeddings · Vector store
        │
PostgreSQL · Redis · Qdrant
```

Principles:
- **Clean Architecture** — routes never touch the DB or the LLM directly.
- **Provider abstraction** — Qwen 3, Faster-Whisper, XTTS are implementations of
  interfaces in `app/providers/base.py`. Swap models by changing `.env`, not code.
- **Prompts are data** — all prompts live in `prompts/*.yaml`, never in code.
- **Async everywhere** — SQLAlchemy async engine, httpx, async agents.

## Quick start

```bash
cp .env.example .env      # fill in secrets
docker compose up -d      # postgres, redis, qdrant, api
# or locally:
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Layout

| Path | Responsibility |
|---|---|
| `app/api/v1/` | HTTP routes only — parse, validate, delegate, respond |
| `app/services/` | Business logic, use-cases |
| `app/agents/` | AI agents + LangGraph orchestrator |
| `app/providers/` | Model adapters behind abstract interfaces |
| `app/repositories/` | DB access (SQLAlchemy) |
| `app/db/models/` | ORM entities |
| `prompts/` | Versioned YAML prompt templates |
| `tests/` | Pytest (async) |

## Tests

```bash
pytest -q
```
