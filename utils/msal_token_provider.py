import json
import os
import time
from typing import Optional

from msal import ConfidentialClientApplication


class PBITokenProvider:
    def __init__(
        self,
        app: ConfidentialClientApplication,
        scopes: list[str],
        cache_file: str = "pbi_token_cache.json",
        expiry_buffer: int = 300,
    ):
        self.app = app
        self.scopes = scopes
        self.cache_file = cache_file
        self.expiry_buffer = expiry_buffer

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

        expires_in = int(result.get("expires_in", 0))
        result["expires_at"] = time.time() + expires_in
        return result

    def _load_cache(self) -> Optional[dict]:
        if not os.path.isfile(self.cache_file):
            return None
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            try:
                os.remove(self.cache_file)
            except OSError:
                pass
            return None

    def _save_cache(self, data: dict) -> None:
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _is_valid(self, data: dict) -> bool:
        expires_at = data.get("expires_at")
        if not isinstance(expires_at, (int, float)):
            return False
        return time.time() < expires_at - self.expiry_buffer
