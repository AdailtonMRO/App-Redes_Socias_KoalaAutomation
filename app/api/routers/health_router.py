"""
Roteador de Healthcheck e Prontidão
Atende às exigências de monitoramento do pipeline AppSpace 2 e orquestrador Docker.
"""
from fastapi import APIRouter
from app.config import get_settings
from app.database.database import engine
from sqlalchemy import text

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
def health_check():
    """Endpoint básico para checagem de vida do container."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@router.get("/ready")
def readiness_check():
    """Endpoint detalhado para validação de dependências e banco de dados."""
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception as e:
        db_error = str(e)
    else:
        db_error = None

    is_ready = db_ok
    status_code = 200 if is_ready else 503

    return {
        "ready": is_ready,
        "database": {"ok": db_ok, "error": db_error},
        "services": {
            "telegram_configured": bool(settings.TELEGRAM_BOT_TOKEN),
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "instagram_configured": bool(settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID),
        },
    }
