"""
Testes unitários e de integração para o Content Radar.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.research.models import ResearchItem, ContentOpportunity
from app.research.verification import ItemVerifier
from app.research.scoring import ResearchScorer
from app.research.adapters.news import NewsAdapter
from app.research.adapters.atp import ATPAdapter

client = TestClient(app)


def test_research_item_normalization():
    """Valida o schema uniforme do ResearchItem."""
    item = ResearchItem(
        source_name="ATP Tour",
        source_type="official",
        title="Alcaraz wins semifinal",
        url="https://atptour.com/news/123",
        summary="Resumo da partida",
        topics=["tennis", "atp"],
    )
    compact = item.to_compact_dict()
    assert compact["title"] == "Alcaraz wins semifinal"
    assert "ATP Tour" in compact["source"]
    assert item.id is not None


def test_item_verifier_filters_spam():
    """Valida que o sanitizador remove spam e apostas."""
    spam_item = ResearchItem(
        source_name="Blog",
        source_type="news",
        title="Ganhe bônus de cadastro no tigrinho aposta online",
    )
    valid_item = ResearchItem(
        source_name="ATP Tour",
        source_type="official",
        title="Novo recorde de velocidade de saque no tênis profissional",
    )

    assert not ItemVerifier.is_valid(spam_item)
    assert ItemVerifier.is_valid(valid_item)


def test_research_scorer_affinity():
    """Valida que itens relacionados a máquinas e treino recebem maior pontuação."""
    machine_item = ResearchItem(
        source_name="News",
        source_type="news",
        title="Como regular o motor e RPM de uma máquina de bolas de tênis DIY",
    )
    generic_item = ResearchItem(
        source_name="ATP",
        source_type="official",
        title="Jogador descansa antes do próximo torneio",
    )

    score_machine = ResearchScorer.calculate_item_score(machine_item)
    score_generic = ResearchScorer.calculate_item_score(generic_item)

    assert score_machine > score_generic
    assert score_machine >= 35.0  # Pontuação acumulada pelos pesos DIY


def test_api_radar_daily_endpoint():
    """Valida o endpoint GET /api/radar/daily."""
    resp = client.get("/api/radar/daily?top_k=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    assert "total_scanned" in data
    assert "top_opportunities" in data
    assert isinstance(data["top_opportunities"], list)
