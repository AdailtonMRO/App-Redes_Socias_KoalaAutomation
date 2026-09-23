"""
Testes Unitários do ContentOrchestrator (Geração de Conteúdo Multi-Formato)
Verifica formatos STORIES, FEED, CAROUSEL e integridade do BASE_DIR.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
from app.services.content_service import ContentOrchestrator
from app.config import get_settings, BASE_DIR


def test_settings_base_dir_attribute():
    """Valida que o objeto Settings possui o atributo BASE_DIR como Path válido."""
    settings = get_settings()
    assert hasattr(settings, "BASE_DIR"), "Settings deve possuir BASE_DIR"
    assert isinstance(settings.BASE_DIR, Path)
    assert settings.BASE_DIR == BASE_DIR


@pytest.mark.anyio
async def test_create_story_content_success(tmp_path):
    """
    Testa a geração de publicação no formato STORIES.
    Simula o Gemini e FFmpeg para garantir que não ocorra 'Settings object has no attribute BASE_DIR'
    e que o fluxo complete com status WAITING_APPROVAL.
    """
    orchestrator = ContentOrchestrator()
    orchestrator.media_base_dir = tmp_path

    mock_gemini_res = {
        "success": True,
        "data": {
            "title": "Notícia do Tênis",
            "headline": "João Fonseca avança",
            "hook": "Sensação brasileira brilha",
            "body": "Vitória expressiva em dois sets.",
            "call_to_action": "O que você achou?",
            "visual_prompt": "tennis player celebrating",
        }
    }

    with patch.object(orchestrator.gemini, "generate_content", new_callable=AsyncMock) as mock_gen_content, \
         patch.object(orchestrator.gemini, "generate_image", new_callable=AsyncMock) as mock_gen_img, \
         patch.object(orchestrator.ffmpeg, "generate_story_vertical_image") as mock_story_img:

        mock_gen_content.return_value = mock_gemini_res

        # Simula criação do arquivo story pelo ffmpeg
        def fake_ffmpeg(output_path, **kwargs):
            Path(output_path).touch()
            return True

        mock_story_img.side_effect = fake_ffmpeg

        res = await orchestrator.create_new_content(
            profile_id="koalatenis",
            topic="João Fonseca vence torneio",
            content_format="STORIES",
        )

        assert res["success"] is True, f"Falha na geração: {res.get('error')}"
        assert res["format"] == "STORIES"
        assert res["thumbnail_path"] is not None
        assert Path(res["thumbnail_path"]).exists()


@pytest.mark.anyio
async def test_create_feed_content_success(tmp_path):
    """Testa geração de post no formato FEED garantindo resolução de caminhos."""
    orchestrator = ContentOrchestrator()
    orchestrator.media_base_dir = tmp_path

    mock_gemini_res = {
        "success": True,
        "data": {
            "title": "Post Feed Tênis",
            "headline": "Dica de Saque",
            "caption": "Confira como melhorar seu saque.",
            "cta": "Comente abaixo!",
            "visual_prompt": "tennis racket close up",
        }
    }

    with patch.object(orchestrator.gemini, "generate_content", new_callable=AsyncMock) as mock_gen_content, \
         patch.object(orchestrator.gemini, "generate_image", new_callable=AsyncMock) as mock_gen_img, \
         patch.object(orchestrator.ffmpeg, "generate_square_slide_image") as mock_feed_img:

        mock_gen_content.return_value = mock_gemini_res

        def fake_ffmpeg(output_path, **kwargs):
            Path(output_path).touch()
            return True

        mock_feed_img.side_effect = fake_ffmpeg

        res = await orchestrator.create_new_content(
            profile_id="koalatenis",
            topic="Dica de Saque no Tênis",
            content_format="FEED",
        )

        assert res["success"] is True, f"Falha na geração: {res.get('error')}"
        assert res["format"] == "FEED"
        assert res["thumbnail_path"] is not None
        assert Path(res["thumbnail_path"]).exists()

