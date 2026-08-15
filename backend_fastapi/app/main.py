from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import logging
from starlette.responses import PlainTextResponse

from .core.logging_config import configure_logging
from .core.config import settings
from .middleware.security import SecurityHeadersMiddleware, SimpleRateLimitMiddleware, RequestSizeLimitMiddleware

from .api import auth as auth_router
from .api import users as users_router
from .api import predict as predict_router
from .api import activity as activity_router
from .api import recommend as recommend_router
from .api import admin as admin_router
from .api import analyst as analyst_router
from .api import models_api as models_router
from .api import feedback as feedback_router
from .api import monitor as monitor_router


app = FastAPI(title="Personalized Healthcare API")

# configure logging early
configure_logging(log_file=Path(__file__).resolve().parents[2] / "logs" / "app.log")
logger = logging.getLogger(__name__)

allowed = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security middlewares
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, calls_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
app.add_middleware(SecurityHeadersMiddleware)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(predict_router.router)
app.include_router(activity_router.router)
app.include_router(recommend_router.router)
app.include_router(admin_router.router)
app.include_router(analyst_router.router)
app.include_router(models_router.router)
app.include_router(feedback_router.router)
app.include_router(monitor_router.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/symptoms")
def get_symptoms():
    # Read canonical symptom list from existing repository file
    repo_root = Path(__file__).resolve().parents[2]
    symptom_file = repo_root / "backend" / "ml" / "symptom_list.json"
    if not symptom_file.exists():
        return {"error": "symptom list not found"}
    with symptom_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {"n_symptoms": len(data), "symptoms": data}


@app.exception_handler(Exception)
def generic_exception_handler(request, exc):
    # log exception and return non-detailed error
    logger.exception("Unhandled exception: %s", exc)
    return PlainTextResponse("Internal server error", status_code=500)
