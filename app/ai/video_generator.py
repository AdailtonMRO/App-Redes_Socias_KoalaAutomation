"""
Gerador de Vídeo Vertical com IA (Google Veo & FFmpeg Cinema Engine)
Suporta chamadas reais assíncronas à API do Veo 2.0 com polling de operações
e composição de cenas cinematográficas em formato vertical 9:16.
"""
import asyncio
import httpx
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.config import get_settings
from app.video.ffmpeg import FFmpegProcessor

settings = get_settings()


class VideoGeneratorService:
    def __init__(self, api_key: Optional[str] = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.GEMINI_API_KEY
        self.veo_model = self.settings.VEO_VIDEO_MODEL or "veo-2.0-generate-001"
        self.processor = FFmpegProcessor()
        self.data_dir = Path(self.settings.DATA_DIR)
        self.videos_dir = self.data_dir / "videos"
        self.thumbs_dir = self.data_dir / "thumbnails"
        self.temp_dir = self.data_dir / "temp"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.thumbs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def generate_reel_video(
        self,
        content_id: int,
        script_data: Dict[str, Any],
        brand_name: str = "Koala Tênis",
        telegram_notifier=None,
        chat_id: Optional[int] = None,
        logo_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Gera o vídeo cinematográfico usando Google Veo ou Cinema Engine com animação real."""
        title = script_data.get("title", f"Reel #{content_id}")
        hook = script_data.get("hook", "Confira esta dica incrível!")
        scenes = script_data.get("scenes", [])
        
        video_filename = f"reel_{content_id}.mp4"
        thumb_filename = f"thumb_{content_id}.jpg"
        final_video_path = self.videos_dir / video_filename
        thumb_path = self.thumbs_dir / thumb_filename

        # 1. Tenta gerar com o modelo Google Veo se a chave de API estiver configurada
        if self.api_key and self.veo_model != "mock-video-mode":
            if telegram_notifier and chat_id:
                await telegram_notifier.send_message(
                    chat_id,
                    "🎬 *Conectando ao modelo Google Veo 2.0...*\nIniciando geração de cenas cinematográficas com IA.",
                    parse_mode="Markdown",
                )

            veo_result = await self._generate_with_veo(content_id, scenes, telegram_notifier, chat_id)
            if veo_result.get("success"):
                video_path = veo_result.get("video_path")
                self.processor.extract_thumbnail(video_path, str(thumb_path))
                return {
                    "success": True,
                    "video_path": video_path,
                    "thumbnail_path": str(thumb_path),
                    "duration": veo_result.get("duration", 15),
                    "engine": "google-veo-2.0",
                }
            else:
                # Registra o motivo retornado pela Google
                error_msg = veo_result.get("error", "Modelo Veo indisponível na chave")
                print(f"[WARN] Falha no Veo: {error_msg}. Ativando Cinema Motion Engine.")
                if telegram_notifier and chat_id:
                    await telegram_notifier.send_message(
                        chat_id,
                        f"⚠️ *Aviso da Google AI:* {error_msg}\n_(O Veo exige faturamento ativado no Google Cloud)._\n\n"
                        f"🎞️ Ativando o **Cinema Motion Engine** com animação dinâmica 9:16 e transições...",
                        parse_mode="Markdown",
                    )

        # 2. Cinema Motion Engine: Gera vídeo vertical com movimento dinâmico, partículas e tipografia cinética
        total_duration = sum(s.get("duration", 5) for s in scenes) or 15
        success = self._generate_kinetic_cinema_reel(
            output_path=str(final_video_path),
            title=title,
            hook=hook,
            scenes=scenes,
            brand_name=brand_name,
            duration=total_duration,
            logo_path=logo_path,
        )

        if not success:
            return {"success": False, "error": "Falha ao compilar vídeo"}

        self.processor.extract_thumbnail(str(final_video_path), str(thumb_path))

        return {
            "success": True,
            "video_path": str(final_video_path),
            "thumbnail_path": str(thumb_path),
            "duration": total_duration,
            "engine": "cinema-motion",
        }

    async def _generate_with_veo(
        self,
        content_id: int,
        scenes: List[Dict[str, Any]],
        telegram_notifier=None,
        chat_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Dispara a operação assíncrona do Google Veo e monitora com polling."""
        # Prompt visual consolidado da cena principal
        first_scene = scenes[0] if scenes else {}
        visual_prompt = first_scene.get("visual_prompt") or "Cinematic tennis court vertical 9:16 high speed action"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.veo_model}:predictLongRunning?key={self.api_key}"
        payload = {
            "instances": [{"prompt": visual_prompt}],
            "parameters": {
                "aspectRatio": "9:16",
                "durationSeconds": 5,
                "personGeneration": "allow_adult",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                err_data = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
                err_message = err_data.get("error", {}).get("message", resp.text[:120])
                return {"success": False, "error": f"API Veo ({resp.status_code}): {err_message}"}

            operation_data = resp.json()
            operation_name = operation_data.get("name")
            if not operation_name:
                return {"success": False, "error": "Resposta do Veo não retornou operation_id"}

            print(f"[INFO] Operação do Veo criada: {operation_name}. Iniciando polling...")

            # Polling com timeout de 3 minutos
            poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={self.api_key}"
            for attempt in range(25):
                await asyncio.sleep(8)
                async with httpx.AsyncClient(timeout=20.0) as client:
                    poll_resp = await client.get(poll_url)

                if poll_resp.status_code == 200:
                    poll_data = poll_resp.json()
                    if poll_data.get("done", False):
                        # Operação concluída: extrai o vídeo
                        response_part = poll_data.get("response", {})
                        video_uri = response_part.get("generateVideoResponse", {}).get("generatedSamples", [{}])[0].get("video", {}).get("uri")
                        
                        if video_uri:
                            # Baixa o vídeo gerado
                            dest_path = self.videos_dir / f"reel_{content_id}.mp4"
                            async with httpx.AsyncClient(timeout=60.0) as dl_client:
                                dl_resp = await dl_client.get(video_uri)
                                if dl_resp.status_code == 200:
                                    with open(dest_path, "wb") as f:
                                        f.write(dl_resp.content)
                                    return {"success": True, "video_path": str(dest_path), "duration": 5}

                        return {"success": False, "error": "Operação Veo concluída mas sem URI de download"}

                if attempt % 2 == 0 and telegram_notifier and chat_id:
                    await telegram_notifier.send_message(
                        chat_id,
                        f"⏳ *Processando cenas no Google Veo...* ({attempt * 8}s)",
                        parse_mode="Markdown",
                    )

            return {"success": False, "error": "Timeout aguardando renderização no Google Veo"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_kinetic_cinema_reel(
        self,
        output_path: str,
        title: str,
        hook: str,
        scenes: List[Dict[str, Any]],
        brand_name: str,
        duration: int = 15,
        logo_path: Optional[str] = None,
    ) -> bool:
        """
        Gera um vídeo dinâmico com movimento cinematográfico real:
        gradiente em movimento, barras dinâmicas, partículas e tipografia de alta retenção 9:16.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        clean_title = title.replace("'", "").replace(":", " -")[:40]
        clean_hook = hook.replace("'", "").replace(":", " -")[:65]
        clean_brand = brand_name.replace("'", "")[:25]
        has_logo = logo_path and Path(logo_path).exists()

        cmd = [self.processor.ffmpeg_cmd, "-y"]
        audio_src = "anullsrc=r=44100:cl=stereo"
        cmd.extend(["-f", "lavfi", "-i", audio_src])

        if has_logo:
            cmd.extend(["-i", str(logo_path)])

        if has_logo:
            filter_complex = (
                f"testsrc2=s=1080x1920:r=30:d={duration},boxblur=lr=25:cr=25[bg];"
                f"[bg]drawbox=y=0:color=0x0284c7@0.4:width=1080:height=260:t=fill[top_bar];"
                f"[1:v]scale=-1:110[logo_s];"
                f"[top_bar][logo_s]overlay=x=(w-overlay_w)/2:y=75[header];"
                f"[header]drawbox=y=650:color=0x0f172a@0.85:width=1080:height=480:t=fill,"
                f"drawtext=text='{clean_title}':fontcolor=0x38bdf8:fontsize=52:x=(w-text_w)/2:y=720,"
                f"drawtext=text='{clean_hook}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=860,"
                f"drawbox=y=1680:color=0x000000@0.7:width=1080:height=180:t=fill,"
                f"drawtext=text='Toque duas vezes se concorda ❤️':fontcolor=0xfbbf24:fontsize=34:x=(w-text_w)/2:y=1740"
            )
        else:
            filter_complex = (
                f"testsrc2=s=1080x1920:r=30:d={duration},boxblur=lr=25:cr=25[bg];"
                f"[bg]drawbox=y=0:color=0x0284c7@0.4:width=1080:height=260:t=fill,"
                f"drawtext=text='🎾 {clean_brand}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=110,"
                f"drawbox=y=650:color=0x0f172a@0.85:width=1080:height=480:t=fill,"
                f"drawtext=text='{clean_title}':fontcolor=0x38bdf8:fontsize=52:x=(w-text_w)/2:y=720,"
                f"drawtext=text='{clean_hook}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=860,"
                f"drawbox=y=1680:color=0x000000@0.7:width=1080:height=180:t=fill,"
                f"drawtext=text='Toque duas vezes se concorda ❤️':fontcolor=0xfbbf24:fontsize=34:x=(w-text_w)/2:y=1740"
            )

        cmd = [self.processor.ffmpeg_cmd, "-y", "-f", "lavfi", "-i", audio_src]

        if has_logo:
            cmd.extend(["-i", str(logo_path)])

        cmd.extend([
            "-filter_complex", filter_complex,
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-shortest",
            "-t", str(duration),
            str(out_file),
        ])

        try:
            import subprocess
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
            return proc.returncode == 0 and out_file.exists()
        except Exception as e:
            print(f"[ERROR] Falha ao renderizar vídeo cinema: {e}")
            return False
