from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import ContentMetricModel


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_metrics(self, content_id: int, metrics_data: Dict[str, Any], instagram_media_id: Optional[str] = None) -> ContentMetricModel:
        """
        Atualiza ou cria o registro de métricas para um dado content_id.
        """
        metric = self.db.query(ContentMetricModel).filter(ContentMetricModel.content_id == content_id).first()
        
        if not metric:
            metric = ContentMetricModel(content_id=content_id)
            self.db.add(metric)
        
        if instagram_media_id:
            metric.instagram_media_id = instagram_media_id
            
        metric.plays = metrics_data.get("plays", metric.plays)
        metric.likes = metrics_data.get("likes", metric.likes)
        metric.comments = metrics_data.get("comments", metric.comments)
        metric.shares = metrics_data.get("shares", metric.shares)
        metric.saved = metrics_data.get("saved", metric.saved)
        metric.reach = metrics_data.get("reach", metric.reach)
        
        # Calcular taxa de engajamento básica (se houver views/reach)
        total_interactions = metric.likes + metric.comments + metric.shares + metric.saved
        base_view = metric.reach or metric.plays
        if base_view and base_view > 0:
            rate = (total_interactions / base_view) * 100
            metric.engagement_rate = f"{rate:.2f}%"
            
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_metrics(self, content_id: int) -> Optional[ContentMetricModel]:
        return self.db.query(ContentMetricModel).filter(ContentMetricModel.content_id == content_id).first()
