"""OAuth authentication routes for YouTube, Instagram, LinkedIn."""

import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from config import settings
from auth.oauth_config import OAUTH_CONFIGS
from auth.oauth_manager import store_token, remove_token, get_all_status, get_token

router = APIRouter()

# In-memory state store for CSRF protection
_oauth_states: dict[str, str] = {}


@router.get("/status")
async def auth_status():
    """Get connection status for all platforms."""
    return get_all_status()


@router.get("/{platform}/login")
async def login(platform: str):
    """Initiate OAuth flow for a platform."""
    config = OAUTH_CONFIGS.get(platform)
    if not config:
        raise HTTPException(400, f"Unknown platform: {platform}")

    if not config["client_id"]:
        raise HTTPException(
            400,
            f"OAuth not configured for {platform}. Set the client ID and secret in .env",
        )

    state = secrets.token_urlsafe(32)
    _oauth_states[state] = platform

    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }

    auth_url = f"{config['authorize_url']}?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/{platform}/callback")
async def callback(platform: str, code: str = "", state: str = "", error: str = ""):
    """Handle OAuth callback."""
    if error:
        return RedirectResponse(f"{settings.frontend_url}?auth_error={error}")

    # Verify state
    stored_platform = _oauth_states.pop(state, None)
    if stored_platform != platform:
        raise HTTPException(400, "Invalid OAuth state")

    config = OAUTH_CONFIGS.get(platform)
    if not config:
        raise HTTPException(400, f"Unknown platform: {platform}")

    # Exchange code for token
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config["token_url"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config["redirect_uri"],
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
            },
        )

        if resp.status_code != 200:
            return RedirectResponse(
                f"{settings.frontend_url}?auth_error=token_exchange_failed"
            )

        token_data = resp.json()

        # Calculate expiry
        if "expires_in" in token_data:
            import time
            token_data["expires_at"] = time.time() + token_data["expires_in"]

        store_token(platform, token_data)

    return RedirectResponse(f"{settings.frontend_url}?auth_success={platform}")


@router.post("/{platform}/disconnect")
async def disconnect(platform: str):
    """Disconnect a platform."""
    remove_token(platform)
    return {"status": "disconnected", "platform": platform}


@router.get("/{platform}/token")
async def get_platform_token(platform: str):
    """Get the stored token for a platform (internal use)."""
    token = get_token(platform)
    if not token:
        raise HTTPException(404, f"Not connected to {platform}")
    return {"connected": True, "has_refresh": "refresh_token" in token}
