"""Seed the database with realistic demo data for dashboards and workflows."""
from sqlalchemy import create_engine, text
from pathlib import Path
from ..app.core.config import settings
import json


def seed():
    engine = create_engine(settings.DATABASE_URL)
    with engine.begin() as conn:
        # Roles
        conn.execute(text("INSERT INTO roles (name, description) VALUES (:n,:d) ON CONFLICT (name) DO NOTHING"),
                     [dict(n='USER', d='Regular user'), dict(n='ADMIN', d='Administrator'), dict(n='ANALYST', d='Analyst')])

        # Users
        users = [
            dict(username='alice', email='alice@example.com', hashed_password='hashed_pw_alice'),
            dict(username='bob', email='bob@example.com', hashed_password='hashed_pw_bob'),
            dict(username='carol', email='carol@example.com', hashed_password='hashed_pw_carol')
        ]
        for u in users:
            conn.execute(text("INSERT INTO users (username, email, hashed_password) VALUES (:username,:email,:hashed_password) ON CONFLICT (username) DO NOTHING"), u)

        # Assign roles
        conn.execute(text("INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username = :u AND r.name = :r ON CONFLICT DO NOTHING"), dict(u='alice', r='USER'))
        conn.execute(text("INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username = :u AND r.name = :r ON CONFLICT DO NOTHING"), dict(u='bob', r='ANALYST'))
        conn.execute(text("INSERT INTO user_roles (user_id, role_id) SELECT u.id, r.id FROM users u, roles r WHERE u.username = :u AND r.name = :r ON CONFLICT DO NOTHING"), dict(u='carol', r='ADMIN'))

        # Symptoms and diseases
        symptoms = ['Fever', 'Cough', 'Sore throat', 'Runny nose', 'Headache', 'Fatigue']
        for s in symptoms:
            conn.execute(text("INSERT INTO symptoms (name, description) VALUES (:n, :d) ON CONFLICT (name) DO NOTHING"), dict(n=s, d=f"Symptom: {s}"))

        diseases = [
            dict(name='Common Cold', description='Viral upper respiratory infection', prevalence=0.3),
            dict(name='Influenza', description='Flu virus infection', prevalence=0.05),
            dict(name='Migraine', description='Neurological headache disorder', prevalence=0.1)
        ]
        for d in diseases:
            conn.execute(text("INSERT INTO diseases (name, description, prevalence) VALUES (:name, :description, :prevalence) ON CONFLICT (name) DO NOTHING"), d)

        # Link disease-symptoms with weights
        conn.execute(text("INSERT INTO disease_symptoms (disease_id, symptom_id, weight) SELECT d.id, s.id, 0.8 FROM diseases d, symptoms s WHERE d.name = 'Influenza' AND s.name = 'Fever' ON CONFLICT DO NOTHING"))
        conn.execute(text("INSERT INTO disease_symptoms (disease_id, symptom_id, weight) SELECT d.id, s.id, 0.6 FROM diseases d, symptoms s WHERE d.name = 'Common Cold' AND s.name = 'Runny nose' ON CONFLICT DO NOTHING"))

        # Medicines
        meds = [dict(name='Paracetamol', description='Analgesic/antipyretic'), dict(name='Ibuprofen', description='NSAID')]
        for m in meds:
            conn.execute(text("INSERT INTO medicines (name, description) VALUES (:name, :description) ON CONFLICT (name) DO NOTHING"), m)

        # Model versions and metrics
        conn.execute(text("INSERT INTO model_versions (name, version, description) VALUES ('baseline_rf', 'v1', 'RandomForest baseline') ON CONFLICT DO NOTHING"))
        conn.execute(text("INSERT INTO model_metrics (model_version_id, metric_name, metric_value) SELECT mv.id, 'accuracy', 0.78 FROM model_versions mv WHERE mv.name='baseline_rf' ON CONFLICT DO NOTHING"))

        # Sample predictions
        conn.execute(text("INSERT INTO prediction_history (user_id, model_version_id, input_features, prediction, confidence) SELECT u.id, mv.id, :features, :prediction, :conf FROM users u, model_versions mv WHERE u.username = 'alice' AND mv.name='baseline_rf'"),
                     dict(features=json.dumps({'symptoms': ['Fever','Cough']}), prediction=json.dumps({'disease':'Influenza'}), conf=0.86))

        # Recommendations and interactions
        conn.execute(text("INSERT INTO recommendations (user_id, rec_type, source, model_version_id, score) SELECT u.id, 'personal', 'content-based', mv.id, 0.9 FROM users u, model_versions mv WHERE u.username='alice' AND mv.name='baseline_rf'"))
        conn.execute(text("INSERT INTO user_interactions (user_id, interaction_type, target_type, metadata) SELECT u.id, 'search', 'symptom_search', jsonb_build_object('query','fever') FROM users u WHERE u.username='alice'"))

        print("Seeding complete")


if __name__ == '__main__':
    seed()
