"""
Adapters de fontes de dados externas para o Content Radar.
"""
from app.research.adapters.google_trends import GoogleTrendsAdapter
from app.research.adapters.atp import ATPAdapter
from app.research.adapters.itf import ITFAdapter
from app.research.adapters.news import NewsAdapter

__all__ = [
    "GoogleTrendsAdapter",
    "ATPAdapter",
    "ITFAdapter",
    "NewsAdapter",
]
