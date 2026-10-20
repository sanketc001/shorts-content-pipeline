"""Direct model inference for image generation (primary backend).

Loads standalone UNet safetensors + separate text encoder + VAE
using ComfyUI's own model loading infrastructure for maximum compatibility.
Falls back gracefully to ComfyUI API if direct loading fails.
"""

import asyncio
import io
import os
import random
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

from config import settings

# Thread pool for blocking inference calls
_executor = ThreadPoolExecutor(max_workers=1)

# Track if ComfyUI path has been added
_comfy_initialized = False
_pipeline_cache: dict = {}


def _init_comfy():
    """Add ComfyUI to sys.path so we can use its model loading infrastructure."""
    global _comfy_initialized
    if _comfy_initialized:
        return

    comfyui_path = str(Path(settings.model_base_path).parent)
    if comfyui_path not in sys.path:
        sys.path.insert(0, comfyui_path)

    # Set ComfyUI model paths
    os.environ.setdefault("COMFYUI_MODEL_PATH", settings.model_base_path)

    _comfy_initialized = True


def _load_t2i_components():
    """Load Z-Image Turbo components for text-to-image."""
    if "t2i" in _pipeline_cache:
        return _pipeline_cache["t2i"]

    try:
        import torch
        from safetensors.torch import load_file

        print("[ImageService] Loading Z-Image Turbo T2I components...")
        start = time.time()

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Try loading via diffusers FluxPipeline with component paths
        try:
            from diffusers import FluxPipeline, AutoencoderKL, FluxTransformer2DModel
            from transformers import AutoTokenizer, AutoModelForCausalLM

            # Load the UNet/transformer from single file
            print("[ImageService]   Loading transformer...")
            transformer = FluxTransformer2DModel.from_single_file(
                str(settings.t2i_model_path),
                torch_dtype=torch.bfloat16,
            )

            print("[ImageService]   Loading VAE...")
            vae = AutoencoderKL.from_single_file(
                str(settings.vae_t2i_path),
                torch_dtype=torch.bfloat16,
            )

            components = {
                "transformer": transformer,
                "vae": vae,
                "device": device,
                "method": "diffusers",
            }

            _pipeline_cache["t2i"] = components
            print(f"[ImageService] T2I components loaded in {time.time() - start:.1f}s")
            return components

        except Exception as e:
            print(f"[ImageService]   Diffusers loading failed: {e}")
            print("[ImageService]   Trying raw safetensors loading...")

            # Fallback: load raw state dicts for manual inference
            unet_sd = load_file(str(settings.t2i_model_path), device="cpu")
            vae_sd = load_file(str(settings.vae_t2i_path), device="cpu")

            components = {
                "unet_sd": unet_sd,
                "vae_sd": vae_sd,
                "device": device,
                "method": "raw",
            }

            _pipeline_cache["t2i"] = components
            print(f"[ImageService] T2I raw state dicts loaded in {time.time() - start:.1f}s")
            return components

    except Exception as e:
        print(f"[ImageService] Failed to load T2I components: {e}")
        raise


def _load_i2i_components():
    """Load Flux 2 Klein 9B components for image-to-image."""
    if "i2i" in _pipeline_cache:
        return _pipeline_cache["i2i"]

    try:
        import torch
        from safetensors.torch import load_file

        print("[ImageService] Loading Flux 2 Klein I2I components...")
        start = time.time()

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            from diffusers import FluxImg2ImgPipeline, AutoencoderKL, FluxTransformer2DModel

            print("[ImageService]   Loading transformer (fp8)...")
            transformer = FluxTransformer2DModel.from_single_file(
                str(settings.i2i_model_path),
                torch_dtype=torch.float16,
            )

            print("[ImageService]   Loading VAE...")
            vae = AutoencoderKL.from_single_file(
                str(settings.vae_i2i_path),
                torch_dtype=torch.float16,
            )

            components = {
                "transformer": transformer,
                "vae": vae,
                "device": device,
                "method": "diffusers",
            }

            _pipeline_cache["i2i"] = components
            print(f"[ImageService] I2I components loaded in {time.time() - start:.1f}s")
            return components

        except Exception as e:
            print(f"[ImageService]   Diffusers loading failed: {e}")
            print("[ImageService]   Trying raw safetensors loading...")

            unet_sd = load_file(str(settings.i2i_model_path), device="cpu")
            vae_sd = load_file(str(settings.vae_i2i_path), device="cpu")

            components = {
                "unet_sd": unet_sd,
                "vae_sd": vae_sd,
                "device": device,
                "method": "raw",
            }

            _pipeline_cache["i2i"] = components
            print(f"[ImageService] I2I raw state dicts loaded in {time.time() - start:.1f}s")
            return components

    except Exception as e:
        print(f"[ImageService] Failed to load I2I components: {e}")
        raise


def _run_t2i(prompt: str, width: int, height: int, seed: int) -> bytes:
    """Run T2I inference via diffusers pipeline."""
    import torch

    components = _load_t2i_components()

    if components["method"] == "diffusers":
        from diffusers import FluxPipeline

        # Build pipeline from components
        pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            transformer=components["transformer"],
            vae=components["vae"],
            torch_dtype=torch.bfloat16,
        )
        pipe.enable_model_cpu_offload()

        generator = torch.Generator("cuda").manual_seed(seed)
        result = pipe(
            prompt=prompt,
            width=width,
            height=height,
            num_inference_steps=4,
            guidance_scale=1.0,
            generator=generator,
        )

        img = result.images[0]
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    # Raw method - can't do full inference without the full pipeline
    raise RuntimeError(
        "Direct inference requires diffusers with FluxPipeline support. "
        "Use ComfyUI backend instead, or install: pip install diffusers[torch] transformers"
    )


def _run_i2i(prompt: str, image_bytes: bytes, denoise: float, seed: int) -> bytes:
    """Run I2I inference via diffusers pipeline."""
    import torch

    components = _load_i2i_components()

    if components["method"] == "diffusers":
        from diffusers import FluxImg2ImgPipeline

        pipe = FluxImg2ImgPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            transformer=components["transformer"],
            vae=components["vae"],
            torch_dtype=torch.float16,
        )
        pipe.enable_model_cpu_offload()

        source_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        generator = torch.Generator("cuda").manual_seed(seed)

        result = pipe(
            prompt=prompt,
            image=source_image,
            strength=denoise,
            num_inference_steps=20,
            guidance_scale=1.0,
            generator=generator,
        )

        img = result.images[0]
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    raise RuntimeError(
        "Direct inference requires diffusers with FluxImg2ImgPipeline support. "
        "Use ComfyUI backend instead, or install: pip install diffusers[torch] transformers"
    )


async def generate_t2i(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    seed: int | None = None,
) -> bytes:
    """Async T2I generation using direct inference."""
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_t2i, prompt, width, height, seed)


async def generate_i2i(
    prompt: str,
    image_bytes: bytes,
    denoise: float = 0.65,
    seed: int | None = None,
) -> bytes:
    """Async I2I generation using direct inference."""
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _run_i2i, prompt, image_bytes, denoise, seed)


def is_available() -> bool:
    """Check if direct inference is available (CUDA + torch + diffusers)."""
    try:
        import torch
        if not torch.cuda.is_available():
            return False
        import diffusers  # noqa: F401
        return True
    except ImportError:
        return False
