"""
Interfaces abstratas para os Provedores de Dados do Content Radar.
Garante o desacoplamento arquitetural (Padrão Adapter), permitindo
trocar ou adicionar provedores sem alterar o núcleo do Radar ou do Gemini.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.research.models import ResearchItem


class SourceAdapter(ABC):
    """Interface base obrigatória para qualquer fonte de dados externa."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome legível do provedor (ex: 'ATP Tour', 'Google Trends')."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Tipo de fonte: 'trends', 'official', 'news', 'community'."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível e pronto para uso."""
        pass

    @abstractmethod
    async def fetch_items(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 10,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """
        Executa a coleta e retorna itens estruturados e normalizados.
        Nenhum dado não normalizado deve sair deste método.
        """
        pass


class TrendsProvider(SourceAdapter):
    """Interface especializada para provedores de dados de tendência (ex: pytrends)."""

    @abstractmethod
    async def get_rising_queries(
        self,
        keyword: str,
        geo: str = "BR",
        timeframe: str = "today 7-d",
    ) -> List[Dict[str, Any]]:
        """Retorna termos e pesquisas em ascensão (Breakout / Rising)."""
        pass

    @abstractmethod
    async def get_related_topics(
        self,
        keyword: str,
        geo: str = "BR",
    ) -> List[Dict[str, Any]]:
        """Retorna tópicos associados à palavra-chave."""
        pass
