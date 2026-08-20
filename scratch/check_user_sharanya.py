import sys
from pathlib import Path

PROJECT_ROOT = Path(r"c:\Users\G SAI SHARANYA\OneDrive\Desktop\Personalized-HealthCare-Predictor-main")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.models import User, PredictionHistory, HealthProfile, db

app = create_app()

with app.app_context():
    users = User.query.all()
    print("ALL USERS IN DB:")
    for u in users:
        print(f"ID: {u.id} | Name: '{u.name}' | Email: '{u.email}' | Role: '{u.role}' | Password Hash Exists: {bool(u.password_hash)}")
    
    # Check if sharanyagummadavelli@gmail.com exists
    u = User.query.filter((User.email == 'sharanyagummadavelli@gmail.com') | (User.name == 'sharanya')).first()
    if u:
        print(f"\nFound target user: ID={u.id}, Name={u.name}, Email={u.email}")
    else:
        print("\nUser 'sharanya' not found in database. Creating default account...")
        new_u = User(name="sharanya", email="sharanyagummadavelli@gmail.com", role="user")
        new_u.set_password("123456")
        db.session.add(new_u)
        db.session.commit()
        print("Created user 'sharanya' (Email: sharanyagummadavelli@gmail.com, Pass: 123456)")
