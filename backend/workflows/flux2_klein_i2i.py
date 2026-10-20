"""ComfyUI workflow builder for Flux 2 Klein 4B image edit.

Exact replica of the user's verified working ComfyUI API export,
with prompt, image_name, and seed as dynamic parameters.
"""


def build_workflow(
    prompt: str,
    image_name: str,
    denoise: float = 0.65,
    seed: int = 0,
    text_encoder: str = "qwen_3_4b_fp4_mixed.safetensors",
    vae: str = "flux2-vae.safetensors",
    unet: str = "flux-2-klein-4b-fp8.safetensors",
) -> dict:
    steps = max(1, int(20 * denoise))

    return {
        "9": {
            "inputs": {
                "filename_prefix": "shorts_i2i",
                "images": ["75:65", 0],
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"},
        },
        "76": {
            "inputs": {
                "image": image_name,
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"},
        },
        "75:61": {
            "inputs": {
                "sampler_name": "euler",
            },
            "class_type": "KSamplerSelect",
            "_meta": {"title": "KSamplerSelect"},
        },
        "75:62": {
            "inputs": {
                "steps": steps,
                "width": ["75:100", 0],
                "height": ["75:100", 1],
            },
            "class_type": "Flux2Scheduler",
            "_meta": {"title": "Flux2Scheduler"},
        },
        "75:63": {
            "inputs": {
                "cfg": 5,
                "model": ["75:70", 0],
                "positive": ["75:79:77", 0],
                "negative": ["75:79:101", 0],
            },
            "class_type": "CFGGuider",
            "_meta": {"title": "CFGGuider"},
        },
        "75:64": {
            "inputs": {
                "noise": ["75:73", 0],
                "guider": ["75:63", 0],
                "sampler": ["75:61", 0],
                "sigmas": ["75:62", 0],
                "latent_image": ["75:66", 0],
            },
            "class_type": "SamplerCustomAdvanced",
            "_meta": {"title": "SamplerCustomAdvanced"},
        },
        "75:65": {
            "inputs": {
                "samples": ["75:64", 0],
                "vae": ["75:72", 0],
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"},
        },
        "75:73": {
            "inputs": {
                "noise_seed": seed,
            },
            "class_type": "RandomNoise",
            "_meta": {"title": "RandomNoise"},
        },
        "75:70": {
            "inputs": {
                "unet_name": unet,
                "weight_dtype": "default",
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load Diffusion Model"},
        },
        "75:71": {
            "inputs": {
                "clip_name": text_encoder,
                "type": "flux2",
                "device": "default",
            },
            "class_type": "CLIPLoader",
            "_meta": {"title": "Load CLIP"},
        },
        "75:74": {
            "inputs": {
                "text": prompt,
                "clip": ["75:71", 0],
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Positive Prompt)"},
        },
        "75:67": {
            "inputs": {
                "text": "",
                "clip": ["75:71", 0],
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Negative Prompt)"},
        },
        "75:72": {
            "inputs": {
                "vae_name": vae,
            },
            "class_type": "VAELoader",
            "_meta": {"title": "Load VAE"},
        },
        "75:66": {
            "inputs": {
                "width": ["75:100", 0],
                "height": ["75:100", 1],
                "batch_size": 1,
            },
            "class_type": "EmptyFlux2LatentImage",
            "_meta": {"title": "Empty Flux 2 Latent"},
        },
        "75:80": {
            "inputs": {
                "upscale_method": "nearest-exact",
                "megapixels": 1,
                "resolution_steps": 1,
                "image": ["76", 0],
            },
            "class_type": "ImageScaleToTotalPixels",
            "_meta": {"title": "ImageScaleToTotalPixels"},
        },
        "75:79:101": {
            "inputs": {
                "conditioning": ["75:67", 0],
                "latent": ["75:79:78", 0],
            },
            "class_type": "ReferenceLatent",
            "_meta": {"title": "ReferenceLatent"},
        },
        "75:79:78": {
            "inputs": {
                "pixels": ["75:80", 0],
                "vae": ["75:72", 0],
            },
            "class_type": "VAEEncode",
            "_meta": {"title": "VAE Encode"},
        },
        "75:79:77": {
            "inputs": {
                "conditioning": ["75:74", 0],
                "latent": ["75:79:78", 0],
            },
            "class_type": "ReferenceLatent",
            "_meta": {"title": "ReferenceLatent"},
        },
        "75:100": {
            "inputs": {
                "image": ["75:80", 0],
            },
            "class_type": "GetImageSize",
            "_meta": {"title": "Get Image Size"},
        },
    }
