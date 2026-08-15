"""Utility: create DB tables using SQLAlchemy metadata.

This script is intentionally simple for dev environments. For production migrations use Alembic.
"""
from app.db.session import engine
from app.models import Base


def main():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")


if __name__ == "__main__":
    main()
