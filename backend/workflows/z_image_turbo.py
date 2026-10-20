"""ComfyUI workflow builder for Z-Image Turbo text-to-image.

Based on user's verified working ComfyUI API export.
Z-Image Turbo is Lumina2-based, using:
- CLIPLoader type=lumina2 with qwen_3_4b_fp4_mixed
- ModelSamplingAuraFlow shift=3
- ConditioningZeroOut for negative
- EmptySD3LatentImage
- KSampler: res_multistep, simple, 8 steps, cfg=1
"""


def build_workflow(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    seed: int = 0,
    text_encoder: str = "qwen_3_4b_fp4_mixed.safetensors",
    vae: str = "ae.safetensors",
    unet: str = "z_image_turbo_fp8_e4m3fn.safetensors",
) -> dict:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": unet,
                "weight_dtype": "default",
            },
            "_meta": {"title": "Load Diffusion Model"},
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": text_encoder,
                "type": "lumina2",
                "device": "default",
            },
            "_meta": {"title": "Load CLIP"},
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": vae,
            },
            "_meta": {"title": "Load VAE"},
        },
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": prompt,
                "clip": ["2", 0],
            },
            "_meta": {"title": "CLIP Text Encode (Prompt)"},
        },
        "5": {
            "class_type": "ConditioningZeroOut",
            "inputs": {
                "conditioning": ["4", 0],
            },
            "_meta": {"title": "ConditioningZeroOut"},
        },
        "6": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
            "_meta": {"title": "EmptySD3LatentImage"},
        },
        "7": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {
                "shift": 3,
                "model": ["1", 0],
            },
            "_meta": {"title": "ModelSamplingAuraFlow"},
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 8,
                "cfg": 1,
                "sampler_name": "res_multistep",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["7", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0],
            },
            "_meta": {"title": "KSampler"},
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["8", 0],
                "vae": ["3", 0],
            },
            "_meta": {"title": "VAE Decode"},
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": "shorts_t2i",
                "images": ["9", 0],
            },
            "_meta": {"title": "Save Image"},
        },
    }
