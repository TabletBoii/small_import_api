from uuid import uuid4
import json, os


class UserSessionStore:
    def __init__(self, folder: str = "sessions"):
        os.makedirs(folder, exist_ok=True)
        self.folder = folder

    def _path(self, session_id: str) -> str:
        return os.path.join(self.folder, f"{session_id}.json")

    def create(self, email: str, id_token: str, access_token: str, refresh_token: str, expires_at: float) -> str:
        session_id = str(uuid4())
        data = {
            "email":        email,
            "id_token":     id_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at":   expires_at,
        }
        with open(self._path(session_id), "w", encoding="utf-8") as f:
            json.dump(data, f)
        return session_id

    def read(self, session_id: str) -> dict | None:
        if not os.path.isfile(self._path(session_id)):
            return None
        try:
            with open(self._path(session_id), "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            os.remove(self._path(session_id))
            return None

    def delete(self, session_id: str):
        try:
            os.remove(self._path(session_id))
        except FileNotFoundError:
            pass

    def update(self, session_id: str, **kwargs) -> None:
        if not os.path.exists(self._path(session_id)):
            return
        try:
            with open(self._path(session_id), "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        data.update(kwargs)
        with open(self._path(session_id), "w", encoding="utf-8") as f:
            json.dump(data, f)
