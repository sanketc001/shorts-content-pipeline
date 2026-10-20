"""Instagram Graph API publishing service."""

import asyncio

import httpx
from auth.oauth_manager import get_token

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


def _get_access_token() -> str:
    token = get_token("instagram")
    if not token:
        raise RuntimeError("Not connected to Instagram")
    return token["access_token"]


async def get_instagram_account_id() -> str:
    """Get the Instagram Business account ID linked to the Facebook page."""
    access_token = _get_access_token()
    async with httpx.AsyncClient() as client:
        # Get pages
        resp = await client.get(
            f"{GRAPH_API_BASE}/me/accounts",
            params={"access_token": access_token},
        )
        resp.raise_for_status()
        pages = resp.json().get("data", [])

        if not pages:
            raise RuntimeError("No Facebook pages found. Link a page to your Instagram account.")

        page_id = pages[0]["id"]
        page_token = pages[0]["access_token"]

        # Get Instagram account linked to the page
        resp = await client.get(
            f"{GRAPH_API_BASE}/{page_id}",
            params={"fields": "instagram_business_account", "access_token": page_token},
        )
        resp.raise_for_status()
        ig_account = resp.json().get("instagram_business_account")

        if not ig_account:
            raise RuntimeError("No Instagram Business account linked to this page.")

        return ig_account["id"]


async def publish_image_post(
    image_url: str,
    caption: str,
) -> dict:
    """Publish a single image post to Instagram."""
    access_token = _get_access_token()
    ig_id = await get_instagram_account_id()

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Step 1: Create media container
        resp = await client.post(
            f"{GRAPH_API_BASE}/{ig_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            },
        )
        resp.raise_for_status()
        container_id = resp.json()["id"]

        # Step 2: Wait for container to be ready
        for _ in range(30):
            resp = await client.get(
                f"{GRAPH_API_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": access_token},
            )
            status = resp.json().get("status_code")
            if status == "FINISHED":
                break
            await asyncio.sleep(2)

        # Step 3: Publish
        resp = await client.post(
            f"{GRAPH_API_BASE}/{ig_id}/media_publish",
            data={"creation_id": container_id, "access_token": access_token},
        )
        resp.raise_for_status()
        return {"post_id": resp.json()["id"]}


async def publish_carousel(
    image_urls: list[str],
    caption: str,
) -> dict:
    """Publish a carousel post to Instagram."""
    access_token = _get_access_token()
    ig_id = await get_instagram_account_id()

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create individual media containers
        children_ids = []
        for url in image_urls:
            resp = await client.post(
                f"{GRAPH_API_BASE}/{ig_id}/media",
                data={
                    "image_url": url,
                    "is_carousel_item": "true",
                    "access_token": access_token,
                },
            )
            resp.raise_for_status()
            children_ids.append(resp.json()["id"])

        # Create carousel container
        resp = await client.post(
            f"{GRAPH_API_BASE}/{ig_id}/media",
            data={
                "media_type": "CAROUSEL",
                "children": ",".join(children_ids),
                "caption": caption,
                "access_token": access_token,
            },
        )
        resp.raise_for_status()
        container_id = resp.json()["id"]

        # Wait and publish
        for _ in range(30):
            resp = await client.get(
                f"{GRAPH_API_BASE}/{container_id}",
                params={"fields": "status_code", "access_token": access_token},
            )
            if resp.json().get("status_code") == "FINISHED":
                break
            await asyncio.sleep(2)

        resp = await client.post(
            f"{GRAPH_API_BASE}/{ig_id}/media_publish",
            data={"creation_id": container_id, "access_token": access_token},
        )
        resp.raise_for_status()
        return {"post_id": resp.json()["id"]}
