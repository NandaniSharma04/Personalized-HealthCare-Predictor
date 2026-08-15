"""
Database Schema Migration and Column Synchronizer
Ensures all tables and columns in backend/models.py are present in backend/healthai.db
"""
import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.utils.db import db

def migrate_and_sync():
    app = create_app()
    with app.app_context():
        db_path = PROJECT_ROOT / "backend" / "healthai.db"
        print(f"Synchronizing database at {db_path}...")
        
        # 1. Create any missing tables
        db.create_all()
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        def ensure_column(table: str, col_name: str, col_type: str):
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = {row[1] for row in cursor.fetchall()}
                if col_name not in cols:
                    print(f"Adding missing column '{col_name}' ({col_type}) to table '{table}'...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
            except Exception as err:
                print(f"Error checking {table}.{col_name}: {err}")

        # Table: recommendations
        ensure_column("recommendations", "user_id", "INTEGER")
        ensure_column("recommendations", "recommendation_type", "VARCHAR(50) DEFAULT 'general'")
        ensure_column("recommendations", "item", "JSON")
        ensure_column("recommendations", "score", "FLOAT DEFAULT 1.0")
        ensure_column("recommendations", "reason", "TEXT")
        ensure_column("recommendations", "model", "VARCHAR(100) DEFAULT 'HybridRecommender'")
        ensure_column("recommendations", "created_at", "DATETIME")

        # Table: saved_recommendations
        ensure_column("saved_recommendations", "user_id", "INTEGER")
        ensure_column("saved_recommendations", "recommendation_id", "INTEGER")
        ensure_column("saved_recommendations", "title", "VARCHAR(200)")
        ensure_column("saved_recommendations", "notes", "TEXT")
        ensure_column("saved_recommendations", "created_at", "DATETIME")

        # Table: recommendation_feedback
        ensure_column("recommendation_feedback", "user_id", "INTEGER")
        ensure_column("recommendation_feedback", "recommendation_id", "INTEGER")
        ensure_column("recommendation_feedback", "rating", "INTEGER")
        ensure_column("recommendation_feedback", "feedback_text", "TEXT")
        ensure_column("recommendation_feedback", "created_at", "DATETIME")

        # Table: user_activity
        ensure_column("user_activity", "user_id", "INTEGER")
        ensure_column("user_activity", "activity_type", "VARCHAR(64)")
        ensure_column("user_activity", "details", "JSON")
        ensure_column("user_activity", "created_at", "DATETIME")

        # Table: notifications
        ensure_column("notifications", "user_id", "INTEGER")
        ensure_column("notifications", "title", "VARCHAR(150)")
        ensure_column("notifications", "message", "TEXT")
        ensure_column("notifications", "is_read", "BOOLEAN DEFAULT 0")
        ensure_column("notifications", "created_at", "DATETIME")

        # Table: audit_logs
        ensure_column("audit_logs", "actor", "VARCHAR(120)")
        ensure_column("audit_logs", "action", "VARCHAR(128)")
        ensure_column("audit_logs", "entity", "VARCHAR(128)")
        ensure_column("audit_logs", "result", "VARCHAR(64)")
        ensure_column("audit_logs", "timestamp", "DATETIME")

        conn.commit()
        conn.close()
        print("Database synchronization completed successfully.")

if __name__ == "__main__":
    migrate_and_sync()
