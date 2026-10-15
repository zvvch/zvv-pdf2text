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


# Icons an der Domain-Wurzel: Browser und Passwortmanager (z. B. 1Password)
# fragen /favicon.ico und /apple-touch-icon.png direkt ab.
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(STATIC_DIR / "favicon.ico", media_type="image/x-icon")


@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    return FileResponse(STATIC_DIR / "apple-touch-icon.png", media_type="image/png")


@app.get("/")
async def root():
    """Serve the frontend UI."""
    return FileResponse(STATIC_DIR / "index.html")


app.include_router(api_router, prefix="")

# Mount static files (after routes to not override them)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


