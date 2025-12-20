# Reading App (FastAPI + React)

This project has been refactored away from Streamlit into a clean backend/frontend structure.

## Structure

- `backend/` – FastAPI application
  - `app/main.py` – app factory and router wiring
  - `app/routers/` – API endpoints (`health`, `texts`, `qa`)
  - `app/services/` – business logic (LLM calls, text splitting/loading, evaluation)
  - `app/core/config.py` – environment variables and model settings
- `frontend/` – Vite + React + TypeScript UI
  - `src/pages/Library.tsx` – text reader & Q&A flow
  - `src/pages/Upload.tsx` – upload/simplify/save workflow
  - `src/api/client.ts` – Axios client for backend APIs
- `data/` – persisted content (`texts.json`, `uploads.json`)

## Requirements

- Python 3.10+
- Node 18+
- Environment variables for LLM providers (put them in `.env`):
  - `GEMINI_API_KEY`
  - `GEMINI_AUDIO_API_KEY`
  - `DEEPSEEK_API_KEY`
  - `HF_API_TOKEN`

## Backend

```bash
# from project root
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

- API docs: http://localhost:8000/docs
- Data files are read from `data/`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

- Default dev server: http://localhost:5173
- Configure backend URL with `VITE_API_BASE` (falls back to `http://localhost:8000`)

## Available APIs

- `GET /health` – readiness probe
- `GET /texts?lang=Latvian` – list library texts (built-in + uploads)
- `POST /texts` – upload a new text; splits into fragments
- `POST /texts/preview` – preview fragmenting before saving
- `GET /texts/{name}/parts?lang=` – fetch parts for a given text
- `POST /qa/simplify` – simplify text via LLM
- `POST /qa/format` – clean up formatting/punctuation
- `POST /qa/questions` – generate questions for a fragment
- `POST /qa/evaluate` – evaluate a user answer (rate-limited by `userId`)
- `POST /qa/audio` – synthesize short audio clips for fragments/questions

## Development Notes

- Streamlit files have been removed; all UI lives in the React app.
- Business logic is isolated in `backend/app/services` for reuse.
- Uploaded texts are appended to `data/uploads.json`; adjust persistence as needed.
- Run frontend & backend concurrently for a full experience.

