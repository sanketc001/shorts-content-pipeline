from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # OpenAI-compatible API
    openai_api_base: str = "http://localhost:3000/v1"
    openai_api_key: str = "your-key-here"
    openai_model_heavy: str = "gpt-4.1"
    openai_model_light: str = "gpt-5-mini"

    # ComfyUI
    comfyui_url: str = "http://127.0.0.1:8188"

    # Model paths
    model_base_path: str = "./models"
    diffusion_model_t2i: str = "diffusion_models/z_image_turbo_bf16.safetensors"
    diffusion_model_i2i: str = "diffusion_models/flux-2-klein-9b-fp8.safetensors"
    vae_t2i: str = "vae/ae.safetensors"
    vae_i2i: str = "vae/flux2-vae.safetensors"
    text_encoder: str = "text_encoders/qwen_3_4b_fp4_mixed.safetensors"

    # Output
    output_dir: str = "./output"

    # OAuth - YouTube
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/youtube/callback"

    # OAuth - Instagram
    meta_client_id: str = ""
    meta_client_secret: str = ""
    meta_redirect_uri: str = "http://localhost:8000/api/auth/instagram/callback"

    # OAuth - LinkedIn
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_redirect_uri: str = "http://localhost:8000/api/auth/linkedin/callback"

    # App
    secret_key: str = "change-this-to-a-random-string"
    frontend_url: str = "http://localhost:5173"

    @property
    def t2i_model_path(self) -> Path:
        return Path(self.model_base_path) / self.diffusion_model_t2i

    @property
    def i2i_model_path(self) -> Path:
        return Path(self.model_base_path) / self.diffusion_model_i2i

    @property
    def vae_t2i_path(self) -> Path:
        return Path(self.model_base_path) / self.vae_t2i

    @property
    def vae_i2i_path(self) -> Path:
        return Path(self.model_base_path) / self.vae_i2i

    @property
    def text_encoder_path(self) -> Path:
        return Path(self.model_base_path) / self.text_encoder

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()
