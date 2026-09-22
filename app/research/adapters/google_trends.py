"""
Adapter para o Google Trends.
Isola totalmente a biblioteca pytrends e fornece fallback resiliente via RSS oficial
para garantir que o restante do sistema nunca dependa de detalhes de implementação.
"""
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
import httpx

from app.research.sources import TrendsProvider
from app.research.models import ResearchItem

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False


class GoogleTrendsAdapter(TrendsProvider):
    """Provedor de inteligência de tendências via Google Trends."""

    def __init__(self, hl: str = "pt-BR", tz: int = 180):
        self.hl = hl
        self.tz = tz
        self._pytrends_client = None

    @property
    def name(self) -> str:
        return "Google Trends"

    @property
    def source_type(self) -> str:
        return "trends"

    def is_available(self) -> bool:
        return True  # Sempre disponível pois possui fallback RSS

    def _get_pytrends_client(self):
        if self._pytrends_client is None and PYTRENDS_AVAILABLE:
            try:
                self._pytrends_client = TrendReq(hl=self.hl, tz=self.tz, timeout=(10, 25))
            except Exception as e:
                print(f"[WARN] Falha ao inicializar TrendReq: {e}")
        return self._pytrends_client

    async def get_rising_queries(
        self,
        keyword: str,
        geo: str = "BR",
        timeframe: str = "now 7-d",
    ) -> List[Dict[str, Any]]:
        """Busca consultas em ascensão para uma palavra-chave."""
        client = self._get_pytrends_client()
        if not client:
            return []

        def _sync_fetch():
            try:
                client.build_payload([keyword], cat=0, timeframe=timeframe, geo=geo)
                rq = client.related_queries()
                kw_data = rq.get(keyword, {})
                rising = kw_data.get("rising")
                if rising is not None and not rising.empty:
                    return rising.head(10).to_dict(orient="records")
                return []
            except Exception as e:
                print(f"[WARN] Erro pytrends related_queries para '{keyword}': {e}")
                return []

        return await asyncio.to_thread(_sync_fetch)

    async def get_related_topics(
        self,
        keyword: str,
        geo: str = "BR",
    ) -> List[Dict[str, Any]]:
        """Busca tópicos relacionados para uma palavra-chave."""
        client = self._get_pytrends_client()
        if not client:
            return []

        def _sync_fetch():
            try:
                client.build_payload([keyword], cat=0, timeframe="now 7-d", geo=geo)
                rt = client.related_topics()
                kw_data = rt.get(keyword, {})
                rising = kw_data.get("rising")
                if rising is not None and not rising.empty:
                    return rising.head(10).to_dict(orient="records")
                return []
            except Exception as e:
                print(f"[WARN] Erro pytrends related_topics para '{keyword}': {e}")
                return []

        return await asyncio.to_thread(_sync_fetch)

    async def fetch_rss_trending(self, geo: str = "BR", limit: int = 5) -> List[ResearchItem]:
        """Fallback via RSS oficial do Google Trends."""
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        items: List[ResearchItem] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as http:
                resp = await http.get(url)
                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    for xml_item in root.findall("./channel/item")[:limit]:
                        title = xml_item.find("title").text if xml_item.find("title") is not None else "Trend"
                        link = xml_item.find("link").text if xml_item.find("link") is not None else ""
                        pub_date = xml_item.find("pubDate").text if xml_item.find("pubDate") is not None else None
                        items.append(
                            ResearchItem(
                                source_name="Google Trends (RSS)",
                                source_type="trends",
                                title=f"Tendência em Alta: {title}",
                                url=link,
                                summary=f"Termo em alta recente no Google Trends ({geo}).",
                                published_at=pub_date,
                                language="pt" if geo == "BR" else "en",
                                country=geo,
                                topics=["trends", "search-volume"],
                                raw_metrics={"source": "rss_fallback"},
                            )
                        )
        except Exception as e:
            print(f"[WARN] Erro no fallback RSS do Google Trends: {e}")
        return items

    async def fetch_items(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 10,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """Executa a coleta normalizada de dados de tendências."""
        target_keywords = keywords or ["tennis", "saque tenis", "raquete tenis", "treino tenis"]
        collected: List[ResearchItem] = []

        for kw in target_keywords:
            rising = await self.get_rising_queries(kw, geo=geo)
            for row in rising:
                query_name = row.get("query", "")
                growth_value = row.get("value", 0)
                if not query_name:
                    continue

                item = ResearchItem(
                    source_name="Google Trends",
                    source_type="trends",
                    title=f"Busca em Alta: '{query_name}' (relacionado a '{kw}')",
                    url=f"https://trends.google.com/trends/explore?q={query_name}&geo={geo}",
                    summary=f"Crescimento repentino de interesse detectado no Google Trends para '{query_name}'.",
                    language=language,
                    country=geo,
                    topics=["tennis", "trends", kw.lower()],
                    raw_metrics={"growth_rate": growth_value, "seed_keyword": kw},
                )
                collected.append(item)
                if len(collected) >= limit:
                    return collected

        # Se pytrends não retornou dados (ex: rate limit ou poucas buscas), ativa fallback RSS
        if not collected:
            collected = await self.fetch_rss_trending(geo=geo, limit=limit)

        return collected
