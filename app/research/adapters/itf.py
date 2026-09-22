"""
Adapter para a International Tennis Federation (ITF).
Focado em regras oficiais, especificações de equipamentos, regulamentos de bolas/raquetes
e competições sob a chancela da federação internacional.
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import httpx

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem


class ITFAdapter(SourceAdapter):
    """Adapter para regras, equipamentos e notícias oficiais da ITF Tennis."""

    @property
    def name(self) -> str:
        return "ITF Tennis"

    @property
    def source_type(self) -> str:
        return "official"

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
        Coleta informações e regulamentos oficiais da ITF via feed estruturado.
        """
        query = "site:itftennis.com"
        if keywords:
            query += f" ({' OR '.join(keywords)})"

        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
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

                        clean_title = title_raw.replace(" - itftennis.com", "").strip()
                        if not clean_title:
                            continue

                        items.append(
                            ResearchItem(
                                source_name="ITF Tennis",
                                source_type="official",
                                title=clean_title,
                                url=link,
                                summary=desc or f"Regulamento e notícias oficiais da ITF: {clean_title}",
                                published_at=pub_date,
                                language="en",
                                country="US",
                                topics=["itf", "rules", "regulations", "equipment"],
                                raw_metrics={"domain": "itftennis.com"},
                            )
                        )
                else:
                    print(f"[WARN] ITFAdapter retornou status {resp.status_code}")
        except Exception as e:
            print(f"[ERROR] Falha ao coletar dados do ITFAdapter: {e}")

        return items
