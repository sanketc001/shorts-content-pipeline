"""YouTube Data API v3 publishing service."""

import httpx
from auth.oauth_manager import get_token


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"


def _get_auth_header() -> dict:
    token = get_token("youtube")
    if not token:
        raise RuntimeError("Not connected to YouTube")
    return {"Authorization": f"Bearer {token['access_token']}"}


async def get_channel_info() -> dict:
    """Get the authenticated user's YouTube channel info."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{YOUTUBE_API_BASE}/channels",
            params={"part": "snippet,statistics", "mine": "true"},
            headers=_get_auth_header(),
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("items"):
            channel = data["items"][0]
            return {
                "id": channel["id"],
                "title": channel["snippet"]["title"],
                "thumbnail": channel["snippet"]["thumbnails"]["default"]["url"],
                "subscribers": channel["statistics"].get("subscriberCount", "0"),
            }
    return {}


async def upload_video(
    video_bytes: bytes,
    title: str,
    description: str,
    tags: list[str] | None = None,
    privacy: str = "private",
    thumbnail_bytes: bytes | None = None,
) -> dict:
    """Upload a video to YouTube."""
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    async with httpx.AsyncClient(timeout=600.0) as client:
        # Upload video
        resp = await client.post(
            YOUTUBE_UPLOAD_URL,
            params={"uploadType": "multipart", "part": "snippet,status"},
            headers=_get_auth_header(),
            files={
                "metadata": ("metadata.json", __import__("json").dumps(metadata), "application/json"),
                "media": ("video.mp4", video_bytes, "video/*"),
            },
        )
        resp.raise_for_status()
        video_data = resp.json()
        video_id = video_data["id"]

        # Upload thumbnail if provided
        if thumbnail_bytes:
            await client.post(
                f"{YOUTUBE_API_BASE}/thumbnails/set",
                params={"videoId": video_id},
                headers=_get_auth_header(),
                files={"media": ("thumbnail.png", thumbnail_bytes, "image/png")},
            )

        return {"video_id": video_id, "url": f"https://youtube.com/watch?v={video_id}"}


async def update_video(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update video metadata."""
    body: dict = {"id": video_id, "snippet": {}}
    if title:
        body["snippet"]["title"] = title
    if description:
        body["snippet"]["description"] = description
    if tags:
        body["snippet"]["tags"] = tags

    async with httpx.AsyncClient() as client:
        resp = await client.put(
            f"{YOUTUBE_API_BASE}/videos",
            params={"part": "snippet"},
            headers={**_get_auth_header(), "Content-Type": "application/json"},
            json=body,
        )
        resp.raise_for_status()
        return resp.json()
