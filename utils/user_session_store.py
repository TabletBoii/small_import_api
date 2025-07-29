from uuid import uuid4
import json, os


class UserSessionStore:
    def __init__(self, folder: str = "sessions"):
        os.makedirs(folder, exist_ok=True)
        self.folder = folder

    def create(self, email: str, id_token: str, access_token: str, expires_at: float) -> str:
        session_id = str(uuid4())
        data = {
            "email":        email,
            "id_token":     id_token,
            "access_token": access_token,
            "expires_at":   expires_at,
        }
        with open(f"{self.folder}/{session_id}.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
        return session_id

    def read(self, session_id: str) -> dict | None:
        path = f"{self.folder}/{session_id}.json"
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            os.remove(path)
            return None

    def delete(self, session_id: str):
        try:
            os.remove(f"{self.folder}/{session_id}.json")
        except FileNotFoundError:
            pass
