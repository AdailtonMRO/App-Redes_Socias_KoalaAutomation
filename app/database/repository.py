"""
Camada de Repositório (Repository Pattern)
Isola o acesso a dados da lógica de negócio, facilitando testes e futura migração para PostgreSQL.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import ProfileModel, ContentModel, GenerationModel, ActionModel, ContentStatus


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, profile_id: str) -> Optional[ProfileModel]:
        return self.db.query(ProfileModel).filter(ProfileModel.id == profile_id).first()

    def list_all(self, active_only: bool = True) -> List[ProfileModel]:
        query = self.db.query(ProfileModel)
        if active_only:
            query = query.filter(ProfileModel.active.is_(True))
        return query.all()

    def upsert(self, profile_id: str, name: str, username: str, config_json: str, instagram_account_id: Optional[str] = None) -> ProfileModel:
        profile = self.get_by_id(profile_id)
        if not profile:
            profile = ProfileModel(
                id=profile_id,
                name=name,
                username=username,
                config_json=config_json,
                instagram_account_id=instagram_account_id,
            )
            self.db.add(profile)
        else:
            profile.name = name
            profile.username = username
            profile.config_json = config_json
            if instagram_account_id:
                profile.instagram_account_id = instagram_account_id
        self.db.commit()
        self.db.refresh(profile)
        return profile


class ContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, profile_id: str, topic: str, title: Optional[str] = None) -> ContentModel:
        content = ContentModel(
            profile_id=profile_id,
            topic=topic,
            title=title or topic,
            status=ContentStatus.DRAFT,
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def get_by_id(self, content_id: int) -> Optional[ContentModel]:
        return self.db.query(ContentModel).filter(ContentModel.id == content_id).first()

    def update_status(self, content_id: int, status: ContentStatus) -> Optional[ContentModel]:
        content = self.get_by_id(content_id)
        if content:
            content.status = status
            self.db.commit()
            self.db.refresh(content)
        return content

    def list_waiting_approval(self) -> List[ContentModel]:
        return self.db.query(ContentModel).filter(ContentModel.status == ContentStatus.WAITING_APPROVAL).all()

    def list_recent(self, limit: int = 10) -> List[ContentModel]:
        return self.db.query(ContentModel).order_by(ContentModel.created_at.desc()).limit(limit).all()
