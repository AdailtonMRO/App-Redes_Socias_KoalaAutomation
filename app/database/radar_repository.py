from datetime import datetime, timezone, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.database.models import RadarRunModel, ResearchItemModel, ContentOpportunityModel
from app.research.models import ResearchItem, ContentOpportunity


class RadarRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_radar_run(
        self,
        profile_id: Optional[str],
        total_scanned: int,
        raw_items: List[ResearchItem],
        opportunities: List[ContentOpportunity]
    ) -> RadarRunModel:
        """Salva a execução do Radar, itens coletados e oportunidades no banco de dados."""
        radar_run = RadarRunModel(
            profile_id=profile_id,
            total_scanned=total_scanned
        )
        self.db.add(radar_run)
        self.db.flush()

        for item in raw_items:
            db_item = ResearchItemModel(
                id=item.id,
                radar_run_id=radar_run.id,
                source_name=item.source_name,
                source_type=item.source_type,
                title=item.title[:500],
                url=item.url,
                summary=item.summary,
                published_at=item.published_at,
                collected_at=item.collected_at
            )
            self.db.add(db_item)

        for opp in opportunities:
            db_opp = ContentOpportunityModel(
                id=opp.id,
                profile_id=profile_id,
                radar_run_id=radar_run.id,
                research_item_id=opp.research_item_id,
                headline=opp.headline[:500],
                theme=opp.theme[:255] if opp.theme else None,
                source_reference=opp.source_reference[:255] if opp.source_reference else None,
                pillar=opp.pillar[:100] if opp.pillar else None,
                relevance_score=opp.relevance_score,
                news_summary=opp.news_summary,
                key_takeaway=opp.key_takeaway,
                suggested_format=opp.suggested_format[:50] if opp.suggested_format else None,
                why_it_matters=opp.why_it_matters
            )
            self.db.add(db_opp)

        self.db.commit()
        self.db.refresh(radar_run)
        return radar_run

    def get_recent_headlines(self, profile_id: Optional[str] = None, days: int = 7) -> List[str]:
        """Recupera as manchetes recentes geradas para o perfil (ou global) para evitar repetições."""
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = select(ContentOpportunityModel.headline).where(
            ContentOpportunityModel.created_at >= threshold
        )
        
        if profile_id:
            query = query.where(ContentOpportunityModel.profile_id == profile_id)
            
        query = query.order_by(desc(ContentOpportunityModel.created_at)).limit(30)
        
        result = self.db.execute(query).scalars().all()
        return list(set(result))
