"""Image generation endpoints supporting both direct inference and ComfyUI."""

import time
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from config import settings
from services import image_service, comfyui_service

router = APIRouter()

# In-memory job tracking
_jobs: dict[str, dict] = {}


class T2IRequest(BaseModel):
    prompt: str
    width: int = 1024
    height: int = 1024
    seed: int | None = None
    backend: str = "comfyui"  # default to comfyui (more reliable)


@router.post("/t2i")
async def text_to_image(req: T2IRequest):
    """Generate image from text prompt using Z-Image Turbo."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "processing", "started": time.time()}

    try:
        image_bytes = None
        used_backend = req.backend

        # Try requested backend first, fall back to the other on failure
        if req.backend == "direct" and image_service.is_available():
            try:
                image_bytes = await image_service.generate_t2i(
                    prompt=req.prompt,
                    width=req.width,
                    height=req.height,
                    seed=req.seed,
                )
            except Exception as e:
                print(f"[Image] Direct T2I failed: {e}, falling back to ComfyUI")
                used_backend = "comfyui"

        if image_bytes is None:
            image_bytes = await comfyui_service.generate_t2i(
                prompt=req.prompt,
                width=req.width,
                height=req.height,
                seed=req.seed or 0,
            )
            used_backend = "comfyui"

        # Save to output directory
        output_path = Path(settings.output_dir) / f"{job_id}.png"
        output_path.write_bytes(image_bytes)

        elapsed = time.time() - _jobs[job_id]["started"]
        _jobs[job_id] = {
            "status": "completed",
            "filename": f"{job_id}.png",
            "backend": used_backend,
            "elapsed": elapsed,
        }

        return {
            "job_id": job_id,
            "status": "completed",
            "filename": f"{job_id}.png",
            "backend": used_backend,
            "elapsed": round(elapsed, 2),
        }

    except Exception as e:
        _jobs[job_id] = {"status": "failed", "error": str(e)}
        raise HTTPException(500, f"Image generation failed: {e}")


@router.post("/i2i")
async def image_to_image(
    prompt: str = Form(...),
    denoise: float = Form(0.65),
    seed: int | None = Form(None),
    backend: str = Form("comfyui"),
    image: UploadFile = File(...),
):
    """Transform image using Flux 2 Klein 9B."""
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "processing", "started": time.time()}

    try:
        image_bytes = await image.read()
        result_bytes = None
        used_backend = backend

        # Try requested backend first, fall back on failure
        if backend == "direct" and image_service.is_available():
            try:
                result_bytes = await image_service.generate_i2i(
                    prompt=prompt,
                    image_bytes=image_bytes,
                    denoise=denoise,
                    seed=seed,
                )
            except Exception as e:
                print(f"[Image] Direct I2I failed: {e}, falling back to ComfyUI")
                used_backend = "comfyui"

        if result_bytes is None:
            result_bytes = await comfyui_service.generate_i2i(
                prompt=prompt,
                image_bytes=image_bytes,
                filename=image.filename or "upload.png",
                denoise=denoise,
                seed=seed or 0,
            )
            used_backend = "comfyui"

        output_path = Path(settings.output_dir) / f"{job_id}.png"
        output_path.write_bytes(result_bytes)

        elapsed = time.time() - _jobs[job_id]["started"]
        _jobs[job_id] = {
            "status": "completed",
            "filename": f"{job_id}.png",
            "backend": used_backend,
            "elapsed": elapsed,
        }

        return {
            "job_id": job_id,
            "status": "completed",
            "filename": f"{job_id}.png",
            "backend": used_backend,
            "elapsed": round(elapsed, 2),
        }

    except Exception as e:
        _jobs[job_id] = {"status": "failed", "error": str(e)}
        raise HTTPException(500, f"Image generation failed: {e}")


@router.get("/status/{job_id}")
async def job_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {"job_id": job_id, **job}


@router.get("/result/{filename}")
async def get_result(filename: str):
    """Serve a generated image."""
    filepath = Path(settings.output_dir) / filename
    if not filepath.exists():
        raise HTTPException(404, "Image not found")
    return Response(content=filepath.read_bytes(), media_type="image/png")


@router.get("/backends")
async def list_backends():
    """Check which image generation backends are available."""
    direct = image_service.is_available()
    try:
        comfyui = await comfyui_service.check_status()
    except Exception:
        comfyui = False

    return {
        "direct": {"available": direct, "description": "Direct GPU inference (faster)"},
        "comfyui": {"available": comfyui, "description": "ComfyUI API (more reliable)"},
        "recommended": "comfyui" if comfyui else ("direct" if direct else "none"),
    }
