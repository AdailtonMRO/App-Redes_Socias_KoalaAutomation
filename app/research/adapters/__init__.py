"""
Adapters de fontes de dados externas para o Content Radar.
"""
from app.research.adapters.google_trends import GoogleTrendsAdapter
from app.research.adapters.atp import ATPAdapter
from app.research.adapters.itf import ITFAdapter
from app.research.adapters.news import NewsAdapter
from app.research.adapters.brazilian_tennis import BrazilianTennisAdapter
from app.research.adapters.sports_portals import SportsPortalsAdapter
from app.research.adapters.wta_cbt import WTAAndCBTAdapter

__all__ = [
    "GoogleTrendsAdapter",
    "ATPAdapter",
    "ITFAdapter",
    "NewsAdapter",
    "BrazilianTennisAdapter",
    "SportsPortalsAdapter",
    "WTAAndCBTAdapter",
]

