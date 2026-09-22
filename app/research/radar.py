"""
Orquestrador Central do Content Radar.
Coordena a varredura paralela em múltiplos provedores desacoplados (TenisBrasil,
Tenis News, Diário do Tênis, ge.globo, ESPN, WTA, CBT, ATP, ITF e Google Trends),
consolida os dados normalizados, aplica rotação anti-repetição e gera o briefing de
oportunidades lapidadas com o Google Gemini.
"""
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem, ContentOpportunity, RadarDailyReport
from app.research.content_opportunities import ContentOpportunityScorer
from app.research.verification import ItemVerifier
from app.research.scoring import ResearchScorer
from app.research.adapters.brazilian_tennis import BrazilianTennisAdapter
from app.research.adapters.sports_portals import SportsPortalsAdapter
from app.research.adapters.wta_cbt import WTAAndCBTAdapter
from app.research.adapters.news import NewsAdapter
from app.research.adapters.google_trends import GoogleTrendsAdapter
from app.research.adapters.atp import ATPAdapter
from app.research.adapters.itf import ITFAdapter

# Memória de rotação para evitar repetição entre atualizações sucessivas
_RECENT_HEADLINES_MEMORY: List[str] = []
_MAX_MEMORY_ITEMS = 30


class ContentRadar:
    """Orquestrador do Radar de Conteúdo Multi-Fontes."""

    def __init__(
        self,
        adapters: Optional[List[SourceAdapter]] = None,
        scorer: Optional[ContentOpportunityScorer] = None,
    ):
        self.adapters = adapters or [
            BrazilianTennisAdapter(),
            SportsPortalsAdapter(),
            WTAAndCBTAdapter(),
            NewsAdapter(),
            ATPAdapter(),
            ITFAdapter(),
            GoogleTrendsAdapter(),
        ]
        self.scorer = scorer or ContentOpportunityScorer()

    async def scan_all_sources(
        self,
        keywords: Optional[List[str]] = None,
        limit_per_source: int = 6,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """Varre todas as fontes cadastradas concorrentemente de forma resiliente."""
        tasks = []
        for adapter in self.adapters:
            if adapter.is_available():
                tasks.append(
                    adapter.fetch_items(
                        keywords=keywords,
                        limit=limit_per_source,
                        geo=geo,
                        language=language,
                    )
                )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items: List[ResearchItem] = []
        seen_titles = set()

        for res in results:
            if isinstance(res, Exception):
                print(f"[WARN] Erro em um dos adapters durante o scan: {res}")
                continue
            for item in res:
                title_key = item.title.strip().lower()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_items.append(item)

        # 1. Sanitização e Filtragem Anti-Spam
        cleaned_items = ItemVerifier.filter_and_clean(all_items)

        # 2. Ranqueamento Heurístico por Afinidade Koala Tênis & DIY
        ranked_items = ResearchScorer.rank_items(cleaned_items)

        return ranked_items

    async def run_daily_radar(
        self,
        profile_data: Optional[Dict[str, Any]] = None,
        top_k: int = 4,
        refresh: bool = False,
        db: Optional[Any] = None, # type: Session
    ) -> RadarDailyReport:
        """
        Executa o pipeline completo do Radar com anti-repetição dinâmica consultando o banco.
        1. Coleta itens das 7 fontes especializadas e portais nacionais
        2. Deduplica e sanitiza
        3. Passa pelo filtro Gemini com histórico de exclusão de temas recentes do banco
        4. Monta o relatório diário e persiste o run (items e opportunities) no banco
        """
        today_str = datetime.now().strftime("%d/%m/%Y")
        raw_items = await self.scan_all_sources(limit_per_source=6)

        # Passa histórico recente para evitar repetição (do banco se disponível)
        avoid_list = None
        performance_data = None
        profile_id = profile_data.get("id") if profile_data else None
        
        if refresh:
            if db:
                from app.database.radar_repository import RadarRepository
                from app.database.models import ContentModel, ContentStatus
                repo = RadarRepository(db)
                avoid_list = repo.get_recent_headlines(profile_id=profile_id, days=7)
                
                # Fetch recent metrics for the learning loop
                try:
                    recent_published = db.query(ContentModel).filter(
                        ContentModel.profile_id == profile_id,
                        ContentModel.status == ContentStatus.PUBLISHED,
                        ContentModel.metrics.has()
                    ).order_by(ContentModel.published_at.desc()).limit(10).all()
                    
                    if recent_published:
                        performance_data = []
                        for c in recent_published:
                            if c.metrics:
                                performance_data.append({
                                    "tema": c.topic,
                                    "formato": c.content_format,
                                    "engajamento": c.metrics.engagement_rate,
                                    "alcance": c.metrics.reach,
                                    "salvos": c.metrics.saved
                                })
                except Exception as e:
                    print(f"[WARN] Falha ao extrair métricas para Learning Loop: {e}")
            else:
                avoid_list = list(_RECENT_HEADLINES_MEMORY)

        opportunities = await self.scorer.score_and_filter(
            items=raw_items,
            profile_data=profile_data,
            top_k=top_k,
            avoid_headlines=avoid_list,
            force_refresh=refresh,
            performance_data=performance_data,
        )

        # Atualiza memória e salva no banco de dados
        if db:
            from app.database.radar_repository import RadarRepository
            repo = RadarRepository(db)
            repo.save_radar_run(
                profile_id=profile_id,
                total_scanned=len(raw_items),
                raw_items=raw_items,
                opportunities=opportunities
            )
        else:
            # Fallback for when no db is provided
            for opp in opportunities:
                if opp.headline and opp.headline not in _RECENT_HEADLINES_MEMORY:
                    _RECENT_HEADLINES_MEMORY.append(opp.headline)
            while len(_RECENT_HEADLINES_MEMORY) > _MAX_MEMORY_ITEMS:
                _RECENT_HEADLINES_MEMORY.pop(0)

        featured = opportunities[0] if opportunities else None

        # Monta mensagem formatada para o Telegram
        summary_msg = self.format_telegram_briefing(
            date_str=today_str,
            total_scanned=len(raw_items),
            opportunities=opportunities,
            featured=featured,
            is_refresh=refresh,
        )

        return RadarDailyReport(
            date=today_str,
            total_scanned=len(raw_items),
            top_opportunities=opportunities,
            featured_opportunity=featured,
            summary_message=summary_msg,
        )

    def format_telegram_briefing(
        self,
        date_str: str,
        total_scanned: int,
        opportunities: List[ContentOpportunity],
        featured: Optional[ContentOpportunity],
        is_refresh: bool = False,
    ) -> str:
        """Gera o texto com formatação rica para o Telegram."""
        title_header = "🔄 *RADAR ATUALIZADO*" if is_refresh else f"🎾 *RADAR KOALA — {date_str}*"
        lines = [
            title_header,
            f"Varri os portais especializados (*TenisBrasil, Tenis News, ge.globo, ESPN, WTA, CBT, ATP*) e localizei *{total_scanned} notícias e tendências em tempo real*.",
            "",
            "📊 *Notícias e Oportunidades para Stories:*",
        ]

        for idx, opp in enumerate(opportunities[:4], 1):
            src = f" ({opp.source_reference})" if opp.source_reference else ""
            lines.append(f"{idx}. {opp.pillar} — *{opp.headline}*{src}")

        if featured:
            lines.extend([
                "",
                "💡 *NOTÍCIA DE DESTAQUE PARA O STORY:*",
                f"📱 *\"{featured.headline}\"*",
                f"• *Pilar:* {featured.pillar}",
                f"• *Formato:* `Story (Imagem 9:16)` (Score: {featured.relevance_score}/10)",
                f"• *Origem:* {featured.source_reference}",
                "",
                "📝 *Resumo do Assunto Pesquisado:*",
                f"_{featured.news_summary}_",
            ])
            if featured.key_takeaway:
                lines.extend([
                    f"🎯 *Ponto Central:* _{featured.key_takeaway}_",
                ])

        lines.extend([
            "",
            "Toque no botão de qualquer notícia abaixo para gerar o Story 9:16 com a logomarca do perfil!",
        ])

        return "\n".join(lines)
