"""Video generation endpoints - placeholder for future implementation."""

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/generate")
async def generate_video():
    raise HTTPException(
        501,
        detail="Video generation pipeline is coming soon. This feature is under development.",
    )


@router.get("/status")
async def video_status():
    return {
        "available": False,
        "message": "Video generation pipeline is coming soon.",
        "planned_features": [
            "Text-to-video generation",
            "Video with AI speech synthesis",
            "YouTube Shorts / Instagram Reels / LinkedIn video",
            "Auto-captioning",
        ],
    }
