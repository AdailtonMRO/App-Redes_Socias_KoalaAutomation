"""
Adapter para Notícias Esportivas, Tecnologia no Tênis e Treinamento (Google News RSS).
Monitora acontecimentos no Brasil e globalmente, cobrindo biomecânica,
treinamento repetitivo, equipamentos e inovações no tênis.
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import re
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
        limit: int = 15,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """
        Coleta notícias de tênis, treinamento e equipamentos via Google News RSS.
        """
        if keywords:
            query_str = " OR ".join(keywords[:5])
        else:
            # Query abrangente e dinâmica cobrindo astros atuais, circuito e treino
            query_str = 'tênis (ATP OR WTA OR "Bia Haddad" OR "João Fonseca" OR Alcaraz OR Sinner OR Djokovic OR treino OR raquete)'

        if geo == "BR":
            rss_url = f"https://news.google.com/rss/search?q={query_str}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        else:
            rss_url = f"https://news.google.com/rss/search?q={query_str}&hl=en-US&gl=US&ceid=US:en"

        items: List[ResearchItem] = []

        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 KoalaContentRadar/1.3"
                }
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

                        # Limpa sufixo da fonte caso presente
                        clean_title = re.sub(r"\s*-\s*[^-]+$", "", title_raw).strip() or title_raw

                        items.append(
                            ResearchItem(
                                source_name=f"News ({source_site})",
                                source_type="news",
                                title=clean_title,
                                url=link,
                                summary=desc or f"Publicação recente sobre tênis: {clean_title}",
                                published_at=pub_date,
                                language=language,
                                country=geo,
                                topics=["tennis", "training", "atp_wta", "competicao"],
                                raw_metrics={"source_outlet": source_site},
                            )
                        )
                else:
                    print(f"[WARN] NewsAdapter retornou status {resp.status_code}")
        except Exception as e:
            print(f"[ERROR] Falha ao coletar dados do NewsAdapter: {e}")

        return items
