"""
HealthAI - Activity Tracking & Notification Utility
"""
from datetime import datetime
from backend.utils.db import db
from backend.models import UserActivity, Notification

def track_activity(user_id: int, activity_type: str, details: dict = None) -> UserActivity:
    """Records a genuine user action event in the database."""
    if not user_id:
        return None
    try:
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type.upper(),
            details=details or {},
            created_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        return activity
    except Exception as err:
        db.session.rollback()
        print(f"[ACTIVITY TRACKER WARN] Failed to log activity: {err}")
        return None

def create_notification(user_id: int, title: str, message: str) -> Notification:
    """Generates a system notification for the user."""
    if not user_id:
        return None
    try:
        note = Notification(
            user_id=user_id,
            title=title,
            message=message,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(note)
        db.session.commit()
        return note
    except Exception as err:
        db.session.rollback()
        print(f"[NOTIFICATION WARN] Failed to create notification: {err}")
        return None
