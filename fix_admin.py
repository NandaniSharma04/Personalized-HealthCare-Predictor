"""
One-time script to reactivate a suspended admin account.
Run from the project root: python fix_admin.py
"""
from backend.app import app
from backend.utils.db import db
from backend.models import User

with app.app_context():
    admin = User.query.filter_by(email="admin@gmail.com").first()

    if not admin:
        print("No user found with email admin@gmail.com")
    else:
        print(f"Found user: {admin.name} | current status: {admin.status}")
        admin.status = "active"
        admin.failed_attempts = 0
        admin.locked_until = None
        db.session.commit()
        print("Done. Account status is now: active")
