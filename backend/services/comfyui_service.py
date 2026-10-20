"""ComfyUI API client for image generation (fallback backend)."""

import asyncio
import json
import uuid
from pathlib import Path

import httpx

from config import settings


async def submit_workflow(workflow: dict) -> str:
    """Submit a workflow to ComfyUI and return the prompt_id."""
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{settings.comfyui_url}/prompt", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["prompt_id"]


async def poll_result(prompt_id: str, timeout: float = 300.0) -> dict:
    """Poll ComfyUI history until the prompt completes."""
    interval = 1.0
    elapsed = 0.0

    async with httpx.AsyncClient(timeout=30.0) as client:
        while elapsed < timeout:
            resp = await client.get(f"{settings.comfyui_url}/history/{prompt_id}")
            resp.raise_for_status()
            data = resp.json()

            if prompt_id in data:
                return data[prompt_id]

            await asyncio.sleep(interval)
            elapsed += interval

    raise TimeoutError(f"ComfyUI prompt {prompt_id} did not complete within {timeout}s")


async def get_image(filename: str, subfolder: str = "", folder_type: str = "output") -> bytes:
    """Retrieve a generated image from ComfyUI."""
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{settings.comfyui_url}/view", params=params)
        resp.raise_for_status()
        return resp.content


async def upload_image(image_bytes: bytes, filename: str) -> dict:
    """Upload an image to ComfyUI for use in img2img workflows."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        files = {"image": (filename, image_bytes, "image/png")}
        resp = await client.post(f"{settings.comfyui_url}/upload/image", files=files)
        resp.raise_for_status()
        return resp.json()


async def check_status() -> bool:
    """Check if ComfyUI is running and accessible."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.comfyui_url}/system_stats")
            return resp.status_code == 200
    except Exception:
        return False


async def generate_t2i(prompt: str, width: int = 1024, height: int = 1024, seed: int = 0) -> bytes:
    """Text-to-image using Z-Image Turbo via ComfyUI."""
    from workflows.z_image_turbo import build_workflow

    workflow = build_workflow(prompt=prompt, width=width, height=height, seed=seed)
    prompt_id = await submit_workflow(workflow)
    result = await poll_result(prompt_id)

    # Extract image filename from result
    outputs = result.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            img_info = node_output["images"][0]
            return await get_image(
                img_info["filename"],
                img_info.get("subfolder", ""),
                img_info.get("type", "output"),
            )

    raise RuntimeError("No image found in ComfyUI output")


async def generate_i2i(
    prompt: str,
    image_bytes: bytes,
    filename: str,
    denoise: float = 0.65,
    seed: int = 0,
) -> bytes:
    """Image-to-image using Flux 2 Klein via ComfyUI."""
    from workflows.flux2_klein_i2i import build_workflow

    upload_result = await upload_image(image_bytes, filename)
    uploaded_name = upload_result.get("name", filename)

    workflow = build_workflow(
        prompt=prompt,
        image_name=uploaded_name,
        denoise=denoise,
        seed=seed,
    )
    prompt_id = await submit_workflow(workflow)
    result = await poll_result(prompt_id)

    outputs = result.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            img_info = node_output["images"][0]
            return await get_image(
                img_info["filename"],
                img_info.get("subfolder", ""),
                img_info.get("type", "output"),
            )

    raise RuntimeError("No image found in ComfyUI output")
