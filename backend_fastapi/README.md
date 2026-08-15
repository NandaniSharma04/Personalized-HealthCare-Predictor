# Backend (FastAPI) scaffold

This folder contains a production-ready scaffold for a FastAPI backend.

Quickstart (dev):

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn app.main:app --reload --port 8000
```

The app exposes a `/health` endpoint and `/api/symptoms` (reads the canonical symptom list from the repository).
