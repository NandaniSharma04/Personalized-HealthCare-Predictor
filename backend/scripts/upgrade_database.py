"""
Database Schema Safe Migration & Upgrade Script
Safely extends existing SQLite databases without destroying existing user accounts or prediction history.
"""
import sqlite3
from pathlib import Path

def upgrade_sqlite_database(db_path: Path):
    if not db_path.exists():
        print(f"[MIGRATION WARN] Database file not found: {db_path}")
        return

    print(f"[MIGRATION] Safe schema upgrade on: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Inspect existing columns in users table
    cursor.execute("PRAGMA table_info(users)")
    existing_user_cols = {row[1] for row in cursor.fetchall()}

    new_user_cols = {
        "status": "TEXT DEFAULT 'active'",
        "updated_at": "TIMESTAMP NULL",
        "last_login": "TIMESTAMP NULL"
    }
    for col_name, col_def in new_user_cols.items():
        if col_name not in existing_user_cols:
            print(f"  + Adding column users.{col_name}")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")

    # 2. Inspect existing columns in prediction_history table
    cursor.execute("PRAGMA table_info(prediction_history)")
    existing_pred_cols = {row[1] for row in cursor.fetchall()}

    if "model_version" not in existing_pred_cols:
        print("  + Adding column prediction_history.model_version")
        cursor.execute("ALTER TABLE prediction_history ADD COLUMN model_version TEXT DEFAULT 'v1.0.0'")

    # 3. Create missing tables safely
    tables = [
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(255)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            phone VARCHAR(30),
            address VARCHAR(255),
            avatar_url VARCHAR(512),
            bio TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS health_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            age INTEGER,
            gender VARCHAR(20),
            allergies JSON,
            existing_conditions JSON,
            current_medications JSON,
            health_preferences JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS recommendation_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recommendation_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            feedback_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS saved_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recommendation_id INTEGER NOT NULL,
            title VARCHAR(200),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type VARCHAR(64) NOT NULL,
            details JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query VARCHAR(255) NOT NULL,
            results_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sentiment_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT NOT NULL,
            sentiment_score FLOAT NOT NULL,
            sentiment_label VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_version_id INTEGER NOT NULL,
            accuracy FLOAT,
            macro_f1 FLOAT,
            kl_divergence FLOAT,
            metrics_json JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(model_version_id) REFERENCES model_versions(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor VARCHAR(120) NOT NULL,
            action VARCHAR(128) NOT NULL,
            entity VARCHAR(128),
            result VARCHAR(64) DEFAULT 'SUCCESS',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    for stmt in tables:
        cursor.execute(stmt)

    conn.commit()
    conn.close()
    print(f"[MIGRATION SUCCESS] Database {db_path.name} upgraded successfully!")

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parents[1]
    upgrade_sqlite_database(backend_dir / "healthai.db")
    upgrade_sqlite_database(backend_dir / "scripts" / "demo_sqlite.db")
