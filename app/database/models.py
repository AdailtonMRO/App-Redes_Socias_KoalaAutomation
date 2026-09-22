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
