"""
Motor de Pontuação Heurística e Ranqueamento para o Content Radar.
Atribui pesos aos itens com base na proximidade com o universo Koala Tênis
(Tênis + Treinamento + Tecnologia + Máquinas de Bolas DIY).
"""
from typing import List
from app.research.models import ResearchItem

# Dicionário de pesos calibrados para Notícias e Destaques do Tênis
NICHE_WEIGHTS = {
    # Nível 4: Astros e Destaques do Tênis Brasileiro (Prioridade Máxima)
    "joao fonseca": 16,
    "fonseca": 14,
    "bia haddad": 16,
    "haddad": 14,
    "luisa stefani": 15,
    "stefani": 13,
    "thiago wild": 13,
    "monteiro": 13,
    "cbt": 12,
    "copa davis": 14,
    "davis cup": 14,
    "billie jean king": 12,
    "juvenil": 10,
    # Nível 3: Astros Mundiais & Grandes Torneios
    "alcaraz": 14,
    "sinner": 14,
    "djokovic": 14,
    "grand slam": 13,
    "wimbledon": 13,
    "roland garros": 13,
    "us open": 13,
    "australian open": 13,
    "atp": 12,
    "wta": 12,
    "itf": 10,
    # Nível 2: Desfechos Competitivos e Rankings
    "campeao": 10,
    "titulo": 10,
    "final": 10,
    "vence": 9,
    "vitoria": 9,
    "ranking": 9,
    "recorde": 9,
    # Nível 1: Técnica, Biomecânica e Equipamentos
    "saque": 8,
    "forehand": 8,
    "backhand": 8,
    "voleio": 8,
    "treino": 8,
    "biomecanica": 8,
    "raquete": 7,
    "cordas": 6,
    "velocidade": 7,
}



class ResearchScorer:
    """Calcula a pontuação de afinidade dos itens com o projeto Koala."""

    @classmethod
    def calculate_item_score(cls, item: ResearchItem) -> float:
        """Calcula uma nota heurística de 0 a 100 baseada em palavras-chave e métricas."""
        text = f"{item.title} {item.summary} {' '.join(item.topics)}".lower()
        score = 10.0  # Pontuação base

        for keyword, weight in NICHE_WEIGHTS.items():
            if keyword in text:
                score += weight

        # Bônus para tendências em crescimento rápido
        growth = item.raw_metrics.get("growth_rate")
        if growth and isinstance(growth, (int, float)) and growth > 100:
            score += 15.0

        return min(score, 100.0)

    @classmethod
    def rank_items(cls, items: List[ResearchItem]) -> List[ResearchItem]:
        """Ordena a lista de itens priorizando os mais estratégicos para o funil Koala."""
        return sorted(items, key=cls.calculate_item_score, reverse=True)
