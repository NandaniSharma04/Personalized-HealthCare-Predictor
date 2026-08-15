class UserRepository:
    def get_by_username(self, username: str) -> dict | None:
        # Placeholder: query DB
        if username == "admin":
            return {"username": "admin", "hashed_password": "", "roles": ["ADMIN"]}
        return None
