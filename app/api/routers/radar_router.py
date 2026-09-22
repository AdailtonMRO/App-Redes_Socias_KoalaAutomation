"""
Router da API REST para o Content Radar.
Permite consultar oportunidades diárias, forçar varreduras sob demanda
e integrar com cron jobs externos ou painel web.
"""
from fastapi import APIRouter, Query, BackgroundTasks
from typing import Optional, Dict, Any

from app.research.radar import ContentRadar
from app.research.models import RadarDailyReport
from app.profiles.manager import ProfileManager

router = APIRouter(prefix="/api/radar", tags=["Content Radar"])
profile_manager = ProfileManager()
radar = ContentRadar()


@router.get("/daily", response_model=RadarDailyReport)
async def get_daily_radar(
    profile_id: Optional[str] = Query(None, description="ID do perfil de referência"),
    top_k: int = Query(5, ge=1, le=10, description="Quantidade de oportunidades a retornar"),
    refresh: bool = Query(False, description="Forçar rotação anti-repetição de notícias"),
):
    """Retorna o briefing diário consolidado com as melhores oportunidades de conteúdo."""
    profile_data = None
    if profile_id:
        profile = profile_manager.get_profile(profile_id)
        if profile:
            profile_data = profile.model_dump()
    else:
        profiles = profile_manager.list_profiles()
        if profiles:
            profile_data = profiles[0]

    report = await radar.run_daily_radar(profile_data=profile_data, top_k=top_k, refresh=refresh)
    return report


@router.post("/scan")
async def trigger_radar_scan(
    notify_telegram: bool = Query(True, description="Se deve enviar o briefing matinal no Telegram"),
    refresh: bool = Query(False, description="Forçar rotação anti-repetição"),
):
    """Dispara a varredura sob demanda de todas as fontes externas especializadas."""
    profiles = profile_manager.list_profiles()
    profile_data = profiles[0] if profiles else None

    report = await radar.run_daily_radar(profile_data=profile_data, top_k=5, refresh=refresh)

    if notify_telegram:
        from app.bot.telegram_bot import get_telegram_bot
        bot = get_telegram_bot()
        if bot and bot.allowed_user_id:
            try:
                chat_id = int(bot.allowed_user_id)
                from app.bot.handlers import LATEST_RADAR_OPPORTUNITIES
                keyboard_buttons = []
                for opp in report.top_opportunities:
                    LATEST_RADAR_OPPORTUNITIES[opp.id] = opp
                    btn_title = f"{opp.pillar.split()[0]} {opp.headline[:32]}..."
                    keyboard_buttons.append([{"text": btn_title, "callback_data": f"radar_create_{opp.id}"}])

                keyboard_buttons.append([
                    {"text": "🔄 Atualizar Notícias", "callback_data": "menu_radar_refresh"},
                    {"text": "⬅️ Menu Principal", "callback_data": "menu_start"},
                ])

                await bot.send_message(
                    chat_id=chat_id,
                    text=report.summary_message,
                    reply_markup={"inline_keyboard": keyboard_buttons},
                    parse_mode="Markdown",
                )
            except Exception as e:
                print(f"[WARN] Falha ao despachar briefing do radar no Telegram: {e}")

    return {
        "success": True,
        "total_scanned": report.total_scanned,
        "opportunities_count": len(report.top_opportunities),
        "featured": report.featured_opportunity.headline if report.featured_opportunity else None,
    }
