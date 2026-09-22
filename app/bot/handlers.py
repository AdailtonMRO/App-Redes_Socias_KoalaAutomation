"""
Tratamento de Comandos, Callbacks e Respostas do Bot do Telegram
Suporta os 4 formatos oficiais do Instagram:
- Reels (Vídeo 9:16)
- Stories (Vertical 9:16)
- Feed (Post Quadrado 1:1)
- Carrossel (Multi-Slides 1:1 com envio em álbum)
"""
from typing import Dict, Any, Optional
from pathlib import Path
from app.config import get_settings
from app.profiles.manager import ProfileManager
from app.database.database import SessionLocal
from app.database.repository import ContentRepository
from app.bot.keyboards import (
    get_main_menu_keyboard,
    get_profiles_keyboard,
    get_format_choice_keyboard,
    get_theme_choice_keyboard,
    get_approval_keyboard,
)

settings = get_settings()
profile_manager = ProfileManager()

# Memória de estado de chat para comandos interativos (ex: digitação de tema)
PENDING_USER_INPUT: Dict[int, Dict[str, Any]] = {}

FORMAT_NAMES = {
    "REELS": "🎬 Reel (Vídeo 9:16)",
    "STORIES": "📱 Story (Vertical 9:16)",
    "FEED": "🖼️ Feed Post (Quadrado 1:1)",
    "CAROUSEL": "📚 Carrossel (Slides 1:1)",
}


async def handle_start(bot, chat_id: int):
    """Mensagem de boas-vindas e menu principal."""
    text = (
        "🤖 *BEM-VINDO AO INSTAGRAM AI STUDIO*\n\n"
        "Seu assistente inteligente para criação de conteúdo multi-formato:\n"
        "• 🎬 *Reels* (Vídeos 9:16 cinematográficos)\n"
        "• 📱 *Stories* (Engajamento rápido e enquetes)\n"
        "• 🖼️ *Feed Posts* (Imagens de alta autoridade 1:1)\n"
        "• 📚 *Carrosséis* (Sequências didáticas de slides)\n\n"
        "Com *aprovação humana obrigatória* antes de qualquer publicação.\n\n"
        "Escolha uma ação abaixo ou digite `/novo` para começar:"
    )
    await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


async def handle_novo(bot, chat_id: int):
    """Inicia o fluxo de criação perguntando o perfil."""
    profiles = profile_manager.list_profiles()
    if not profiles:
        text = (
            "⚠️ *Nenhum perfil cadastrado!*\n\n"
            "Acesse o Painel Web na aba *Perfis de Automação* para adicionar sua primeira conta."
        )
        await bot.send_message(chat_id, text, parse_mode="Markdown")
        return

    text = "✨ *CRIAR NOVA PUBLICAÇÃO*\n\nCom qual perfil ou marca você deseja trabalhar hoje?"
    await bot.send_message(chat_id, text, reply_markup=get_profiles_keyboard(profiles), parse_mode="Markdown")


async def handle_status(bot, chat_id: int):
    """Exibe a saúde geral do sistema."""
    telegram_ok = "🟢 Online"
    gemini_ok = "🟢 Configurado" if settings.GEMINI_API_KEY else "🟡 Pendente Chave"
    ig_ok = "🟢 Configurado" if settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID else "🟡 Pendente Token"

    profiles = profile_manager.list_profiles()

    db = SessionLocal()
    try:
        repo = ContentRepository(db)
        waiting = len(repo.list_waiting_approval())
    finally:
        db.close()

    text = (
        "⚡ *STATUS DO SISTEMA KOALA AUTO*\n\n"
        f"• Container: 🟢 Ativo (DSV)\n"
        f"• Telegram Bot: {telegram_ok}\n"
        f"• Google Gemini AI: {gemini_ok}\n"
        f"• Instagram Meta API: {ig_ok}\n"
        f"• Perfis Cadastrados: *{len(profiles)}*\n\n"
        f"📋 *Fila de Aprovação:* {waiting} conteúdo(s) pendente(s)\n"
        f"🌐 *Painel Web:* `http://{settings.APP_HOST}:{settings.APP_PORT}`"
    )
    await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


async def handle_fila(bot, chat_id: int):
    """Lista conteúdos que estão aguardando aprovação humana."""
    db = SessionLocal()
    try:
        repo = ContentRepository(db)
        waiting = repo.list_waiting_approval()
    finally:
        db.close()

    if not waiting:
        text = "📋 *Fila Vazia*\n\nNão há nenhum conteúdo aguardando aprovação no momento.\nEnvie `/novo` para gerar um conteúdo!"
        await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        return

    text = f"📋 *CONTEÚDOS AGUARDANDO APROVAÇÃO ({len(waiting)}):*\n\n"
    for item in waiting:
        fmt_label = FORMAT_NAMES.get((item.content_format or "REELS").upper(), item.content_format)
        text += f"• *ID #{item.id}* [{fmt_label}]\n  Perfil: `{item.profile_id}`\n  Tema: _{item.topic}_\n\n"

    await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")


async def handle_perfis(bot, chat_id: int):
    """Lista todos os perfis cadastrados no sistema e status da logomarca."""
    profiles = profile_manager.list_profiles()
    if not profiles:
        text = "👤 *Nenhum perfil cadastrado.* Acesse o painel web para adicionar."
        await bot.send_message(chat_id, text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")
        return

    text = "👤 *PERFIS CADASTRADOS & LOGOMARCAS:*\n\n"
    keyboard_rows = []
    for p in profiles:
        logo_file = p.get("logo_path")
        has_logo = "✅ Logomarca salva" if (logo_file and Path(logo_file).exists()) else "⚪ Sem logomarca"
        ig_id = p.get("instagram_account_id") or "Usa padrão do .env"
        text += (
            f"• *{p.get('name')}* (`{p.get('username')}`)\n"
            f"  Status Logo: *{has_logo}*\n"
            f"  Nichos: _{', '.join(p.get('niche', []))}_\n"
            f"  Conta ID: `{ig_id}`\n\n"
        )
        keyboard_rows.append([{
            "text": f"🖼️ Enviar Logo: {p.get('name')}",
            "callback_data": f"upload_logo_{p.get('id')}",
        }])

    keyboard_rows.append([{"text": "⬅️ Menu Principal", "callback_data": "menu_start"}])
    reply_markup = {"inline_keyboard": keyboard_rows}

    await bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode="Markdown")


async def generate_and_send_content(bot, chat_id: int, profile_id: str, topic: str, content_format: str = "REELS"):
    """Orquestra a geração e o envio de mídia + card de aprovação para o Telegram."""
    fmt = content_format.upper()
    fmt_title = FORMAT_NAMES.get(fmt, fmt)

    await bot.send_message(
        chat_id,
        f"⏳ *Gerando publicação [{fmt_title}]...*\nConsultando Google Gemini e renderizando mídias com alta definição.\n_(Aguarde alguns segundos)_",
        parse_mode="Markdown",
    )

    from app.services.content_service import ContentOrchestrator
    orchestrator = ContentOrchestrator()

    res = await orchestrator.create_new_content(
        profile_id=profile_id,
        topic=topic,
        content_format=fmt,
        telegram_notifier=bot,
        chat_id=chat_id,
    )

    if not res.get("success"):
        await bot.send_message(chat_id, f"❌ *Erro ao gerar conteúdo:* {res.get('error')}", parse_mode="Markdown")
        return

    content_id = res.get("content_id")
    profile_username = res.get("profile_username", profile_id)
    title = res.get("title", topic)
    hook = res.get("hook", "")
    caption = res.get("caption", "")
    hashtags = res.get("hashtags", "")

    # Card descritivo com decisão humana
    card_text = (
        f"🎯 *NOVO CONTEÚDO AGUARDANDO SUA APROVAÇÃO*\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📱 *Formato:* {fmt_title}\n"
        f"👤 *Perfil:* `@{profile_username}`\n"
        f"📌 *ID:* `#{content_id}`\n\n"
        f"💡 *Tema:* _{topic}_\n"
        f"🎬 *Título:* *{title}*\n"
        f"🪝 *Gancho:* _{hook}_\n\n"
        f"📝 *Legenda Sugerida:*\n{caption[:350]}...\n\n"
        f"🏷️ *Hashtags:*\n`{hashtags}`\n\n"
        f"⚠️ *Ação Obrigatória:* Avalie o material gerado acima antes de autorizar a publicação na Meta API."
    )

    # Despacha a entrega da mídia conforme o formato
    if fmt == "REELS":
        video_path = res.get("video_path")
        if video_path:
            sent = await bot.send_video(
                chat_id=chat_id,
                video_path=video_path,
                caption=f"🎬 Prévia do Reel #{content_id}\nTema: {topic}",
                reply_markup=get_approval_keyboard(content_id),
            )
            if not sent:
                await bot.send_message(chat_id, card_text, reply_markup=get_approval_keyboard(content_id), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id, card_text, reply_markup=get_approval_keyboard(content_id), parse_mode="Markdown")

    elif fmt == "CAROUSEL":
        slide_images = res.get("slide_images", [])
        if slide_images:
            # 1. Envia os slides como álbum de fotos no Telegram
            await bot.send_media_group(
                chat_id=chat_id,
                photo_paths=slide_images,
                caption=f"📚 Álbum Carrossel ({len(slide_images)} slides) para @{profile_username}\nTema: {topic}",
            )

        # 2. Envia a mensagem de revisão e aprovação com os botões de ação
        await bot.send_message(
            chat_id=chat_id,
            text=card_text,
            reply_markup=get_approval_keyboard(content_id),
            parse_mode="Markdown",
        )

    elif fmt in ("FEED", "STORIES"):
        thumb_path = res.get("thumbnail_path")
        if thumb_path:
            sent = await bot.send_photo(
                chat_id=chat_id,
                photo_path=thumb_path,
                caption=card_text,
                reply_markup=get_approval_keyboard(content_id),
            )
            if not sent:
                await bot.send_message(chat_id, card_text, reply_markup=get_approval_keyboard(content_id), parse_mode="Markdown")
        else:
            await bot.send_message(chat_id, card_text, reply_markup=get_approval_keyboard(content_id), parse_mode="Markdown")


async def handle_text_message(bot, chat_id: int, text: str):
    """Trata mensagens de texto comuns, incluindo temas digitados pelo usuário."""
    if chat_id in PENDING_USER_INPUT:
        state = PENDING_USER_INPUT.get(chat_id, {})
        action = state.get("action")
        if action == "waiting_topic":
            PENDING_USER_INPUT.pop(chat_id, None)
            profile_id = state.get("profile_id")
            fmt = state.get("format", "REELS")
            await generate_and_send_content(bot, chat_id, profile_id, topic=text, content_format=fmt)
            return
        elif action == "waiting_logo":
            profile_id = state.get("profile_id")
            profile = profile_manager.get_profile(profile_id)
            p_name = profile.name if profile else profile_id
            if text.lower() in ("/cancelar", "cancelar", "sair", "/start"):
                PENDING_USER_INPUT.pop(chat_id, None)
                await bot.send_message(
                    chat_id,
                    "❌ *Envio de logomarca cancelado.*",
                    reply_markup=get_main_menu_keyboard(),
                    parse_mode="Markdown",
                )
                return
            await bot.send_message(
                chat_id,
                f"🖼️ *Aguardando o envio da imagem da logo para {p_name}*\n\n"
                f"Envie a foto ou arquivo de imagem (PNG/JPG) aqui no chat.\n"
                f"Se desejar desistir, digite `/cancelar`.",
                parse_mode="Markdown",
            )
            return

    # Mensagem não mapeada
    await bot.send_message(
        chat_id,
        f"Recebi sua mensagem: _{text}_\nPara criar uma nova publicação, use `/novo` ou escolha no menu abaixo:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )


async def handle_callback_query(bot, query: Dict[str, Any]):
    """Roteador para cliques em botões inline do Telegram."""
    data = query.get("data", "")
    message = query.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return

    if data == "menu_start":
        await handle_start(bot, chat_id)
    elif data == "menu_novo":
        await handle_novo(bot, chat_id)
    elif data == "menu_status":
        await handle_status(bot, chat_id)
    elif data == "menu_fila":
        await handle_fila(bot, chat_id)
    elif data == "menu_historico":
        await handle_fila(bot, chat_id)
    elif data == "menu_perfis":
        await handle_perfis(bot, chat_id)

    # Iniciar upload de logomarca para perfil
    elif data.startswith("upload_logo_"):
        profile_id = data.replace("upload_logo_", "")
        profile = profile_manager.get_profile(profile_id)
        name = profile.name if profile else profile_id
        PENDING_USER_INPUT[chat_id] = {
            "action": "waiting_logo",
            "profile_id": profile_id,
        }
        text = (
            f"🖼️ *ENVIAR LOGOMARCA PARA:* *{name}*\n\n"
            f"Por favor, *envie a imagem da logomarca agora* aqui no chat (como foto ou documento PNG com fundo transparente).\n\n"
            f"✨ *Aplicação Automática:*\n"
            f"Esta logo será salva e automaticamente inserida no topo de todas as fotos, carrosséis, stories e reels deste perfil!\n\n"
            f"_(Para cancelar a qualquer momento, digite `/cancelar`)_"
        )
        await bot.send_message(chat_id, text, parse_mode="Markdown")

    # 1. Usuário selecionou o perfil -> agora escolhe o Formato
    elif data.startswith("select_profile_"):
        profile_id = data.replace("select_profile_", "")
        profile = profile_manager.get_profile(profile_id)
        name = profile.name if profile else profile_id
        text = (
            f"🎯 *Perfil Selecionado:* {name}\n\n"
            f"Qual formato de publicação você deseja produzir hoje?"
        )
        await bot.send_message(chat_id, text, reply_markup=get_format_choice_keyboard(profile_id), parse_mode="Markdown")

    # 2. Usuário selecionou o formato -> agora escolhe como definir o Tema
    elif data.startswith("fmt_"):
        parts = data.split("_", 2)
        if len(parts) >= 3:
            profile_id = parts[1]
            fmt = parts[2].upper()
            profile = profile_manager.get_profile(profile_id)
            name = profile.name if profile else profile_id
            fmt_title = FORMAT_NAMES.get(fmt, fmt)
            text = (
                f"✨ *Formato Escolhido:* {fmt_title}\n"
                f"Perfil: *{name}*\n\n"
                f"Como deseja definir o tema do conteúdo?"
            )
            await bot.send_message(chat_id, text, reply_markup=get_theme_choice_keyboard(profile_id, fmt), parse_mode="Markdown")

    # 3. Usuário optou por tema sugerido pela IA
    elif data.startswith("theme_ai_"):
        parts = data.replace("theme_ai_", "").split("_", 1)
        profile_id = parts[0]
        fmt = parts[1] if len(parts) > 1 else "REELS"

        profile = profile_manager.get_profile(profile_id)
        niche_sample = profile.niche[0] if profile and profile.niche else "dicas"
        auto_topic = f"Como dominar a técnica correta em {niche_sample} passo a passo"

        await generate_and_send_content(bot, chat_id, profile_id, topic=auto_topic, content_format=fmt)

    # 4. Usuário optou por digitar o tema
    elif data.startswith("theme_custom_"):
        parts = data.replace("theme_custom_", "").split("_", 1)
        profile_id = parts[0]
        fmt = parts[1] if len(parts) > 1 else "REELS"

        profile = profile_manager.get_profile(profile_id)
        name = profile.name if profile else profile_id
        fmt_title = FORMAT_NAMES.get(fmt.upper(), fmt)

        PENDING_USER_INPUT[chat_id] = {
            "action": "waiting_topic",
            "profile_id": profile_id,
            "format": fmt,
        }

        text = (
            f"✏️ *Digite o tema desejado para o {fmt_title}:*\n\n"
            f"Envie uma mensagem de texto com o assunto para `{name}`.\n"
            f"Exemplo:\n_3 erros graves que você comete sem perceber_"
        )
        await bot.send_message(chat_id, text, parse_mode="Markdown")

    # 5. Aprovação humana e publicação na Meta Graph API
    elif data.startswith("approve_publish_"):
        content_id = int(data.replace("approve_publish_", ""))
        await bot.send_message(chat_id, "🚀 *Processando publicação oficial no Instagram via Meta API...*", parse_mode="Markdown")

        from app.services.content_service import ContentOrchestrator
        orchestrator = ContentOrchestrator()
        res = await orchestrator.approve_and_publish(content_id, telegram_user_id=str(chat_id))

        if res.get("success"):
            media_id = res.get("media_id")
            await bot.send_message(
                chat_id,
                f"🎉 *CONTEÚDO PUBLICADO COM SUCESSO!*\n\n"
                f"• ID da Mídia no Instagram: `{media_id}`\n"
                f"• Status: `PUBLISHED` ✅",
                parse_mode="Markdown",
            )
        else:
            msg = res.get("message") or res.get("error")
            await bot.send_message(chat_id, f"ℹ️ *Status da Publicação:*\n\n{msg}", parse_mode="Markdown")

    # 6. Descarte de conteúdo
    elif data.startswith("approve_reject_"):
        content_id = int(data.replace("approve_reject_", ""))
        from app.database.database import SessionLocal
        from app.database.models import ContentModel, ContentStatus
        db = SessionLocal()
        try:
            content = db.query(ContentModel).filter(ContentModel.id == content_id).first()
            if content:
                content.status = ContentStatus.REJECTED
                db.commit()
        finally:
            db.close()
        await bot.send_message(chat_id, f"❌ *Conteúdo #{content_id} foi descartado.*", parse_mode="Markdown")

    # 7. Solicitação de alteração / retry
    elif data.startswith("approve_retry_") or data.startswith("approve_edit_"):
        await bot.send_message(chat_id, "✏️ *Envie seu feedback em texto:*\nO que você gostaria que a IA alterasse neste conteúdo?", parse_mode="Markdown")
