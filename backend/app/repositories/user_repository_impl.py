from sqlalchemy.orm import Session
from ..models.user_models import UserProfile, MedicalProfile, Notification, SavedItem
from ..models.auth_models import User


class UserRepositoryImpl:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_profile(self, user_id: int) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def upsert_profile(self, user_id: int, data: dict) -> UserProfile:
        p = self.get_profile(user_id)
        if not p:
            p = UserProfile(user_id=user_id, **data)
            self.db.add(p)
        else:
            for k, v in data.items():
                setattr(p, k, v)
        self.db.commit()
        self.db.refresh(p)
        return p

    def get_medical_profile(self, user_id: int) -> MedicalProfile | None:
        return self.db.query(MedicalProfile).filter(MedicalProfile.user_id == user_id).first()

    def upsert_medical_profile(self, user_id: int, data: dict) -> MedicalProfile:
        p = self.get_medical_profile(user_id)
        if not p:
            p = MedicalProfile(user_id=user_id, **data)
            self.db.add(p)
        else:
            for k, v in data.items():
                setattr(p, k, v)
        self.db.commit()
        self.db.refresh(p)
        return p

    def list_notifications(self, user_id: int):
        return self.db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

    def mark_notification_read(self, notification_id: int, user_id: int):
        n = self.db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
        if n:
            n.is_read = True
            self.db.commit()
        return n

    # Additional listing methods for user dashboard and histories
    def list_prediction_history(self, user_id: int, limit: int = 50):
        res = self.db.execute(
            "SELECT id, model_version_id, input_features, prediction, confidence, created_at FROM prediction_history WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim",
            dict(uid=user_id, lim=limit),
        )
        return [dict(row) for row in res.fetchall()]

    def list_recommendations(self, user_id: int, limit: int = 20):
        res = self.db.execute(
            "SELECT id, rec_type, source, score, metadata, created_at FROM recommendations WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim",
            dict(uid=user_id, lim=limit),
        )
        return [dict(row) for row in res.fetchall()]

    def list_medical_records(self, user_id: int, limit: int = 50):
        res = self.db.execute(
            "SELECT id, record_type, record, created_at FROM medical_records WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim",
            dict(uid=user_id, lim=limit),
        )
        return [dict(row) for row in res.fetchall()]

    def list_activity(self, user_id: int, limit: int = 100):
        res = self.db.execute(
            "SELECT id, interaction_type, target_type, target_id, metadata, created_at FROM user_interactions WHERE user_id = :uid ORDER BY created_at DESC LIMIT :lim",
            dict(uid=user_id, lim=limit),
        )
        return [dict(row) for row in res.fetchall()]

    def list_saved_items(self, user_id: int):
        return self.db.query(SavedItem).filter(SavedItem.user_id == user_id).order_by(SavedItem.created_at.desc()).all()

    def add_feedback(self, user_id: int, target_type: str, target_id: int | None, rating: int | None, comment: str | None):
        res = self.db.execute(
            "INSERT INTO feedback (user_id, target_type, target_id, rating, comment) VALUES (:u,:t,:i,:r,:c) RETURNING id",
            dict(u=user_id, t=target_type, i=target_id, r=rating, c=comment),
        )
        fid = res.fetchone()[0]
        self.db.commit()
        return fid

