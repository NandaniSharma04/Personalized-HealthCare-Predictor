from fastapi import FastAPI
from .core.logging import configure_logging
from .routers import router as api_router

configure_logging("./backend/logs/backend.log")

app = FastAPI(title="Personalized Healthcare API")

app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
