"""Create or update an administrator account from the command line.

Usage:
    python -m backend.scripts.create_admin --email admin@example.com
The command securely prompts for the password unless --password is supplied.
"""
import argparse
import getpass
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import create_app
from backend.models import User
from backend.utils.db import db
from backend.utils.security import hash_password


def main():
    parser = argparse.ArgumentParser(description="Create or update an administrator account.")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="System Administrator")
    parser.add_argument("--password", help="Password (omit to enter it securely at a prompt)")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Administrator password: ")
    if len(password) < 8:
        parser.error("Administrator password must contain at least 8 characters.")

    email = args.email.strip().lower()
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user is None:
            user = User(name=args.name.strip(), email=email, role="admin", status="active")
            db.session.add(user)
        else:
            user.name = args.name.strip()
            user.role = "admin"
            user.status = "active"

        user.password_hash = hash_password(password)
        db.session.commit()
        print(f"Administrator account is ready: {email}")


if __name__ == "__main__":
    main()
