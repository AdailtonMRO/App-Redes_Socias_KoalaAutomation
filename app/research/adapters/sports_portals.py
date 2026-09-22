"""
Adapter para Grandes Portais de Esportes no Brasil.
Coleta matérias de tênis em tempo real de:
- ge.globo (Tênis)
- ESPN Brasil (Tênis)
- UOL Esporte (Tênis)
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import html
import re
import urllib.parse
import httpx

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem


class SportsPortalsAdapter(SourceAdapter):
    """Adapter para cobertura de tênis nos grandes portais de mídia esportiva no Brasil."""

    PORTALS = [
        {
            "name": "ge.globo Tênis",
            "query": "site:ge.globo.com tenis",
            "weight": 1.3,
        },
        {
            "name": "ESPN Brasil Tênis",
            "query": "site:espn.com.br tenis",
            "weight": 1.2,
        },
        {
            "name": "UOL Esporte Tênis",
            "query": "site:uol.com.br/esporte tenis",
            "weight": 1.1,
        },
    ]

    @property
    def name(self) -> str:
        return "Grandes Portais de Esportes (ge.globo, ESPN, UOL)"

    @property
    def source_type(self) -> str:
        return "sports_portals"

    def is_available(self) -> bool:
        return True

    def _clean_html(self, raw_html: str) -> str:
        if not raw_html:
            return ""
        clean = re.sub(r"<[^>]+>", " ", raw_html)
        clean = html.unescape(clean)
        return " ".join(clean.split())[:300]

    async def fetch_items(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 15,
        geo: str = "BR",
        language: str = "pt",
    ) -> List[ResearchItem]:
        """Coleta notícias de tênis filtradas por grandes portais esportivos."""
        items: List[ResearchItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 KoalaContentRadar/1.3"
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for portal in self.PORTALS:
                portal_name = portal["name"]
                query_str = portal["query"]
                weight = portal["weight"]

                encoded_query = urllib.parse.quote(query_str)
                rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

                try:
                    resp = await client.get(rss_url, headers=headers)
                    if resp.status_code != 200:
                        continue

                    root = ET.fromstring(resp.content)
                    xml_items = root.findall(".//item")

                    for elem in xml_items[:8]:
                        title_elem = elem.find("title")
                        link_elem = elem.find("link")
                        pub_date_elem = elem.find("pubDate")
                        desc_elem = elem.find("description")

                        raw_title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                        pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else None
                        raw_desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                        clean_desc = self._clean_html(raw_desc)

                        if not raw_title:
                            continue

                        # O Google News frequentemente adiciona " - Nome da Fonte" no fim do título
                        title = re.sub(r"\s*-\s*[^-]+$", "", raw_title).strip()
                        if not title:
                            title = raw_title

                        if keywords:
                            title_lower = title.lower()
                            if not any(k.lower() in title_lower for k in keywords):
                                continue

                        items.append(
                            ResearchItem(
                                source_name=portal_name,
                                source_type="sports_portals",
                                title=title,
                                url=link,
                                summary=clean_desc or f"Notícia esportiva de tênis via {portal_name}: {title}",
                                published_at=pub_date,
                                language=language,
                                country=geo,
                                topics=["tenis_brasil", "esporte_nacional", "grand_slam", "atp_wta"],
                                raw_metrics={"source_weight": weight, "outlet": portal_name},
                            )
                        )
                except Exception as e:
                    print(f"[WARN] Falha ao coletar notícias de {portal_name}: {e}")

        return items[:limit]
