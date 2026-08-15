"""Seed development data into the FastAPI backend database.

Creates roles (`admin`, `analyst`, `user`), imports users from `data/users.json`,
loads symptoms and disease metadata from `backend/ml/` artifacts, creates sample
patients and predictions, and writes a few CF interactions.

Run: `python backend_fastapi/scripts/seed_dev_data.py`
"""
from pathlib import Path
import json
from app.db.session import SessionLocal, engine
from app.models import Base, Role, User, Symptom, Disease, DiseaseMetadata, Patient, PatientSymptom, Prediction
from app.core.security import get_password_hash


def main():
    repo_root = Path(__file__).resolve().parents[3]
    print("Seeding development data...")

    # create tables if needed
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Roles
        roles = {r.name: r for r in db.query(Role).all()}
        for name in ("admin", "analyst", "user"):
            if name not in roles:
                r = Role(name=name)
                db.add(r)
        db.commit()

        roles = {r.name: r for r in db.query(Role).all()}

        # Users from data/users.json
        users_file = repo_root / "data" / "users.json"
        if users_file.exists():
            users_data = json.loads(users_file.read_text(encoding="utf-8"))
            for i, u in enumerate(users_data):
                existing = db.query(User).filter(User.email == u.get("email")).first()
                if existing:
                    continue
                hashed = get_password_hash(u.get("password", "password"))
                user = User(email=u.get("email"), name=u.get("name"), hashed_password=hashed)
                # first user: admin+analyst
                if i == 0:
                    user.roles = [roles["admin"], roles["analyst"]]
                else:
                    user.roles = [roles["user"]]
                db.add(user)
            db.commit()

        # Symptoms
        sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
        if sym_file.exists():
            syms = json.loads(sym_file.read_text(encoding="utf-8"))
            for s in syms:
                if not db.query(Symptom).filter(Symptom.name == s).first():
                    db.add(Symptom(name=s))
            db.commit()

        # Diseases and metadata
        disease_file = repo_root / "backend" / "ml" / "disease_info.json"
        if disease_file.exists():
            data = json.loads(disease_file.read_text(encoding="utf-8"))
            for name, info in data.items():
                d = db.query(Disease).filter(Disease.name == name).first()
                if not d:
                    d = Disease(name=name, description=info.get("Description"))
                    db.add(d)
                    db.flush()
                # metadata
                meta = db.query(DiseaseMetadata).filter(DiseaseMetadata.disease_id == d.id).first()
                if not meta:
                    meta = DiseaseMetadata(disease_id=d.id, medications=info.get("Medication"), diets=info.get("Diets"), workouts=info.get("Workouts"), precautions=info.get("Precautions"), extra={})
                    db.add(meta)
            db.commit()

        # Create a Patient for each user and a sample prediction
        users = db.query(User).all()
        for u in users:
            patient = db.query(Patient).filter(Patient.user_id == u.id).first()
            if not patient:
                patient = Patient(user_id=u.id, age=30)
                db.add(patient)
                db.flush()
                # add a sample symptom and a prediction if possible
                first_sym = db.query(Symptom).first()
                if first_sym:
                    db.add(PatientSymptom(patient_id=patient.id, symptom_id=first_sym.id, value=1))
                # sample prediction row
                db.add(Prediction(patient_id=patient.id, input_vector={"example": True}, predicted_disease="common cold", probabilities={"common cold": 0.8}))
        db.commit()

        # Seed a few CF interactions (written to interactions.json by cf_service)
        interactions_path = repo_root / "backend" / "ml" / "interactions.json"
        if not interactions_path.exists():
            sample = []
            for u in db.query(User).limit(4).all():
                sample.append({"user": str(u.id), "item": "common cold", "rating": 5.0})
                sample.append({"user": str(u.id), "item": "flu", "rating": 4.0})
            interactions_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")

        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
"""Seed development data from existing backend/ml artifacts into the DB.

This script reads `backend/ml/symptom_list.json`, `backend/ml/disease_info.json` and writes
rows into `diseases`, `symptoms`, and `disease_metadata` tables.
"""
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models import Disease, Symptom, DiseaseMetadata


def main():
    repo_root = Path(__file__).resolve().parents[2]
    sym_file = repo_root / "backend" / "ml" / "symptom_list.json"
    disease_file = repo_root / "backend" / "ml" / "disease_info.json"
    db = SessionLocal()
    try:
        symptoms = json.loads(sym_file.read_text(encoding="utf-8"))
        for s in symptoms:
            if not db.query(Symptom).filter(Symptom.name == s).first():
                db.add(Symptom(name=s))
        db.commit()

        disease_info = json.loads(disease_file.read_text(encoding="utf-8"))
        for d, info in disease_info.items():
            disease = db.query(Disease).filter(Disease.name == d).first()
            if not disease:
                disease = Disease(name=d, description=info.get("Description") or "")
                db.add(disease)
                db.commit()
                db.refresh(disease)
            meta = db.query(DiseaseMetadata).filter(DiseaseMetadata.disease_id == disease.id).first()
            if not meta:
                meta = DiseaseMetadata(disease_id=disease.id, medications=info.get("Medication"), diets=None, workouts=info.get("Workouts"), precautions=info.get("Precautions"), extra=None)
                db.add(meta)
        db.commit()
        print("Seeding complete")
    finally:
        db.close()


if __name__ == "__main__":
    main()
