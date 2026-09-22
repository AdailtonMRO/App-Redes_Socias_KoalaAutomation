"""
Teclados e Menus Interativos do Telegram Bot
"""
from typing import List, Dict, Any


def get_main_menu_keyboard():
    """Retorna o teclado inline com as ações principais."""
    return {
        "inline_keyboard": [
            [{"text": "✨ Criar Publicação (/novo)", "callback_data": "menu_novo"}],
            [{"text": "📡 Radar de Conteúdo (/radar)", "callback_data": "menu_radar"}],
            [
                {"text": "📋 Fila de Aprovação", "callback_data": "menu_fila"},
                {"text": "📜 Histórico", "callback_data": "menu_historico"},
            ],
            [
                {"text": "👤 Perfis Cadastrados", "callback_data": "menu_perfis"},
                {"text": "⚡ Status do Sistema", "callback_data": "menu_status"},
            ],
        ]
    }


def get_profiles_keyboard(profiles: List[Dict[str, Any]]):
    """Gera botões para seleção de cada marca/perfil cadastrado."""
    buttons = []
    for p in profiles:
        buttons.append([{"text": f"🎾 {p.get('name')} ({p.get('username')})", "callback_data": f"select_profile_{p.get('id')}"}])
    buttons.append([{"text": "« Voltar ao Início", "callback_data": "menu_start"}])
    return {"inline_keyboard": buttons}


def get_format_choice_keyboard(profile_id: str):
    """Gera botões para seleção do formato da publicação."""
    return {
        "inline_keyboard": [
            [
                {"text": "🎬 Reel (Vídeo 9:16)", "callback_data": f"fmt_{profile_id}_REELS"},
                {"text": "📱 Story (9:16)", "callback_data": f"fmt_{profile_id}_STORIES"},
            ],
            [
                {"text": "🖼️ Feed Post (1:1)", "callback_data": f"fmt_{profile_id}_FEED"},
                {"text": "📚 Carrossel (Slides 1:1)", "callback_data": f"fmt_{profile_id}_CAROUSEL"},
            ],
            [{"text": "« Voltar aos Perfis", "callback_data": "menu_novo"}],
        ]
    }


def get_theme_choice_keyboard(profile_id: str, content_format: str = "REELS"):
    """Pergunta se o usuário quer tema sugerido pela IA ou digitar um tema."""
    return {
        "inline_keyboard": [
            [{"text": "💡 Deixar a IA Sugerir Tema", "callback_data": f"theme_ai_{profile_id}_{content_format}"}],
            [{"text": "✏️ Eu quero Digitar um Tema", "callback_data": f"theme_custom_{profile_id}_{content_format}"}],
            [{"text": "« Escolher Outro Formato", "callback_data": f"select_profile_{profile_id}"}],
        ]
    }


def get_approval_keyboard(content_id: int):
    """Teclado com a decisão humana obrigatória da V1."""
    return {
        "inline_keyboard": [
            [{"text": "✅ PUBLICAR NO INSTAGRAM", "callback_data": f"approve_publish_{content_id}"}],
            [
                {"text": "🔄 Refazer Roteiro", "callback_data": f"approve_retry_{content_id}"},
                {"text": "✏️ Alterar Detalhe", "callback_data": f"approve_edit_{content_id}"},
            ],
            [{"text": "❌ Descartar Conteúdo", "callback_data": f"approve_reject_{content_id}"}],
        ]
    }
