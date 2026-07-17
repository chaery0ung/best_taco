# Dermalyze

A demo service for AI-assisted skin lesion analysis.

## MVP flow

1. Select a body part
2. Upload a lesion photo
3. Get an AI classification result
4. Generate a PDF report
5. Get nearby dermatologist recommendations when needed

## Mock scope of this demo

The real production architecture (Vertex AI CNN classification, Vertex Explainable AI
heatmaps, Gemini API reports, Google Maps API) requires a GCP project, a trained model,
and API keys, so this demo mocks all of it:

- CNN classification + heatmap → deterministic mock classification based on an image
  hash, with a heatmap overlay rendered by Pillow
- Gemini report → template-based natural language report
- Nearby dermatologist search → mock data + Leaflet/OpenStreetMap map (free, no API key needed)

To swap in the real APIs, replace the corresponding mock module under `backend/app/services/`.

## Tech stack

- Backend: FastAPI + SQLAlchemy (PostgreSQL on Render / SQLite for local dev)
- Frontend: plain HTML/CSS/JS (static files served by FastAPI)
- Auth: JWT (bearer token)
- PDF: ReportLab

## Run locally

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit http://localhost:8000 (falls back to local sqlite `dev.db` if `DATABASE_URL` isn't set)

## Deploy to Render

Connect this repo's root `render.yaml` via Render's "Blueprint" deploy to create the
web service and PostgreSQL DB together. `JWT_SECRET` is auto-generated.
