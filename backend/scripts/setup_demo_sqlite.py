"""Create a lightweight SQLite demo DB and seed minimal tables used by the dashboard.
This is intended for local dev when Postgres is unavailable.
"""
import os
import sys
from sqlalchemy import create_engine, text
from pathlib import Path

# Ensure the project root is on sys.path so `app` package imports work
HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.models import Base
# Import model modules so their classes are registered with Base.metadata
import app.models.auth_models  # noqa: F401
import app.models.user_models  # noqa: F401

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "demo_sqlite.db"
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

def create_tables_and_seed():
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

    # Create ORM models tables (users, profiles, notifications, saved_items, etc.)
    Base.metadata.create_all(engine)

    with engine.begin() as conn:
        # Create simple versions of tables the repo queries via raw SQL
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            version TEXT,
            description TEXT,
            metadata TEXT,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            model_version_id INTEGER,
            input_features TEXT,
            prediction TEXT,
            confidence REAL,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rec_type TEXT,
            source TEXT,
            model_version_id INTEGER,
            score REAL,
            metadata TEXT,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            record_type TEXT,
            record TEXT,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            interaction_type TEXT,
            target_type TEXT,
            target_id INTEGER,
            metadata TEXT,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            target_type TEXT,
            target_id INTEGER,
            rating INTEGER,
            comment TEXT,
            created_at DATETIME DEFAULT (datetime('now'))
        );
        """))

        # Seed a demo user if not exists (use ORM user table shape)
        # users table created by Base.metadata.create_all
        res = conn.execute(text("SELECT id FROM users WHERE username = :u"), dict(u='demo'))
        if not res.fetchone():
            conn.execute(text("INSERT INTO users (username, email, hashed_password, is_active, is_superuser) VALUES (:u,:e,:p,1,0)"), dict(u='demo', e='demo@example.com', p='demo_pw'))
            uid = conn.execute(text("SELECT id FROM users WHERE username = :u"), dict(u='demo')).fetchone()[0]

            # profile
            conn.execute(text("INSERT OR REPLACE INTO user_profiles (user_id, first_name, last_name) VALUES (:uid,:fn,:ln)"), dict(uid=uid, fn='Demo', ln='User'))

            # medical profile
            conn.execute(text("INSERT OR REPLACE INTO medical_profiles (user_id, blood_type, allergies) VALUES (:uid,:bt,:al)"), dict(uid=uid, bt='O+', al='None'))

            # model version
            conn.execute(text("INSERT INTO model_versions (name, version, description) VALUES ('baseline_rf', 'v1', 'demo model')"))
            mv_id = conn.execute(text("SELECT id FROM model_versions WHERE name='baseline_rf' LIMIT 1")).fetchone()[0]

            # prediction
            conn.execute(text("INSERT INTO prediction_history (user_id, model_version_id, input_features, prediction, confidence) VALUES (:uid,:mv,:f,:p,:c)"), dict(uid=uid, mv=mv_id, f='{"symptoms": ["Fever"]}', p='{"disease":"Influenza"}', c=0.86))

            # recommendation
            conn.execute(text("INSERT INTO recommendations (user_id, rec_type, source, model_version_id, score, metadata) VALUES (:uid, :rec_type, :source, :mv, :score, :metadata)"), dict(uid=uid, rec_type='personal', source='demo', mv=mv_id, score=0.9, metadata='{"title":"Stay hydrated"}'))

            # notification
            conn.execute(text("INSERT INTO notifications (user_id, message, payload, is_read) VALUES (:uid, :msg, :payload, :is_read)"), dict(uid=uid, msg='Welcome to the demo dashboard', payload='{"type":"welcome"}', is_read=0))

            print('Demo data seeded for user id', uid)
        else:
            print('Demo user already exists, skipping seeding.')


if __name__ == '__main__':
    create_tables_and_seed()
