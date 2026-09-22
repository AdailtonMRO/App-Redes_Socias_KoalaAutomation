"""
Orquestrador Central do Content Radar.
Coordena a varredura paralela em múltiplos provedores desacoplados,
consolida os dados normalizados e gera o briefing de oportunidades com o Gemini.
"""
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem, ContentOpportunity, RadarDailyReport
from app.research.content_opportunities import ContentOpportunityScorer
from app.research.verification import ItemVerifier
from app.research.scoring import ResearchScorer
from app.research.adapters.google_trends import GoogleTrendsAdapter
from app.research.adapters.atp import ATPAdapter
from app.research.adapters.itf import ITFAdapter
from app.research.adapters.news import NewsAdapter


class ContentRadar:
    """Orquestrador do Radar de Conteúdo."""

    def __init__(
        self,
        adapters: Optional[List[SourceAdapter]] = None,
        scorer: Optional[ContentOpportunityScorer] = None,
    ):
        self.adapters = adapters or [
            GoogleTrendsAdapter(),
            ATPAdapter(),
            ITFAdapter(),
            NewsAdapter(),
        ]
        self.scorer = scorer or ContentOpportunityScorer()

    async def scan_all_sources(
        self,
        keywords: Optional[List[str]] = None,
        limit_per_source: int = 5,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """Varre todas as fontes cadastradas concorrentemente de forma segura."""
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
        top_k: int = 5,
    ) -> RadarDailyReport:
        """
        Executa o pipeline completo do Radar:
        1. Coleta itens das fontes
        2. Normaliza e deduplica
        3. Passa pelo filtro Gemini com ângulo de conversão DIY
        4. Monta o relatório diário
        """
        today_str = datetime.now().strftime("%d/%m/%Y")
        raw_items = await self.scan_all_sources(limit_per_source=4)

        opportunities = await self.scorer.score_and_filter(
            items=raw_items,
            profile_data=profile_data,
            top_k=top_k,
        )

        featured = opportunities[0] if opportunities else None

        # Monta mensagem formatada para o Telegram
        summary_msg = self.format_telegram_briefing(today_str, len(raw_items), opportunities, featured)

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
    ) -> str:
        """Gera o texto com formatação rica para o Telegram."""
        lines = [
            f"🎾 *RADAR KOALA — {date_str}*",
            f"Varri as fontes oficiais (ATP, ITF, Trends e Notícias) e localizei *{total_scanned} acontecimentos* relevantes.",
            "",
            "📊 *Resumo das Oportunidades Selecionadas:*",
        ]

        for idx, opp in enumerate(opportunities[:4], 1):
            lines.append(f"{idx}. {opp.pillar} — *{opp.headline}*")

        if featured:
            lines.extend([
                "",
                "💡 *SUGESTÃO DE DESTAQUE PARA HOJE:*",
                f"🎬 *\"{featured.headline}\"*",
                f"• *Pilar:* {featured.pillar}",
                f"• *Formato Ideal:* `{featured.suggested_format}` (Score: {featured.relevance_score}/10)",
                f"• *Origem:* {featured.source_reference}",
                "",
                "🎯 *Ângulo Koala (Ponte para a Máquina DIY):*",
                f"_{featured.diy_ball_machine_angle}_",
            ])

        lines.extend([
            "",
            "Toque no botão abaixo para gerar o roteiro e a mídia automaticamente!",
        ])

        return "\n".join(lines)
