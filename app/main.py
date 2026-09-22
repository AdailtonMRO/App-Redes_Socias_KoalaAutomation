"""
Ponto de Entrada da Aplicação FastAPI (Instagram AI / Koala Automation)
Serve tanto a API REST quanto a Interface Web de Configuração e Controle.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database.database import init_db
from app.api.routers.health_router import router as health_router
from app.api.routers.config_router import router as config_router
from app.api.routers.profiles_router import router as profiles_router
from app.api.routers.instagram_router import router as instagram_router
from app.api.routers.radar_router import router as radar_router

settings = get_settings()

app = FastAPI(
    title="Koala Social Media Automation API",
    description="Sistema de Automação de Redes Sociais com IA (Instagram AI V1)",
    version="1.0.0",
)

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.bot.telegram_bot import bot_service

# Evento de inicialização
@app.on_event("startup")
async def on_startup():
    init_db()
    if settings.TELEGRAM_BOT_TOKEN:
        bot_service.token = settings.TELEGRAM_BOT_TOKEN
        bot_service.allowed_user_id = str(settings.TELEGRAM_ALLOWED_USER_ID or "").strip()
        bot_service.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
        bot_service.start()
        print("[INFO] Telegram Bot polling iniciado com sucesso no startup!")


@app.on_event("shutdown")
async def on_shutdown():
    bot_service.stop()



# Inclusão dos Roteadores de API
app.include_router(health_router)
app.include_router(config_router)
app.include_router(profiles_router)
app.include_router(instagram_router)
app.include_router(radar_router)

# Montagem de diretório de mídia gerada (vídeos, carrosséis, stories)
media_dir = Path(settings.DATA_DIR).resolve()
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

# Montagem dos arquivos estáticos da Interface Web (app/static/)
static_dir = Path(__file__).resolve().parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
