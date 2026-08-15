try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic.v1 import BaseSettings
    except ImportError:
        from pydantic import BaseSettings


import os
from pathlib import Path

_demo_db = Path(__file__).resolve().parents[3] / "backend" / "scripts" / "demo_sqlite.db"
_sqlite_url = f"sqlite:///{_demo_db.as_posix()}" if _demo_db.exists() else "sqlite:///./healthai.db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personalized Healthcare API"
    DATABASE_URL: str = os.environ.get("DATABASE_URL") or _sqlite_url
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    # CORS and security
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120
    MAX_REQUEST_SIZE: int = 1_048_576  # 1 MB
    ENABLE_HTTPS_REDIRECT: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
