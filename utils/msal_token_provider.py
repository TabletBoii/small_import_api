import json
import os
import time
from pathlib import Path
from typing import Optional

from msal import ConfidentialClientApplication


class PBITokenProvider:
    def __init__(
        self,
        app: ConfidentialClientApplication,
        scopes: list[str],
        cache_file: str = "tokens/pbi_token.json",
        expiry_buffer: int = 300,
    ):
        self.app = app
        self.scopes = scopes
        self.cache_path = Path(cache_file)
        self.expiry_buffer = expiry_buffer
        if self.cache_path.parent != Path():
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def get_token(self) -> str:
        data = self._load_cache()
        if data and self._is_valid(data):
            return data["access_token"]

        new_data = self._acquire_new_token()
        self._save_cache(new_data)
        return new_data["access_token"]

    def _acquire_new_token(self) -> dict:
        result = self.app.acquire_token_for_client(scopes=self.scopes)
        if "access_token" not in result:
            raise ValueError(f"Could not acquire PBI access token: {result}")
        result["expires_at"] = time.time() + int(result.get("expires_in", 0))
        return result

    def _load_cache(self) -> Optional[dict]:
        if not self.cache_path.is_file():
            return None
        try:
            with self.cache_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            try:
                self.cache_path.unlink(missing_ok=True)
            except OSError:
                pass
            return None

    def _save_cache(self, data: dict) -> None:
        tmp = self.cache_path.with_suffix(self.cache_path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f)
            f.flush()
            os.fsync(f.fileno())
        if os.name == "posix":
            os.chmod(tmp, 0o600)
        os.replace(tmp, self.cache_path)

    def _is_valid(self, data: dict) -> bool:
        exp = data.get("expires_at")
        return isinstance(exp, (int, float)) and time.time() < exp - self.expiry_buffer
