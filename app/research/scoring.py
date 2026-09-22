"""
Motor de Pontuação Heurística e Ranqueamento para o Content Radar.
Atribui pesos aos itens com base na proximidade com o universo Koala Tênis
(Tênis + Treinamento + Tecnologia + Máquinas de Bolas DIY).
"""
from typing import List
from app.research.models import ResearchItem

# Dicionário de pesos por nicho temático
NICHE_WEIGHTS = {
    # Nível 4: Direto ao objetivo (DIY Máquina Lançadora)
    "maquina de bola": 15,
    "maquina de bolas": 15,
    "ball machine": 15,
    "diy": 12,
    "motor": 10,
    "rpm": 10,
    "impressao 3d": 10,
    "engenharia": 8,
    "lancador": 10,
    # Nível 3: Treinamento & Biomecânica (Ponte direta)
    "repeticao": 9,
    "treino": 8,
    "treinamento": 8,
    "saque": 7,
    "forehand": 7,
    "backhand": 7,
    "biomecanica": 8,
    "drills": 7,
    "consistencia": 6,
    # Nível 2: Tecnologia & Equipamentos
    "raquete": 5,
    "cordas": 5,
    "velocidade": 6,
    "sensor": 6,
    "tecnologia": 5,
    # Nível 1: Circuito Profissional (Topo de funil)
    "atp": 4,
    "wta": 3,
    "itf": 4,
    "alcaraz": 4,
    "sinner": 4,
    "djokovic": 4,
    "grand slam": 3,
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
