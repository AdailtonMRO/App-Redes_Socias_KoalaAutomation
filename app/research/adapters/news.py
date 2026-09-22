"""
Adapter para Notícias Esportivas, Tecnologia no Tênis e Treinamento (Google News RSS).
Monitora acontecimentos no Brasil e globalmente, cobrindo biomecânica,
treinamento repetitivo, equipamentos e inovações no tênis.
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem


class NewsAdapter(SourceAdapter):
    """Adapter para notícias gerais, tecnologia esportiva e treinamento no tênis."""

    @property
    def name(self) -> str:
        return "Notícias & Tecnologia Esportiva"

    @property
    def source_type(self) -> str:
        return "news"

    def is_available(self) -> bool:
        return True

    async def fetch_items(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 10,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """
        Coleta notícias de tênis, treinamento e equipamentos via Google News RSS.
        """
        # Tópicos padrão calibrados para o universo Koala Tênis (Tênis + Treinamento + Tecnologia)
        default_queries = [
            "tenis treino repeticao",
            "maquina de bolas tenis",
            "biomecanica tenis saque",
            "tecnologia raquete cordas tenis",
        ]
        active_queries = keywords or default_queries
        query_str = " OR ".join([f'"{q}"' if " " in q else q for q in active_queries[:4]])

        if geo == "BR":
            rss_url = f"https://news.google.com/rss/search?q={query_str}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        else:
            rss_url = f"https://news.google.com/rss/search?q={query_str}&hl=en-US&gl=US&ceid=US:en"

        items: List[ResearchItem] = []

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) KoalaContentRadar/1.0"}
                resp = await client.get(rss_url, headers=headers)

                if resp.status_code == 200:
                    root = ET.fromstring(resp.content)
                    xml_items = root.findall("./channel/item")

                    for elem in xml_items[:limit]:
                        title_raw = elem.find("title").text if elem.find("title") is not None else ""
                        link = elem.find("link").text if elem.find("link") is not None else ""
                        pub_date = elem.find("pubDate").text if elem.find("pubDate") is not None else None
                        desc = elem.find("description").text if elem.find("description") is not None else ""
                        source_elem = elem.find("source")
                        source_site = source_elem.text if source_elem is not None else "Google News"

                        if not title_raw:
                            continue

                        items.append(
                            ResearchItem(
                                source_name=f"News ({source_site})",
                                source_type="news",
                                title=title_raw,
                                url=link,
                                summary=desc or f"Publicação recente sobre tênis e equipamentos: {title_raw}",
                                published_at=pub_date,
                                language=language,
                                country=geo,
                                topics=["tennis", "training", "technology", "diy"],
                                raw_metrics={"source_outlet": source_site},
                            )
                        )
                else:
                    print(f"[WARN] NewsAdapter retornou status {resp.status_code}")
        except Exception as e:
            print(f"[ERROR] Falha ao coletar dados do NewsAdapter: {e}")

        return items
