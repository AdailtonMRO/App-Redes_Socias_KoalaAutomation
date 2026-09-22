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
    """Valida que notícias de astros brasileiros e grandes torneios recebem maior pontuação."""
    star_item = ResearchItem(
        source_name="TenisBrasil",
        source_type="specialized_news",
        title="João Fonseca supera rodada e crava forehand com grande vitória",
    )
    generic_item = ResearchItem(
        source_name="Blog",
        source_type="news",
        title="Clube realiza manutenção de quadras no feriado",
    )

    score_star = ResearchScorer.calculate_item_score(star_item)
    score_generic = ResearchScorer.calculate_item_score(generic_item)

    assert score_star > score_generic
    assert score_star >= 30.0



def test_api_radar_daily_endpoint():
    """Valida o endpoint GET /api/radar/daily."""
    resp = client.get("/api/radar/daily?top_k=2")
    assert resp.status_code == 200
    data = resp.json()
    assert "date" in data
    assert "total_scanned" in data
    assert "top_opportunities" in data
    assert isinstance(data["top_opportunities"], list)


def test_new_brazilian_adapters_registered():
    """Valida que todos os novos adapters especializados estão integrados."""
    from app.research.radar import ContentRadar
    from app.research.adapters.brazilian_tennis import BrazilianTennisAdapter
    from app.research.adapters.sports_portals import SportsPortalsAdapter
    from app.research.adapters.wta_cbt import WTAAndCBTAdapter

    radar = ContentRadar()
    adapter_types = [type(a) for a in radar.adapters]

    assert BrazilianTennisAdapter in adapter_types
    assert SportsPortalsAdapter in adapter_types
    assert WTAAndCBTAdapter in adapter_types
    assert len(radar.adapters) >= 7


def test_api_radar_daily_refresh_param():
    """Valida que o endpoint aceita o parâmetro refresh."""
    resp = client.get("/api/radar/daily?top_k=2&refresh=true")
    assert resp.status_code == 200
    data = resp.json()
    assert "top_opportunities" in data


def test_content_opportunity_schema_stories():
    """Valida que o ContentOpportunity tem formato STORIES e campos de resumo sem máquina de bolas."""
    opp = ContentOpportunity(
        headline="João Fonseca brilha com forehand de 160km/h",
        theme="Destaque Brasileiro",
        source_reference="TenisBrasil (UOL)",
        pillar="🇧🇷 Brasil no Circuito",
        relevance_score=9,
        news_summary="O brasileiro dominou os pontos de fundo e venceu com autoridade.",
        key_takeaway="Consolidação no top 100 mundial.",
        why_it_matters="Alta relevância esportiva.",
    )
    assert opp.suggested_format == "STORIES"
    assert opp.news_summary is not None
    dump = opp.model_dump()
    assert "diy_ball_machine_angle" not in dump


