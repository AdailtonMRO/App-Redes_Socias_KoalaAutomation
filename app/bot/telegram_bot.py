"""
Serviço do Telegram Bot (Async Long-Polling)
Gerencia a comunicação assíncrona, filtrando estritamente pelo TELEGRAM_ALLOWED_USER_ID.
"""
import asyncio
from typing import Optional, Dict, Any
import httpx
from app.config import get_settings
from app.bot.handlers import (
    handle_start,
    handle_novo,
    handle_status,
    handle_fila,
    handle_perfis,
    handle_callback_query,
    handle_text_message,
)


class TelegramBotService:
    def __init__(self, token: Optional[str] = None, allowed_user_id: Optional[str] = None):
        self.settings = get_settings()
        self.token = token or self.settings.TELEGRAM_BOT_TOKEN
        self.allowed_user_id = str(allowed_user_id or self.settings.TELEGRAM_ALLOWED_USER_ID or "").strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else ""
        self.is_running = False
        self.last_update_id = 0
        self._task: Optional[asyncio.Task] = None

    async def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "Markdown",
    ) -> bool:
        """Envia mensagem para o usuário no Telegram."""
        if not self.base_url:
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as e:
            print(f"[WARN] Erro ao enviar mensagem no Telegram: {e}")
            return False

    async def send_video(
        self,
        chat_id: int,
        video_path: str,
        caption: str = "",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Envia o arquivo de vídeo do Reel diretamente para o chat do Telegram."""
        if not self.base_url:
            return False

        from pathlib import Path
        import json
        file_path = Path(video_path)
        if not file_path.exists():
            print(f"[ERROR] Arquivo de vídeo não encontrado para envio: {video_path}")
            return False

        url = f"{self.base_url}/sendVideo"
        data = {
            "chat_id": chat_id,
            "caption": caption[:1024],  # Limite da legenda do Telegram
            "parse_mode": "Markdown",
            "supports_streaming": "true",
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                with open(file_path, "rb") as f:
                    files = {"video": (file_path.name, f, "video/mp4")}
                    resp = await client.post(url, data=data, files=files)
                    return resp.status_code == 200
        except Exception as e:
            print(f"[WARN] Erro ao enviar vídeo no Telegram: {e}")
            return False

    async def send_photo(
        self,
        chat_id: int,
        photo_path: str,
        caption: str = "",
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Envia uma foto (ex: post de feed ou story) para o chat do Telegram."""
        if not self.base_url:
            return False

        from pathlib import Path
        import json
        file_path = Path(photo_path)
        if not file_path.exists():
            print(f"[ERROR] Arquivo de foto não encontrado para envio: {photo_path}")
            return False

        url = f"{self.base_url}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "caption": caption[:1024],
            "parse_mode": "Markdown",
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(file_path, "rb") as f:
                    files = {"photo": (file_path.name, f, "image/jpeg")}
                    resp = await client.post(url, data=data, files=files)
                    return resp.status_code == 200
        except Exception as e:
            print(f"[WARN] Erro ao enviar foto no Telegram: {e}")
            return False

    async def send_media_group(
        self,
        chat_id: int,
        photo_paths: list[str],
        caption: str = "",
    ) -> bool:
        """Envia um álbum de fotos (carrossel de slides) para o Telegram."""
        if not self.base_url or not photo_paths:
            return False

        from pathlib import Path
        import json

        url = f"{self.base_url}/sendMediaGroup"
        media = []
        files = {}
        file_handles = []

        try:
            for idx, p in enumerate(photo_paths):
                path_obj = Path(p)
                if not path_obj.exists():
                    continue
                attach_name = f"photo_{idx}"
                item = {
                    "type": "photo",
                    "media": f"attach://{attach_name}",
                }
                if idx == 0 and caption:
                    item["caption"] = caption[:1024]
                    item["parse_mode"] = "Markdown"
                media.append(item)
                fh = open(path_obj, "rb")
                file_handles.append(fh)
                files[attach_name] = (path_obj.name, fh, "image/jpeg")

            if not media:
                return False

            data = {
                "chat_id": chat_id,
                "media": json.dumps(media),
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, data=data, files=files)
                return resp.status_code == 200
        except Exception as e:
            print(f"[WARN] Erro ao enviar media group (carrossel) no Telegram: {e}")
            return False
        finally:
            for fh in file_handles:
                fh.close()

    async def _poll_updates(self):
        """Loop contínuo de polling com a Telegram Bot API."""
        print(f"[INFO] Telegram Bot iniciado para o usuário autorizado: {self.allowed_user_id}")
        self.is_running = True

        while self.is_running:
            if not self.token:
                await asyncio.sleep(5)
                continue

            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 20,
            }

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.get(url, params=params)

                if resp.status_code == 200:
                    data = resp.json()
                    for update in data.get("result", []):
                        self.last_update_id = update.get("update_id", self.last_update_id)
                        await self._process_update(update)
                elif resp.status_code == 401:
                    print("[ERROR] Token do Telegram inválido!")
                    await asyncio.sleep(15)
                else:
                    await asyncio.sleep(3)
            except httpx.RequestError:
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                print("[INFO] Telegram Bot polling cancelado.")
                break
            except Exception as e:
                print(f"[WARN] Erro inesperado no polling do Telegram: {e}")
                await asyncio.sleep(5)

    async def _save_uploaded_logo(self, chat_id: int, file_id: str, ext: str = ".png"):
        """Faz o download da imagem enviada pelo Telegram e vincula como logomarca do perfil."""
        from app.bot.handlers import PENDING_USER_INPUT, profile_manager, get_main_menu_keyboard
        from pathlib import Path

        state = PENDING_USER_INPUT.pop(chat_id, {})
        profile_id = state.get("profile_id")
        if not profile_id:
            await self.send_message(chat_id, "⚠️ Não encontrei o perfil para vincular esta logomarca. Use /perfis.")
            return

        profile = profile_manager.get_profile(profile_id)
        if not profile:
            await self.send_message(chat_id, f"⚠️ Perfil `{profile_id}` não encontrado.")
            return

        await self.send_message(chat_id, "⏳ *Baixando e processando logomarca oficial...*", parse_mode="Markdown")

        try:
            # 1. Obter info do arquivo no Telegram
            async with httpx.AsyncClient(timeout=30.0) as client:
                res_info = await client.get(f"{self.base_url}/getFile?file_id={file_id}")
                if res_info.status_code != 200:
                    await self.send_message(chat_id, "❌ Erro ao consultar arquivo no Telegram.")
                    return
                file_path_tg = res_info.json().get("result", {}).get("file_path")
                if not file_path_tg:
                    await self.send_message(chat_id, "❌ Caminho do arquivo não fornecido pela API do Telegram.")
                    return

                # 2. Fazer download do arquivo binário
                file_dl_url = f"https://api.telegram.org/file/bot{self.token}/{file_path_tg}"
                dl_res = await client.get(file_dl_url)
                if dl_res.status_code != 200:
                    await self.send_message(chat_id, "❌ Erro ao baixar os bytes da imagem.")
                    return

            # 3. Salvar no diretório persistente data/logos
            logos_dir = Path("data/logos")
            logos_dir.mkdir(parents=True, exist_ok=True)
            saved_filename = f"logo_{profile_id}{ext}"
            saved_path = (logos_dir / saved_filename).resolve()
            with open(saved_path, "wb") as f:
                f.write(dl_res.content)

            # 4. Atualizar registro do Profile
            profile.logo_path = str(saved_path)
            profile.logo_url = f"/media/logos/{saved_filename}"
            profile_manager.update_profile(profile_id, profile)

            # 5. Notificar operador com envio da prévia da logo
            await self.send_photo(
                chat_id=chat_id,
                photo_path=str(saved_path),
                caption=(
                    f"🎉 *LOGOMARCA VINCULADA COM SUCESSO!*\n\n"
                    f"• Perfil: *{profile.name}* (`@{profile.username}`)\n"
                    f"• Arquivo: `{saved_filename}`\n\n"
                    f"A partir de agora, todas as publicações geradas (Reels, Feed, Stories e Carrosséis) aplicarão esta logo automaticamente! 🐨✨"
                ),
                reply_markup=get_main_menu_keyboard(),
            )
        except Exception as e:
            print(f"[ERROR] Falha ao salvar logomarca do Telegram: {e}")
            await self.send_message(chat_id, f"❌ Erro ao processar logomarca: {e}")

    async def _process_update(self, update: Dict[str, Any]):
        """Valida usuário e despacha para os handlers apropriados."""
        # Trata clique em botão inline (callback_query)
        if "callback_query" in update:
            cb = update["callback_query"]
            from_user = cb.get("from", {})
            user_id = str(from_user.get("id"))

            if self.allowed_user_id and user_id != self.allowed_user_id:
                return

            await handle_callback_query(self, cb)
            return

        # Trata mensagem de texto comum ou mídia
        if "message" in update:
            msg = update["message"]
            from_user = msg.get("from", {})
            user_id = str(from_user.get("id"))
            chat_id = msg.get("chat", {}).get("id")
            text = (msg.get("text") or "").strip()

            # Bloqueia qualquer usuário que não seja o operador autorizado
            if self.allowed_user_id and user_id != self.allowed_user_id:
                await self.send_message(
                    chat_id,
                    "⛔ *Acesso Não Autorizado*\nEste bot pertence a um ambiente privado de automação.",
                )
                return

            from app.bot.handlers import PENDING_USER_INPUT
            from pathlib import Path

            # Verificação se recebeu foto
            if "photo" in msg:
                if chat_id in PENDING_USER_INPUT and PENDING_USER_INPUT[chat_id].get("action") == "waiting_logo":
                    photos = msg["photo"]
                    best_photo = photos[-1]  # Maior resolução
                    await self._save_uploaded_logo(chat_id, best_photo["file_id"], ext=".png")
                    return
                else:
                    await self.send_message(
                        chat_id,
                        "📸 *Foto recebida!*\nPara definir esta imagem como logomarca de um perfil, use `/perfis` e clique no botão *[ 🖼️ Enviar Logo ]* correspondente.",
                        parse_mode="Markdown",
                    )
                    return

            # Verificação se recebeu documento de imagem
            if "document" in msg:
                doc = msg["document"]
                file_name = doc.get("file_name", "logo.png")
                ext = Path(file_name).suffix.lower() or ".png"
                if chat_id in PENDING_USER_INPUT and PENDING_USER_INPUT[chat_id].get("action") == "waiting_logo":
                    await self._save_uploaded_logo(chat_id, doc["file_id"], ext=ext)
                    return
                else:
                    await self.send_message(
                        chat_id,
                        "📄 *Arquivo recebido!*\nPara definir uma nova logomarca, acesse `/perfis` e clique em *[ 🖼️ Enviar Logo ]*.",
                        parse_mode="Markdown",
                    )
                    return

            if text in ("/start", "start"):
                await handle_start(self, chat_id)
            elif text in ("/novo", "novo", "Criar Reel"):
                await handle_novo(self, chat_id)
            elif text in ("/radar", "radar", "Radar"):
                from app.bot.handlers import handle_radar
                await handle_radar(self, chat_id)
            elif text in ("/status", "status", "Status"):
                await handle_status(self, chat_id)
            elif text in ("/fila", "fila", "Fila"):
                await handle_fila(self, chat_id)
            elif text in ("/historico", "historico"):
                await handle_fila(self, chat_id)
            elif text in ("/perfis", "perfis", "Perfis"):
                await handle_perfis(self, chat_id)
            else:
                # Encaminha texto para tratamento de fluxo interativo (tema personalizado, etc)
                await handle_text_message(self, chat_id, text)

    def start(self):
        """Inicia a rotina de polling em segundo plano."""
        if not self.is_running and self.token:
            try:
                loop = asyncio.get_running_loop()
                self._task = loop.create_task(self._poll_updates())
            except RuntimeError:
                try:
                    self._task = asyncio.ensure_future(self._poll_updates())
                except Exception as e:
                    print(f"[WARN] Nao foi possivel iniciar task do telegram diretamente: {e}")

    def stop(self):
        """Interrompe o polling."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()


# Instância singleton global do bot
bot_service = TelegramBotService()
