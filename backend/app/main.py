import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import Base, engine
from .routers import auth, capture, clinics, lesions, profile, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dermalyze API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(lesions.router)
app.include_router(capture.router)
app.include_router(clinics.router)
app.include_router(reports.router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

PAGES_DIR = os.path.join(STATIC_DIR, "pages")


def _page(name: str):
    async def handler():
        return FileResponse(os.path.join(PAGES_DIR, name))

    return handler


app.add_api_route("/", _page("index.html"), methods=["GET"], include_in_schema=False)
for page in [
    "onboarding.html",
    "bodymap.html",
    "capture.html",
    "result.html",
    "clinics.html",
]:
    app.add_api_route(f"/{page}", _page(page), methods=["GET"], include_in_schema=False)


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok"}
