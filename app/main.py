from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import router as api_router


app = FastAPI(title="PDF Extract Service", version="0.2.0")

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/")
async def root():
    """Serve the frontend UI."""
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(api_router, prefix="")

# Mount static files (after routes to not override them)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


