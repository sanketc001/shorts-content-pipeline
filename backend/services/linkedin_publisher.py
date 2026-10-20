"""LinkedIn API publishing service."""

import httpx
from auth.oauth_manager import get_token

LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_REST_BASE = "https://api.linkedin.com/rest"


def _get_auth_headers() -> dict:
    token = get_token("linkedin")
    if not token:
        raise RuntimeError("Not connected to LinkedIn")
    return {
        "Authorization": f"Bearer {token['access_token']}",
        "LinkedIn-Version": "202401",
        "X-Restli-Protocol-Version": "2.0.0",
    }


async def get_profile() -> dict:
    """Get the authenticated user's LinkedIn profile."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{LINKEDIN_API_BASE}/userinfo",
            headers=_get_auth_headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "sub": data.get("sub"),
            "name": data.get("name"),
            "picture": data.get("picture"),
        }


async def publish_text_post(text: str) -> dict:
    """Publish a text-only post to LinkedIn."""
    profile = await get_profile()
    person_urn = f"urn:li:person:{profile['sub']}"

    body = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{LINKEDIN_API_BASE}/ugcPosts",
            headers={**_get_auth_headers(), "Content-Type": "application/json"},
            json=body,
        )
        resp.raise_for_status()
        return {"post_id": resp.headers.get("x-restli-id", resp.json().get("id"))}


async def publish_image_post(text: str, image_bytes: bytes) -> dict:
    """Publish a post with an image to LinkedIn."""
    profile = await get_profile()
    person_urn = f"urn:li:person:{profile['sub']}"
    headers = _get_auth_headers()

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Register image upload
        register_body = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        resp = await client.post(
            f"{LINKEDIN_API_BASE}/assets?action=registerUpload",
            headers={**headers, "Content-Type": "application/json"},
            json=register_body,
        )
        resp.raise_for_status()
        upload_data = resp.json()

        upload_url = upload_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset = upload_data["value"]["asset"]

        # Step 2: Upload the image
        resp = await client.put(
            upload_url,
            headers={**headers, "Content-Type": "image/png"},
            content=image_bytes,
        )
        resp.raise_for_status()

        # Step 3: Create the post with the image
        post_body = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "media": asset,
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        resp = await client.post(
            f"{LINKEDIN_API_BASE}/ugcPosts",
            headers={**headers, "Content-Type": "application/json"},
            json=post_body,
        )
        resp.raise_for_status()
        return {"post_id": resp.headers.get("x-restli-id", resp.json().get("id"))}
