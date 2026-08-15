from pydantic_settings import BaseSettings
from pathlib import Path
import os


demo_db = Path(__file__).resolve().parents[3] / "backend" / "scripts" / "demo_sqlite.db"
health_db = Path(__file__).resolve().parents[3] / "backend" / "healthai.db"

if demo_db.exists():
    DEFAULT_SQLITE = f"sqlite:///{demo_db.as_posix()}"
elif health_db.exists():
    DEFAULT_SQLITE = f"sqlite:///{health_db.as_posix()}"
else:
    DEFAULT_SQLITE = "sqlite:///./healthai.db"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Personalized Healthcare API"
    DATABASE_URL: str = os.environ.get("DATABASE_URL") or DEFAULT_SQLITE
    SECRET_KEY: str = "CHANGEME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
