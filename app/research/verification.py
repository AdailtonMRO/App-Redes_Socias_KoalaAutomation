"""
Camada de Verificação e Sanitização dos Itens do Content Radar.
Garante que nenhum item mal formatado, com links corrompidos ou spam
seja encaminhado para a análise do Gemini.
"""
import re
from typing import List
from app.research.models import ResearchItem

SPAM_KEYWORDS = [
    "aposta", "bet365", "cassino", "odd", "palpite", "tigrinho",
    "bônus de cadastro", "vagas de emprego", "horóscopo"
]


class ItemVerifier:
    """Verifica e limpa os itens brutos das fontes externas."""

    @staticmethod
    def is_valid(item: ResearchItem) -> bool:
        """Checa se o item tem conteúdo legítimo e relevante."""
        if not item.title or len(item.title.strip()) < 8:
            return False

        full_text = f"{item.title} {item.summary}".lower()

        # Descarta spam ou conteúdo de apostas
        for spam in SPAM_KEYWORDS:
            if spam in full_text:
                return False

        return True

    @staticmethod
    def clean_title(title: str) -> str:
        """Remove ruídos comuns de títulos de notícias."""
        clean = re.sub(r"\s*-\s*[A-Za-z0-9\.\s]+$", "", title)  # Remove sufixos como '- Portal X'
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def filter_and_clean(cls, items: List[ResearchItem]) -> List[ResearchItem]:
        """Aplica a verificação e limpeza em lote."""
        valid_items: List[ResearchItem] = []
        for it in items:
            if cls.is_valid(it):
                it.title = cls.clean_title(it.title)
                valid_items.append(it)
        return valid_items
