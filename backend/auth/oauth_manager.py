"""OAuth token management - storage, refresh, and validation."""

import json
import time
from pathlib import Path

import httpx

from config import settings

_TOKEN_FILE = Path(settings.output_dir) / ".tokens.json"


def _load_tokens() -> dict:
    if _TOKEN_FILE.exists():
        return json.loads(_TOKEN_FILE.read_text())
    return {}


def _save_tokens(tokens: dict):
    _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    _TOKEN_FILE.write_text(json.dumps(tokens, indent=2))


def store_token(platform: str, token_data: dict):
    tokens = _load_tokens()
    token_data["stored_at"] = time.time()
    tokens[platform] = token_data
    _save_tokens(tokens)


def get_token(platform: str) -> dict | None:
    tokens = _load_tokens()
    return tokens.get(platform)


def remove_token(platform: str):
    tokens = _load_tokens()
    tokens.pop(platform, None)
    _save_tokens(tokens)


def is_connected(platform: str) -> bool:
    token = get_token(platform)
    if not token:
        return False
    # Check if token has expired
    expires_at = token.get("expires_at", 0)
    if expires_at and time.time() > expires_at:
        return False
    return True


async def refresh_token(platform: str, token_url: str, client_id: str, client_secret: str) -> dict | None:
    """Attempt to refresh an expired token."""
    token = get_token(platform)
    if not token or "refresh_token" not in token:
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
                "client_id": client_id,
                "client_secret": client_secret,
            },
        )
        if resp.status_code == 200:
            new_token = resp.json()
            # Preserve refresh token if not returned
            if "refresh_token" not in new_token:
                new_token["refresh_token"] = token["refresh_token"]
            if "expires_in" in new_token:
                new_token["expires_at"] = time.time() + new_token["expires_in"]
            store_token(platform, new_token)
            return new_token
    return None


def get_all_status() -> dict:
    return {
        "youtube": is_connected("youtube"),
        "instagram": is_connected("instagram"),
        "linkedin": is_connected("linkedin"),
    }
