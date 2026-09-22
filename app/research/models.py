"""
Modelos de dados unificados para o Content Radar.
Garante que todas as fontes externas (Google Trends, ATP, ITF, Notícias)
sejam convertidas em um schema padronizado antes da análise pelo Gemini.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field


class ResearchItem(BaseModel):
    """Modelo normalizado para qualquer dado coletado de fontes externas."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_name: str = Field(..., description="Nome da fonte (ex: Google Trends, ATP Tour, ITF Tennis)")
    source_type: str = Field(..., description="Tipo de fonte (ex: trends, official, news, community)")
    title: str = Field(..., description="Título ou assunto principal encontrado")
    url: Optional[str] = Field(default="", description="Link original para a notícia ou relatório")
    summary: str = Field(default="", description="Resumo explicativo do acontecimento ou contexto")
    published_at: Optional[str] = Field(default=None, description="Data de publicação original (ISO)")
    collected_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Data da coleta")
    language: str = Field(default="pt", description="Idioma original do conteúdo (pt, en, etc)")
    country: str = Field(default="BR", description="País de referência ou escopo")
    topics: List[str] = Field(default_factory=list, description="Lista de tópicos/tags relacionados")
    raw_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas brutas (ex: volume de busca, crescimento)")

    def to_compact_dict(self) -> Dict[str, Any]:
        """Retorna uma representação limpa e concisa para o prompt do Gemini."""
        return {
            "id": self.id,
            "source": f"{self.source_name} ({self.source_type})",
            "title": self.title,
            "summary": self.summary[:300] if self.summary else "",
            "topics": self.topics,
            "url": self.url,
        }


class ContentOpportunity(BaseModel):
    """Oportunidade de conteúdo filtrada, refinada e conectada ao objetivo de negócio pelo Gemini."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    research_item_id: Optional[str] = Field(default=None, description="ID do ResearchItem original de referência")
    headline: str = Field(..., description="Gancho ou título irresistível para o post/vídeo")
    theme: str = Field(..., description="Tema central que resume a oportunidade")
    source_reference: str = Field(..., description="De onde veio o gatilho original (ex: ATP, Trends)")
    pillar: str = Field(
        ...,
        description="Pilar temático (🎾 Tênis Profissional, 🧠 Aprendizado, ⚙️ Tecnologia, 🔧 DIY/Engenharia, 🔥 Trends, 😂 Leve)",
    )
    relevance_score: int = Field(..., ge=1, le=10, description="Nota de relevância estratégica (1 a 10)")
    news_summary: str = Field(
        ...,
        description="Resumo claro, factual e informativo da matéria para exibição no Story",
    )
    key_takeaway: str = Field(
        default="",
        description="Ponto principal de destaque ou impacto no circuito do tênis",
    )
    suggested_format: str = Field(default="STORIES", description="Formato recomendado: STORIES, FEED, CAROUSEL ou REELS")
    why_it_matters: str = Field(..., description="Por que este assunto atrai o público tenista")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RadarDailyReport(BaseModel):
    """Relatório consolidado diário pronto para o Telegram."""
    date: str
    total_scanned: int
    top_opportunities: List[ContentOpportunity]
    featured_opportunity: Optional[ContentOpportunity]
    summary_message: str
