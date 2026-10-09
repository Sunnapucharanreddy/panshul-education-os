"""Central configuration. Everything comes from the environment — no hardcoded
secrets, URLs, or model names anywhere else in the codebase."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Panshul Education OS"
    # Fail safe when a deployment forgets to set ENV: startup must not try to
    # create tables against the local-development database URL. Local .env
    # files and .env.example explicitly set ENV=development.
    env: str = "production"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    # Comma-separated browser origins allowed to call the API directly.
    # The Next.js site proxies through its own server, so this is for other clients.
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    secret_key: str = "dev-only-secret"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # Infra
    database_url: str = "postgresql+asyncpg://panshul:panshul@localhost:5432/panshul"
    redis_url: str = "redis://localhost:6379/0"

    # OTP
    otp_ttl_seconds: int = 300
    otp_max_attempts: int = 5
    sms_provider: str = "console"
    sms_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_api_key_sid: str = ""
    twilio_api_secret: str = ""
    twilio_verify_service_sid: str = ""

    # LLM
    llm_provider: str = "qwen"
    llm_base_url: str = "http://localhost:8001/v1"
    llm_api_key: str = ""
    llm_model: str = "Qwen/Qwen3-14B"
    llm_timeout_seconds: int = 120

    # YouTube Data API (backend only)
    youtube_api_key: str = ""

    # Embeddings / vector
    embedding_provider: str = "bge_m3"
    embedding_model: str = "BAAI/bge-m3"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_memory: str = "student_memory"
    qdrant_collection_content: str = "learning_content"

    # Voice
    stt_provider: str = "faster_whisper"
    stt_model: str = "large-v3"
    tts_provider: str = "xtts_v2"
    tts_model_path: str = "models/xtts_v2"

    # Sarvam AI (API-based Indian-language voice — no GPU needed)
    sarvam_api_key: str = ""
    sarvam_tts_model: str = "bulbul:v2"
    sarvam_tts_speaker: str = "anushka"
    sarvam_stt_model: str = "saaras:v4"

    # Prompts
    prompts_dir: str = "prompts"


@lru_cache
def get_settings() -> Settings:
    return Settings()
