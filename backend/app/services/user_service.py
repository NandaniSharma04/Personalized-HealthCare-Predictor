from sqlalchemy.orm import Session
from ..repositories.user_repository_impl import UserRepositoryImpl


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepositoryImpl(db)

    def get_profile(self, user_id: int):
        return self.repo.get_profile(user_id)

    def update_profile(self, user_id: int, data: dict):
        return self.repo.upsert_profile(user_id, data)

    def get_medical_profile(self, user_id: int):
        return self.repo.get_medical_profile(user_id)

    def update_medical_profile(self, user_id: int, data: dict):
        return self.repo.upsert_medical_profile(user_id, data)

    def list_notifications(self, user_id: int):
        return self.repo.list_notifications(user_id)

    def mark_notification_read(self, notification_id: int, user_id: int):
        return self.repo.mark_notification_read(notification_id, user_id)

    def get_prediction_history(self, user_id: int, limit: int = 50):
        return self.repo.list_prediction_history(user_id, limit)

    def get_recommendations(self, user_id: int, limit: int = 20):
        return self.repo.list_recommendations(user_id, limit)

    def get_medical_records(self, user_id: int, limit: int = 50):
        return self.repo.list_medical_records(user_id, limit)

    def get_activity(self, user_id: int, limit: int = 100):
        return self.repo.list_activity(user_id, limit)

    def get_saved_items(self, user_id: int):
        return self.repo.list_saved_items(user_id)

    def submit_feedback(self, user_id: int, target_type: str, target_id: int | None, rating: int | None, comment: str | None):
        return self.repo.add_feedback(user_id, target_type, target_id, rating, comment)

