"""
Roteador de Gerenciamento de Configurações (.env)
Permite ao usuário configurar o acesso pelo Painel Web.
"""
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import get_settings, BASE_DIR

router = APIRouter(prefix="/api/config", tags=["Configurações"])


class ConfigUpdateSchema(BaseModel):
    ENVIRONMENT: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_ALLOWED_USER_ID: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_TEXT_MODEL: Optional[str] = None
    VEO_VIDEO_MODEL: Optional[str] = None
    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    PUBLIC_MEDIA_BASE_URL: Optional[str] = None


def mask_secret(value: Optional[str]) -> Optional[str]:
    """Oculta a maior parte de uma chave secreta para exibição segura."""
    if not value or len(value) < 8:
        return "********" if value else ""
    return f"{value[:4]}...{value[-4:]}"


@router.get("")
def get_current_config():
    """Retorna as configurações atuais com valores mascarados."""
    settings = get_settings()
    return {
        "ENVIRONMENT": settings.ENVIRONMENT,
        "APP_PORT": settings.APP_PORT,
        "TELEGRAM_BOT_TOKEN_SET": bool(settings.TELEGRAM_BOT_TOKEN),
        "TELEGRAM_ALLOWED_USER_ID": settings.TELEGRAM_ALLOWED_USER_ID,
        "GEMINI_API_KEY_SET": bool(settings.GEMINI_API_KEY),
        "GEMINI_TEXT_MODEL": settings.GEMINI_TEXT_MODEL,
        "VEO_VIDEO_MODEL": settings.VEO_VIDEO_MODEL,
        "INSTAGRAM_APP_ID": settings.INSTAGRAM_APP_ID,
        "INSTAGRAM_APP_SECRET_SET": bool(settings.INSTAGRAM_APP_SECRET),
        "INSTAGRAM_ACCOUNT_ID": settings.INSTAGRAM_ACCOUNT_ID,
        "INSTAGRAM_ACCESS_TOKEN_SET": bool(settings.INSTAGRAM_ACCESS_TOKEN),
        "PUBLIC_MEDIA_BASE_URL": settings.PUBLIC_MEDIA_BASE_URL,
    }


@router.post("")
async def update_config(payload: ConfigUpdateSchema):
    """Atualiza o arquivo .env do projeto com os valores informados pelo usuário."""
    env_file = BASE_DIR / ".env"
    existing_vars = {}

    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing_vars[k.strip()] = v.strip().strip('"').strip("'")

    # Atualiza apenas campos fornecidos no payload
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if value is not None and value != "":
            existing_vars[key] = value

    # Reescreve o .env formatado
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# Gerado automaticamente pelo Painel de Configurações Koala Automation\n")
            for k, v in sorted(existing_vars.items()):
                f.write(f'{k}="{v}"\n')
        
        # Limpa o cache das configurações
        get_settings.cache_clear()
        new_settings = get_settings()

        # Recarrega o Telegram Bot se configurado
        from app.bot.telegram_bot import bot_service
        if new_settings.TELEGRAM_BOT_TOKEN:
            bot_service.stop()
            bot_service.token = new_settings.TELEGRAM_BOT_TOKEN
            bot_service.allowed_user_id = str(new_settings.TELEGRAM_ALLOWED_USER_ID or "").strip()
            bot_service.base_url = f"https://api.telegram.org/bot{new_settings.TELEGRAM_BOT_TOKEN}"
            bot_service.start()
            print("[INFO] Telegram Bot recarregado com novo token!")

        return {"success": True, "message": "Configurações salvas no .env e Telegram Bot atualizado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar .env: {str(e)}")
