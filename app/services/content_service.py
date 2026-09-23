"""
Orquestrador Central de Conteúdo Multi-Formato (Content Service)
Coordena o fluxo completo para Instagram:
- Reels (Vídeo 9:16)
- Stories (Vertical 9:16)
- Feed (Post Quadrado 1:1)
- Carrossel (Multi-Slides 1:1)
Fluxo: Perfil + Tema + Formato -> Gemini IA -> FFmpeg/Veo -> Telegram (Aprovação Humana) -> Meta Graph API.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.config import get_settings, BASE_DIR
from app.profiles.manager import ProfileManager
from app.database.database import SessionLocal
from app.database.models import ContentStatus, ContentModel, GenerationModel, ActionModel
from app.ai.gemini import GeminiClient
from app.ai.video_generator import VideoGeneratorService
from app.video.ffmpeg import FFmpegProcessor
from app.instagram.client import MetaGraphClient

settings = get_settings()


class ContentOrchestrator:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.gemini = GeminiClient()
        self.video_gen = VideoGeneratorService()
        self.ffmpeg = FFmpegProcessor()
        self.media_base_dir = Path(settings.DATA_DIR) / "media"
        self.media_base_dir.mkdir(parents=True, exist_ok=True)

    async def create_new_content(
        self,
        profile_id: str,
        topic: str,
        content_format: str = "REELS",
        user_id: Optional[str] = None,
        telegram_notifier=None,
        chat_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executa a geração completa do conteúdo estruturado e de suas mídias
        de acordo com o formato escolhido (REELS, STORIES, FEED ou CAROUSEL).
        """
        fmt = content_format.upper()
        profile = self.profile_manager.get_profile(profile_id)
        if not profile:
            return {"success": False, "error": f"Perfil '{profile_id}' não encontrado"}

        db = SessionLocal()
        try:
            # 1. Cria registro inicial no banco com status GENERATING_SCRIPT
            content = ContentModel(
                profile_id=profile_id,
                topic=topic,
                content_format=fmt,
                status=ContentStatus.GENERATING_SCRIPT,
            )
            db.add(content)
            db.commit()
            db.refresh(content)
            content_id = content.id

            # 2. Chama a IA (Google Gemini) para gerar roteiro e estrutura tipada
            profile_dict = profile.model_dump()
            gemini_res = await self.gemini.generate_content(profile_dict, topic, fmt)
            script_data = gemini_res.get("data", {})

            # 3. Processamento de Mídia por Formato
            logo_path = None
            if profile and profile.logo_path:
                cand = Path(profile.logo_path)
                if not cand.is_absolute():
                    cand = BASE_DIR / cand
                if cand.exists():
                    logo_path = str(cand)
            if not logo_path:
                default_cand = BASE_DIR / "profiles" / "koalatenis_logo.png"
                if default_cand.exists():
                    logo_path = str(default_cand)

            if fmt == "CAROUSEL":
                # --- FORMATO CARROSSEL (SLIDES 1:1) ---
                content.title = script_data.get("title", f"Carrossel: {topic}")
                content.caption = script_data.get("caption", "")
                content.hashtags = json.dumps(script_data.get("hashtags", []))
                content.status = ContentStatus.PROCESSING_VIDEO
                db.commit()

                slides = script_data.get("slides", [])
                carousel_dir = self.media_base_dir / f"carousel_{content_id}"
                carousel_dir.mkdir(parents=True, exist_ok=True)

                slide_paths: List[str] = []
                total_slides = len(slides)

                for idx, s in enumerate(slides):
                    slide_num = idx + 1
                    slide_path = str(carousel_dir / f"slide_{slide_num}.jpg")
                    bg_path = str(carousel_dir / f"bg_{slide_num}.jpg")
                    v_prompt = s.get("visual_prompt") or f"{topic}, tennis instruction slide {slide_num}"

                    # Gera imagem fotográfica contextual por IA
                    await self.gemini.generate_image(
                        prompt=v_prompt,
                        aspect_ratio="1:1",
                        output_path=bg_path,
                        keywords=f"tennis,tutorial,slide_{slide_num}",
                    )

                    # Sobrepõe layout institucional via FFmpeg
                    self.ffmpeg.generate_square_slide_image(
                        output_path=slide_path,
                        headline=s.get("slide_title") or s.get("title", f"Passo {slide_num}"),
                        body_text=s.get("slide_body") or s.get("body", ""),
                        slide_num=slide_num,
                        total_slides=total_slides,
                        brand_name=profile.name,
                        background_image=bg_path,
                        logo_path=logo_path,
                    )
                    slide_paths.append(slide_path)

                script_data["slide_paths"] = slide_paths
                content.thumbnail_path = slide_paths[0] if slide_paths else None
                content.script = json.dumps(script_data, ensure_ascii=False)
                content.status = ContentStatus.WAITING_APPROVAL
                db.commit()

            elif fmt == "FEED":
                # --- FORMATO POST DE FEED (1:1) ---
                content.title = script_data.get("title", f"Post: {topic}")
                content.caption = script_data.get("caption", "")
                content.hashtags = json.dumps(script_data.get("hashtags", []))
                content.status = ContentStatus.PROCESSING_VIDEO
                db.commit()

                feed_path = str(self.media_base_dir / f"feed_{content_id}.jpg")
                bg_feed_path = str(self.media_base_dir / f"bg_feed_{content_id}.jpg")
                v_prompt = script_data.get("visual_prompt") or f"{topic}, high quality action photography"

                # Gera imagem temática com IA
                await self.gemini.generate_image(
                    prompt=v_prompt,
                    aspect_ratio="1:1",
                    output_path=bg_feed_path,
                    keywords="tennis,action,player",
                )

                self.ffmpeg.generate_square_slide_image(
                    output_path=feed_path,
                    headline=script_data.get("headline", topic),
                    body_text=script_data.get("cta", ""),
                    brand_name=profile.name,
                    background_image=bg_feed_path,
                    logo_path=logo_path,
                )

                content.thumbnail_path = feed_path if Path(feed_path).exists() else None
                content.script = json.dumps(script_data, ensure_ascii=False)
                content.status = ContentStatus.WAITING_APPROVAL
                db.commit()

            elif fmt == "STORIES":
                # --- FORMATO STORIES (9:16) ---
                content.title = script_data.get("title", f"Story: {topic[:40]}")
                content.caption = script_data.get("body") or script_data.get("summary") or ""
                content.hashtags = json.dumps([])
                content.status = ContentStatus.PROCESSING_VIDEO
                db.commit()

                story_path = str(self.media_base_dir / f"story_{content_id}.jpg")
                bg_story_path = str(self.media_base_dir / f"bg_story_{content_id}.jpg")
                v_prompt = script_data.get("visual_prompt") or f"{topic}, vertical 9:16 tennis court championship action"

                # Gera imagem vertical temática com IA
                await self.gemini.generate_image(
                    prompt=v_prompt,
                    aspect_ratio="9:16",
                    output_path=bg_story_path,
                    keywords="tennis,court,championship,action",
                )

                hook_text = script_data.get("hook") or script_data.get("headline") or script_data.get("title") or topic
                body_text = script_data.get("body") or script_data.get("summary") or script_data.get("news_summary") or topic
                cta_text = script_data.get("call_to_action") or profile.cta or "Deixe seu comentário!"

                self.ffmpeg.generate_story_vertical_image(
                    output_path=story_path,
                    hook=hook_text,
                    body_text=body_text,
                    cta=cta_text,
                    brand_name=profile.name,
                    background_image=bg_story_path,
                    logo_path=logo_path,
                )

                content.thumbnail_path = story_path if Path(story_path).exists() else None
                content.script = json.dumps(script_data, ensure_ascii=False)
                content.status = ContentStatus.WAITING_APPROVAL
                db.commit()

            else:
                # --- FORMATO REELS PADRÃO (VÍDEO 9:16) ---
                content.title = script_data.get("title", topic)
                content.caption = script_data.get("caption", "")
                content.hashtags = json.dumps(script_data.get("hashtags", []))
                content.status = ContentStatus.GENERATING_VIDEO
                db.commit()

                video_res = await self.video_gen.generate_reel_video(
                    content_id=content_id,
                    script_data=script_data,
                    brand_name=profile.name,
                    telegram_notifier=telegram_notifier,
                    chat_id=chat_id,
                    logo_path=logo_path,
                )

                if not video_res.get("success"):
                    content.status = ContentStatus.ERROR
                    db.commit()
                    return {"success": False, "error": video_res.get("error")}

                content.video_path = video_res.get("video_path")
                content.thumbnail_path = video_res.get("thumbnail_path")
                content.script = json.dumps(script_data, ensure_ascii=False)
                content.status = ContentStatus.WAITING_APPROVAL
                db.commit()

            # 4. Registra a geração no histórico
            gen = GenerationModel(
                content_id=content_id,
                version=1,
                prompt=topic,
                video_path=content.video_path or content.thumbnail_path,
            )
            db.add(gen)
            db.commit()
            db.refresh(content)

            return {
                "success": True,
                "content_id": content_id,
                "format": fmt,
                "title": content.title,
                "hook": script_data.get("hook") or script_data.get("cover_hook") or script_data.get("headline", ""),
                "caption": content.caption,
                "hashtags": content.hashtags,
                "video_path": content.video_path,
                "thumbnail_path": content.thumbnail_path,
                "slide_paths": script_data.get("slide_paths", []),
                "duration": script_data.get("duration", 15) if fmt == "REELS" else 0,
                "profile_username": profile.username,
                "script_data": script_data,
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    async def create_new_reel(
        self,
        profile_id: str,
        topic: str,
        user_id: Optional[str] = None,
        telegram_notifier=None,
        chat_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Wrapper retrocompatível para geração exclusiva de Reels."""
        return await self.create_new_content(
            profile_id=profile_id,
            topic=topic,
            content_format="REELS",
            user_id=user_id,
            telegram_notifier=telegram_notifier,
            chat_id=chat_id,
        )

    async def approve_and_publish(self, content_id: int, telegram_user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Aprova e publica no Instagram através da Meta Graph API oficial.
        Suporta os 4 formatos: REELS, STORIES, FEED e CAROUSEL.
        """
        db = SessionLocal()
        try:
            content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
            if not content:
                return {"success": False, "error": "Conteúdo não encontrado"}

            if content.status == ContentStatus.PUBLISHED:
                return {"success": False, "error": "Este conteúdo já foi publicado anteriormente no Instagram!"}

            # 1. Registra a ação de aprovação humana
            action = ActionModel(
                content_id=content_id,
                action="APPROVE_PUBLISH",
                telegram_user_id=telegram_user_id,
            )
            db.add(action)
            content.status = ContentStatus.APPROVED
            db.commit()

            fmt = (content.content_format or "REELS").upper()
            script_data = json.loads(content.script or "{}")

            # 2. Valida credenciais do Instagram para a conta
            profile = self.profile_manager.get_profile(content.profile_id)
            account_id = (profile.instagram_account_id if profile else None) or settings.INSTAGRAM_ACCOUNT_ID
            access_token = (profile.instagram_access_token if profile else None) or settings.INSTAGRAM_ACCESS_TOKEN

            fmt_labels = {
                "REELS": "O Reel (9:16)",
                "STORIES": "O Story (9:16)",
                "FEED": "O Post de Feed (1:1)",
                "CAROUSEL": f"O Carrossel ({len(script_data.get('slide_paths', []))} slides)",
            }
            label_text = fmt_labels.get(fmt, "O conteúdo")

            if not account_id or not access_token:
                # Ambiente de teste sem token oficial configurado
                return {
                    "success": False,
                    "simulated": True,
                    "message": (
                        f"✅ {label_text} foi APROVADO com sucesso no sistema!\n\n"
                        "⚠️ Para publicar na conta real do Instagram, insira seu `INSTAGRAM_ACCOUNT_ID` e "
                        "`INSTAGRAM_ACCESS_TOKEN` na aba 'Instagram & Meta' do Painel Web."
                    ),
                }

            # 3. Publicação real na Meta Graph API
            content.status = ContentStatus.PUBLISHING
            db.commit()

            meta_client = MetaGraphClient(access_token=access_token)
            base_media_url = settings.PUBLIC_MEDIA_BASE_URL or f"http://{settings.APP_HOST}:{settings.APP_PORT}/media"

            if fmt == "REELS":
                media_url = f"{base_media_url}/videos/{Path(content.video_path).name}" if content.video_path else ""
                container_res = await meta_client.create_reel_container(
                    video_url=media_url,
                    caption=content.caption or "",
                    account_id=account_id,
                )
                if not container_res.get("success"):
                    content.status = ContentStatus.ERROR
                    db.commit()
                    return {"success": False, "error": f"Erro na Meta API ao criar Reel: {container_res.get('error')}"}

                container_id = container_res.get("container_id")
                pub_res = await meta_client.publish_media(container_id=container_id, account_id=account_id)

            elif fmt == "STORIES":
                media_url = f"{base_media_url}/media/{Path(content.thumbnail_path).name}" if content.thumbnail_path else ""
                container_res = await meta_client.create_story_container(
                    media_url=media_url,
                    is_video=False,
                    account_id=account_id,
                )
                if not container_res.get("success"):
                    content.status = ContentStatus.ERROR
                    db.commit()
                    return {"success": False, "error": f"Erro na Meta API ao criar Story: {container_res.get('error')}"}

                container_id = container_res.get("container_id")
                pub_res = await meta_client.publish_media(container_id=container_id, account_id=account_id)

            elif fmt == "FEED":
                media_url = f"{base_media_url}/media/{Path(content.thumbnail_path).name}" if content.thumbnail_path else ""
                container_res = await meta_client.create_feed_post_container(
                    image_url=media_url,
                    caption=content.caption or "",
                    account_id=account_id,
                )
                if not container_res.get("success"):
                    content.status = ContentStatus.ERROR
                    db.commit()
                    return {"success": False, "error": f"Erro na Meta API ao criar Feed Post: {container_res.get('error')}"}

                container_id = container_res.get("container_id")
                pub_res = await meta_client.publish_media(container_id=container_id, account_id=account_id)

            elif fmt == "CAROUSEL":
                # Publicação de Carrossel: 1 container por slide + 1 container pai
                slide_paths = script_data.get("slide_paths", [])
                if not slide_paths and content.thumbnail_path:
                    slide_paths = [content.thumbnail_path]

                slide_container_ids: List[str] = []
                for s_path in slide_paths:
                    slide_filename = Path(s_path).name
                    slide_url = f"{base_media_url}/media/carousel_{content_id}/{slide_filename}"
                    item_res = await meta_client.create_carousel_item_container(
                        image_url=slide_url,
                        account_id=account_id,
                    )
                    if not item_res.get("success"):
                        content.status = ContentStatus.ERROR
                        db.commit()
                        return {"success": False, "error": f"Erro no slide {slide_filename} do carrossel: {item_res.get('error')}"}
                    slide_container_ids.append(item_res.get("container_id"))

                # Container pai agregador
                carousel_res = await meta_client.create_carousel_container(
                    children_ids=slide_container_ids,
                    caption=content.caption or "",
                    account_id=account_id,
                )
                if not carousel_res.get("success"):
                    content.status = ContentStatus.ERROR
                    db.commit()
                    return {"success": False, "error": f"Erro ao criar container pai do Carrossel: {carousel_res.get('error')}"}

                container_id = carousel_res.get("container_id")
                pub_res = await meta_client.publish_media(container_id=container_id, account_id=account_id)

            else:
                return {"success": False, "error": f"Formato '{fmt}' desconhecido"}

            if not pub_res.get("success"):
                content.status = ContentStatus.ERROR
                db.commit()
                return {"success": False, "error": f"Falha ao publicar {label_text} na Meta: {pub_res.get('error')}"}

            media_id = pub_res.get("media_id")
            content.instagram_media_id = media_id
            content.status = ContentStatus.PUBLISHED
            content.published_at = datetime.now(timezone.utc)
            db.commit()

            return {
                "success": True,
                "media_id": media_id,
                "message": f"🎉 {label_text} publicado com sucesso no perfil oficial do Instagram!",
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
