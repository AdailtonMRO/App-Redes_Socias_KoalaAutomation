"""
Módulo de Configuração Centralizada da Aplicação
Lê variáveis de ambiente (.env) utilizando Pydantic Settings com validação tipada.
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    BASE_DIR: Path = BASE_DIR
    # Ambiente geral
    ENVIRONMENT: str = "DSV"
    APP_PORT: int = 8080
    APP_HOST: str = "0.0.0.0"
    LOG_LEVEL: str = "INFO"
    DATA_DIR: str = str(BASE_DIR / "data")
    PROFILES_DIR: str = str(BASE_DIR / "profiles")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ALLOWED_USER_ID: Optional[str] = None

    # Google AI Studio (Gemini & Veo)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_TEXT_MODEL: str = "gemini-3-flash-preview"
    VEO_VIDEO_MODEL: str = "veo-3.1-lite-generate-preview"

    # Meta Graph API (Instagram)
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    PUBLIC_MEDIA_BASE_URL: Optional[str] = None

    # Banco de dados
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'instagram_ai.db'}"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
