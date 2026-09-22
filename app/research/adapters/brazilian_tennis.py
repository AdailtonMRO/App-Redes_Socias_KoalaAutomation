"""
Adapter para Portais Especializados de Tênis no Brasil.
Coleta matérias em tempo real via feeds RSS nativos de:
- TenisBrasil (UOL)
- Tenis News
- Diário do Tênis
"""
from typing import List, Optional
import xml.etree.ElementTree as ET
import html
import re
import httpx

from app.research.sources import SourceAdapter
from app.research.models import ResearchItem


class BrazilianTennisAdapter(SourceAdapter):
    """Adapter para os principais portais dedicados de tênis no Brasil."""

    FEEDS = [
        {
            "name": "TenisBrasil (UOL)",
            "url": "https://tenisbrasil.uol.com.br/feed/",
            "weight": 1.2,
        },
        {
            "name": "Tenis News",
            "url": "https://www.tenisnews.com.br/feed",
            "weight": 1.2,
        },
        {
            "name": "Diário do Tênis",
            "url": "https://diariodotenis.com.br/feed/",
            "weight": 1.0,
        },
    ]

    @property
    def name(self) -> str:
        return "Portais Especializados de Tênis (Brasil)"

    @property
    def source_type(self) -> str:
        return "specialized_news"

    def is_available(self) -> bool:
        return True

    def _clean_html(self, raw_html: str) -> str:
        """Remove tags HTML e decodifica entidades para gerar texto limpo."""
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
        """Coleta notícias dos portais especializados brasileiros de tênis."""
        items: List[ResearchItem] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 KoalaContentRadar/1.3"
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            for feed in self.FEEDS:
                feed_name = feed["name"]
                feed_url = feed["url"]
                weight = feed["weight"]

                try:
                    resp = await client.get(feed_url, headers=headers)
                    if resp.status_code != 200:
                        continue

                    root = ET.fromstring(resp.content)
                    xml_items = root.findall(".//item")

                    for elem in xml_items[:8]:
                        title_elem = elem.find("title")
                        link_elem = elem.find("link")
                        pub_date_elem = elem.find("pubDate")
                        desc_elem = elem.find("description")

                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                        pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else None
                        raw_desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                        clean_desc = self._clean_html(raw_desc)

                        if not title:
                            continue

                        # Se keywords forem passadas, filtra se houver interseção
                        if keywords:
                            title_lower = title.lower()
                            if not any(k.lower() in title_lower for k in keywords):
                                continue

                        items.append(
                            ResearchItem(
                                source_name=feed_name,
                                source_type="specialized_news",
                                title=title,
                                url=link,
                                summary=clean_desc or f"Notícia de tênis via {feed_name}: {title}",
                                published_at=pub_date,
                                language=language,
                                country=geo,
                                topics=["tenis_brasil", "competicao", "profissionais", "treinamento"],
                                raw_metrics={"source_weight": weight, "outlet": feed_name},
                            )
                        )
                except Exception as e:
                    print(f"[WARN] Falha ao coletar feed de {feed_name}: {e}")

        # Retorna limitado ao limite solicitado
        return items[:limit]
