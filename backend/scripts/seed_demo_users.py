"""
Seed Default Demo Accounts for Admin, Analyst, and Patient (User)
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.utils.db import db
from backend.models import User, UserProfile, HealthProfile, PredictionHistory
from backend.utils.security import hash_password

def seed_demo_accounts():
    app = create_app()
    with app.app_context():
        # 1. Admin Account
        admin = User.query.filter_by(email="admin@healthai.com").first()
        if not admin:
            admin = User(
                name="Dr. Administrator",
                email="admin@healthai.com",
                password_hash=hash_password("AdminPassword123!"),
                role="admin",
                status="active"
            )
            db.session.add(admin)
            print("Created demo Admin: admin@healthai.com / AdminPassword123!")

        # 2. Analyst Account
        analyst = User.query.filter_by(email="analyst@healthai.com").first()
        if not analyst:
            analyst = User(
                name="Clinical Data Analyst",
                email="analyst@healthai.com",
                password_hash=hash_password("AnalystPassword123!"),
                role="analyst",
                status="active"
            )
            db.session.add(analyst)
            print("Created demo Analyst: analyst@healthai.com / AnalystPassword123!")

        # 3. Patient Account
        patient = User.query.filter_by(email="patient@healthai.com").first()
        if not patient:
            patient = User(
                name="Jane Doe (Patient)",
                email="patient@healthai.com",
                password_hash=hash_password("PatientPassword123!"),
                role="user",
                status="active"
            )
            db.session.add(patient)
            db.session.commit()

            # Seed patient health profile
            hp = HealthProfile(
                user_id=patient.id,
                age=29,
                gender="female",
                allergies=["Pollen", "Penicillin"],
                existing_conditions=["Mild Asthma"],
                current_medications=["Albuterol Inhaler"]
            )
            db.session.add(hp)

            # Seed sample prediction history for patient
            pred = PredictionHistory(
                user_id=patient.id,
                symptoms_input=["anxiety and nervousness", "shortness of breath", "dizziness"],
                predicted_disease="Panic disorder",
                confidence=94.5,
                risk_level="high",
                top_candidates=[
                    {"disease": "Panic disorder", "confidence": 94.5},
                    {"disease": "Asthma", "confidence": 3.2},
                    {"disease": "Migraine", "confidence": 1.1}
                ],
                disease_symptoms=["anxiety and nervousness", "shortness of breath", "dizziness"],
                description="Panic disorder involves sudden episodes of intense fear accompanied by physical symptoms.",
                medicines=["SSRIs (Sertraline)", "Benzodiazepines", "Cognitive Behavioral Therapy"],
                advice=["Practice slow rhythmic breathing", "Avoid high caffeine", "Maintain regular sleep"],
                diet=["Balanced hydration", "High magnesium foods", "Chamomile tea"],
                workout=["Deep diaphragmatic breathing", "Gentle yoga walking"]
            )
            db.session.add(pred)
            print("Created demo Patient: patient@healthai.com / PatientPassword123!")

        db.session.commit()
        print("Demo accounts seeding complete.")

if __name__ == "__main__":
    seed_demo_accounts()
