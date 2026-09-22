"""
Modelos de Dados ORM e Enum de Estados
Implementa a máquina de estados e o esquema de tabelas especificado.
"""
from datetime import datetime, timezone
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from app.database.database import Base


class ContentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    GENERATING_SCRIPT = "GENERATING_SCRIPT"
    GENERATING_VIDEO = "GENERATING_VIDEO"
    PROCESSING_VIDEO = "PROCESSING_VIDEO"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    REGENERATING = "REGENERATING"
    APPROVED = "APPROVED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"
    ERROR = "ERROR"


def utc_now():
    return datetime.now(timezone.utc)


class ProfileModel(Base):
    __tablename__ = "profiles"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    username = Column(String(100), nullable=False)
    platform = Column(String(50), default="instagram")
    instagram_account_id = Column(String(100), nullable=True)
    config_json = Column(Text, nullable=False, default="{}")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    contents = relationship("ContentModel", back_populates="profile", cascade="all, delete-orphan")


class ContentModel(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    topic = Column(String(255), nullable=False)
    content_format = Column(String(30), default="REELS", nullable=False)  # REELS, STORIES, FEED, CAROUSEL
    script = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    status = Column(SQLEnum(ContentStatus), default=ContentStatus.DRAFT, nullable=False, index=True)
    current_version = Column(Integer, default=1)
    video_path = Column(String(500), nullable=True)
    thumbnail_path = Column(String(500), nullable=True)
    instagram_media_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    published_at = Column(DateTime, nullable=True)

    profile = relationship("ProfileModel", back_populates="contents")
    generations = relationship("GenerationModel", back_populates="content", cascade="all, delete-orphan")
    actions = relationship("ActionModel", back_populates="content", cascade="all, delete-orphan")
    metrics = relationship("ContentMetricModel", back_populates="content", uselist=False, cascade="all, delete-orphan")

class ContentMetricModel(Base):
    __tablename__ = "content_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, unique=True, index=True)
    instagram_media_id = Column(String(100), nullable=True)
    
    # Métricas
    plays = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saved = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    engagement_rate = Column(String(50), nullable=True)
    
    last_synced_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    created_at = Column(DateTime, default=utc_now)

    content = relationship("ContentModel", back_populates="metrics")


class GenerationModel(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    version = Column(Integer, default=1)
    prompt = Column(Text, nullable=True)
    gemini_operation_id = Column(String(200), nullable=True)
    video_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    content = relationship("ContentModel", back_populates="generations")


class ActionModel(Base):
    __tablename__ = "actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # PUBLISH, REGENERATE, EDIT, REJECT
    telegram_user_id = Column(String(100), nullable=True)
    metadata_info = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    content = relationship("ContentModel", back_populates="actions")


class RadarRunModel(Base):
    __tablename__ = "radar_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=True, index=True)
    total_scanned = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    research_items = relationship("ResearchItemModel", back_populates="radar_run", cascade="all, delete-orphan")
    opportunities = relationship("ContentOpportunityModel", back_populates="radar_run", cascade="all, delete-orphan")


class ResearchItemModel(Base):
    __tablename__ = "research_items"

    id = Column(String(100), primary_key=True, index=True)
    radar_run_id = Column(Integer, ForeignKey("radar_runs.id"), nullable=False, index=True)
    source_name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    published_at = Column(String(100), nullable=True)
    collected_at = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    radar_run = relationship("RadarRunModel", back_populates="research_items")


class ContentOpportunityModel(Base):
    __tablename__ = "content_opportunities"

    id = Column(String(100), primary_key=True, index=True)
    profile_id = Column(String(50), ForeignKey("profiles.id"), nullable=True, index=True)
    radar_run_id = Column(Integer, ForeignKey("radar_runs.id"), nullable=False, index=True)
    research_item_id = Column(String(100), ForeignKey("research_items.id"), nullable=True)
    headline = Column(String(500), nullable=False)
    theme = Column(String(255), nullable=True)
    source_reference = Column(String(255), nullable=True)
    pillar = Column(String(100), nullable=True)
    relevance_score = Column(Integer, default=0)
    news_summary = Column(Text, nullable=True)
    key_takeaway = Column(Text, nullable=True)
    suggested_format = Column(String(50), nullable=True)
    why_it_matters = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    radar_run = relationship("RadarRunModel", back_populates="opportunities")
