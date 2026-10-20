"""Text generation endpoints with SSE streaming."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from config import settings
from services.openai_service import generate_text_stream, generate_text
from services.prompt_templates import get_system_prompt, get_recommended_model

router = APIRouter()


class TextRequest(BaseModel):
    platform: str  # youtube, instagram, linkedin
    content_type: str  # title, description, caption, post, etc.
    topic: str
    context: str = ""
    tone: str = ""
    model: str | None = None


@router.post("/generate")
async def generate(req: TextRequest):
    system_prompt = get_system_prompt(req.platform, req.content_type)
    if not system_prompt:
        raise HTTPException(400, f"Unknown content type: {req.platform}/{req.content_type}")

    # Build user prompt
    user_parts = [f"Topic: {req.topic}"]
    if req.context:
        user_parts.append(f"Additional context: {req.context}")
    if req.tone:
        user_parts.append(f"Tone: {req.tone}")
    user_prompt = "\n".join(user_parts)

    # Select model
    model = req.model
    if model is None:
        tier = get_recommended_model(req.content_type)
        model = settings.openai_model_heavy if tier == "heavy" else settings.openai_model_light

    async def event_generator():
        try:
            async for chunk in generate_text_stream(system_prompt, user_prompt, model):
                yield {"data": chunk}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(event_generator())


@router.post("/generate-sync")
async def generate_sync(req: TextRequest):
    """Non-streaming text generation."""
    system_prompt = get_system_prompt(req.platform, req.content_type)
    if not system_prompt:
        raise HTTPException(400, f"Unknown content type: {req.platform}/{req.content_type}")

    user_parts = [f"Topic: {req.topic}"]
    if req.context:
        user_parts.append(f"Additional context: {req.context}")
    if req.tone:
        user_parts.append(f"Tone: {req.tone}")
    user_prompt = "\n".join(user_parts)

    model = req.model
    if model is None:
        tier = get_recommended_model(req.content_type)
        model = settings.openai_model_heavy if tier == "heavy" else settings.openai_model_light

    try:
        result = await generate_text(system_prompt, user_prompt, model)
        return {"content": result, "model": model}
    except Exception as e:
        raise HTTPException(500, str(e))
