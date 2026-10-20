import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from routers import text, image, video, auth

app = FastAPI(title="Content Creation Pipeline", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure output directory exists
output_path = Path(settings.output_dir)
output_path.mkdir(parents=True, exist_ok=True)

app.mount("/output", StaticFiles(directory=str(output_path)), name="output")

app.include_router(text.router, prefix="/api/text", tags=["text"])
app.include_router(image.router, prefix="/api/image", tags=["image"])
app.include_router(video.router, prefix="/api/video", tags=["video"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/models")
async def list_models():
    return {
        "text_models": ["gpt-5-mini", "gpt-4o", "gpt-4.1"],
        "image_backends": ["direct", "comfyui"],
        "image_models": {
            "t2i": "Z-Image Turbo (z_image_turbo_bf16)",
            "i2i": "Flux 2 Klein 9B (flux-2-klein-9b-fp8)",
        },
    }
