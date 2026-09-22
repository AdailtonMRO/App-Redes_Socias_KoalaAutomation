"""
Adapter para Circuito Feminino (WTA) e Confederação Brasileira de Tênis (CBT).
Coleta notícias atualizadas sobre Bia Haddad Maia, Luisa Stefani, circuito feminino
e competições nacionais/juvenis da CBT via feeds segmentados do Google News.
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import html
import re
import urllib.parse
import httpx

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem


class WTAAndCBTAdapter(SourceAdapter):
    """Adapter dedicado ao tênis feminino (WTA) e tênis nacional/juvenil (CBT)."""

    FEEDS = [
        {
            "name": "WTA & Tênis Feminino BR",
            "query": 'tênis ("Bia Haddad" OR "Beatriz Haddad" OR "Luisa Stefani" OR "Laura Pigossi" OR WTA)',
            "weight": 1.2,
            "topics": ["wta", "tenis_feminino", "bia_haddad", "brasil_no_tenis"],
        },
        {
            "name": "CBT & Tênis Nacional / Juvenil",
            "query": 'tênis ("CBT" OR "Confederação Brasileira de Tênis" OR "Copa Davis" OR "Billie Jean King Cup" OR "juvenil")',
            "weight": 1.1,
            "topics": ["cbt", "juvenis", "copa_davis", "base_nacional"],
        },
    ]

    @property
    def name(self) -> str:
        return "WTA & Confederação Brasileira de Tênis (CBT)"

    @property
    def source_type(self) -> str:
        return "wta_cbt"

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
        """Coleta notícias de WTA e CBT."""
        items: List[ResearchItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 KoalaContentRadar/1.3"
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for feed in self.FEEDS:
                feed_name = feed["name"]
                query_str = feed["query"]
                weight = feed["weight"]
                topics = feed["topics"]

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

                        title = re.sub(r"\s*-\s*[^-]+$", "", raw_title).strip()
                        if not title:
                            title = raw_title

                        if keywords:
                            title_lower = title.lower()
                            if not any(k.lower() in title_lower for k in keywords):
                                continue

                        items.append(
                            ResearchItem(
                                source_name=feed_name,
                                source_type="wta_cbt",
                                title=title,
                                url=link,
                                summary=clean_desc or f"Notícia via {feed_name}: {title}",
                                published_at=pub_date,
                                language=language,
                                country=geo,
                                topics=topics,
                                raw_metrics={"source_weight": weight, "outlet": feed_name},
                            )
                        )
                except Exception as e:
                    print(f"[WARN] Falha ao coletar notícias de {feed_name}: {e}")

        return items[:limit]
