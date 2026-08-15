"""Simple migration runner: execute SQL files in backend/migrations in lexical order."""
import os
import glob
from sqlalchemy import create_engine, text
from pathlib import Path
from ..app.core.config import settings


def run():
    mig_dir = Path(__file__).resolve().parent.parent / "migrations"
    files = sorted(glob.glob(str(mig_dir / "*.sql")))
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        for f in files:
            print("Applying", f)
            sql = Path(f).read_text()
            conn.execute(text(sql))


if __name__ == "__main__":
    run()
