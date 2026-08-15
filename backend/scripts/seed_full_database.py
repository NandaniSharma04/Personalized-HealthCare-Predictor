"""
Full Database Seeder for HealthAI Platform.
Populates SQLite database from the 6 raw CSV files and generates initial analytics records.
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import random
import bcrypt

def hash_password(pw: str) -> str:
    pw_bytes = pw.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw_dataset"
DB_PATHS = [
    PROJECT_ROOT / "backend" / "healthai.db",
    PROJECT_ROOT / "backend" / "scripts" / "demo_sqlite.db"
]

def seed_database():
    print("[DB SEEDER] Starting full database seeding...")
    
    # Load raw CSV datasets
    desc_df = pd.read_csv(DATA_DIR / "description.csv")
    med_df = pd.read_csv(DATA_DIR / "medications.csv")
    prec_df = pd.read_csv(DATA_DIR / "precautions.csv")
    diets_df = pd.read_csv(DATA_DIR / "diets.csv")
    workout_df = pd.read_csv(DATA_DIR / "workout.csv")
    symptoms_df = pd.read_csv(DATA_DIR / "Diseases_and_Symptoms_dataset.csv")

    symptoms_list = [c for c in symptoms_df.columns if c != "diseases"]

    for db_path in DB_PATHS:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Create Core Tables
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(254) UNIQUE NOT NULL,
            name VARCHAR(200),
            hashed_password VARCHAR(512) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER,
            role_id INTEGER,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) UNIQUE NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS disease_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER UNIQUE,
            medications TEXT,
            diets TEXT,
            workouts TEXT,
            precautions TEXT,
            FOREIGN KEY (disease_id) REFERENCES diseases(id)
        );

        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            input_vector TEXT,
            predicted_disease VARCHAR(255),
            probabilities TEXT,
            explainability TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symptoms TEXT,
            prediction VARCHAR(255),
            confidence REAL,
            risk_level VARCHAR(50),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type VARCHAR(128),
            event_payload TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            sentiment_score REAL,
            sentiment_label VARCHAR(50),
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS model_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL,
            version VARCHAR(64) NOT NULL,
            metrics TEXT,
            path VARCHAR(1024),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Insert Default Roles
        for role in ["user", "analyst", "admin"]:
            cur.execute("INSERT OR IGNORE INTO roles (name) VALUES (?)", (role,))
        
        conn.commit()

        # Seed Users intelligently based on table columns
        cols = [info[1] for info in cur.execute("PRAGMA table_info(users)").fetchall()]
        users_data = [
            ("admin@health.ai", "System Admin", hash_password("admin123"), "admin"),
            ("analyst@health.ai", "Health Analyst", hash_password("analyst123"), "analyst"),
            ("patient@health.ai", "John Doe", hash_password("patient123"), "user"),
        ]

        for email, name, pw, rname in users_data:
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            row = cur.fetchone()
            if not row:
                if "hashed_password" in cols:
                    if "name" in cols:
                        cur.execute("INSERT INTO users (email, name, hashed_password) VALUES (?, ?, ?)", (email, name, pw))
                    elif "username" in cols:
                        is_super = 1 if rname == 'admin' else 0
                        if "is_active" in cols and "is_superuser" in cols:
                            cur.execute("INSERT INTO users (email, username, hashed_password, is_active, is_superuser) VALUES (?, ?, ?, ?, ?)", (email, name.lower().replace(" ", ""), pw, 1, is_super))
                        elif "is_active" in cols:
                            cur.execute("INSERT INTO users (email, username, hashed_password, is_active) VALUES (?, ?, ?, ?)", (email, name.lower().replace(" ", ""), pw, 1))
                        else:
                            cur.execute("INSERT INTO users (email, username, hashed_password) VALUES (?, ?, ?)", (email, name.lower().replace(" ", ""), pw))
                    else:
                        cur.execute("INSERT INTO users (email, hashed_password) VALUES (?, ?)", (email, pw))
                elif "password_hash" in cols:
                    cur.execute("INSERT INTO users (email, name, password_hash, role, created_at, failed_attempts) VALUES (?, ?, ?, ?, ?, ?)", 
                                (email, name, pw, rname, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), 0))
                cur.execute("SELECT id FROM users WHERE email = ?", (email,))
                row = cur.fetchone()
            
            if row and "user_roles" in [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
                uid = row[0]
                cur.execute("SELECT id FROM roles WHERE name = ?", (rname,))
                role_res = cur.fetchone()
                if role_res:
                    rid = role_res[0]
                    cur.execute("INSERT OR IGNORE INTO user_roles (user_id, role_id) VALUES (?, ?)", (uid, rid))

        conn.commit()

        # Seed Symptoms
        for sym in symptoms_list:
            cur.execute("INSERT OR IGNORE INTO symptoms (name) VALUES (?)", (sym.strip().lower(),))
        
        conn.commit()

        # Seed Diseases & Metadata
        for _, row in desc_df.iterrows():
            dname = str(row["Disease"]).strip()
            ddesc = str(row["Description"]).strip()
            cur.execute("INSERT OR IGNORE INTO diseases (name, description) VALUES (?, ?)", (dname, ddesc))
            
            cur.execute("SELECT id FROM diseases WHERE name = ?", (dname,))
            res = cur.fetchone()
            if res:
                did = res[0]
                
                # Fetch meds, diet, workout, precautions
                meds = med_df[med_df["Disease"].str.strip().str.lower() == dname.lower()]
                meds_list = eval(meds.iloc[0]["Medication"]) if not meds.empty and isinstance(meds.iloc[0]["Medication"], str) and meds.iloc[0]["Medication"].startswith("[") else ([meds.iloc[0]["Medication"]] if not meds.empty else [])

                diets = diets_df[diets_df["Disease"].str.strip().str.lower() == dname.lower()]
                diets_list = eval(diets.iloc[0]["Diet"]) if not diets.empty and isinstance(diets.iloc[0]["Diet"], str) and diets.iloc[0]["Diet"].startswith("[") else ([diets.iloc[0]["Diet"]] if not diets.empty else [])

                workouts = workout_df[workout_df["Disease"].str.strip().str.lower() == dname.lower()]
                workouts_list = [workouts.iloc[0]["Workouts"]] if not workouts.empty else []

                precs = prec_df[prec_df["Disease"].str.strip().str.lower() == dname.lower()]
                precs_list = []
                if not precs.empty:
                    for col in ["Precaution_1", "Precaution_2", "Precaution_3", "Precaution_4"]:
                        val = precs.iloc[0][col]
                        if pd.notna(val) and str(val).strip():
                            precs_list.append(str(val).strip())

                cur.execute("""
                    INSERT OR REPLACE INTO disease_metadata (disease_id, medications, diets, workouts, precautions)
                    VALUES (?, ?, ?, ?, ?)
                """, (did, json.dumps(meds_list), json.dumps(diets_list), json.dumps(workouts_list), json.dumps(precs_list)))

        conn.commit()

        # Seed Predictions & Analytics History
        diseases_sample = list(desc_df["Disease"].values[:15])
        now = datetime.now()
        ph_cols = [info[1] for info in cur.execute("PRAGMA table_info(prediction_history)").fetchall()]
        
        for i in range(120):
            d = random.choice(diseases_sample)
            conf = round(random.uniform(75.0, 98.5), 1)
            risk = "high" if conf > 85 else ("medium" if conf > 60 else "low")
            created = now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            sample_syms = random.sample(symptoms_list[:30], k=random.randint(2, 5))
            
            if "symptoms_input" in ph_cols:
                cur.execute("""
                    INSERT INTO prediction_history (user_id, symptoms_input, predicted_disease, confidence, risk_level, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (3, json.dumps(sample_syms), d, conf, risk, created.strftime("%Y-%m-%d %H:%M:%S")))
            elif "symptoms" in ph_cols:
                cur.execute("""
                    INSERT INTO prediction_history (user_id, symptoms, prediction, confidence, risk_level, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (3, json.dumps(sample_syms), d, conf, risk, created.strftime("%Y-%m-%d %H:%M:%S")))

            pred_cols = [info[1] for info in cur.execute("PRAGMA table_info(predictions)").fetchall()]
            if "patient_id" in pred_cols:
                cur.execute("""
                    INSERT INTO predictions (patient_id, input_vector, predicted_disease, probabilities, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (1, json.dumps({"symptoms": sample_syms}), d, json.dumps({d: conf/100.0}), created.strftime("%Y-%m-%d %H:%M:%S")))

        # Seed Model Version
        mv_cols = [info[1] for info in cur.execute("PRAGMA table_info(model_versions)").fetchall()]
        if "metrics" in mv_cols:
            cur.execute("""
                INSERT INTO model_versions (name, version, metrics, path)
                VALUES (?, ?, ?, ?)
            """, ("HistGradientBoostingClassifier", "v1.0.0", json.dumps({"accuracy": 0.907188, "macro_f1": 0.897674}), "backend/ml/best_model.pkl"))
        elif "metadata" in mv_cols:
            cur.execute("""
                INSERT INTO model_versions (name, version, description, metadata)
                VALUES (?, ?, ?, ?)
            """, ("HistGradientBoostingClassifier", "v1.0.0", "Main disease classifier", json.dumps({"accuracy": 0.907188, "macro_f1": 0.897674, "path": "backend/ml/best_model.pkl"})))

        conn.commit()
        conn.close()
        print(f"[DB SEEDER] Successfully seeded {db_path}")

if __name__ == "__main__":
    seed_database()
