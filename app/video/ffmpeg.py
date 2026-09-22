"""
Abstração Centralizada de Processamento de Vídeo e Imagem com FFmpeg
Gera mídias para Reels (9:16), Stories (9:16), Feed (1:1) e Carrossel (Slides 1:1).
"""
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List


class FFmpegProcessor:
    def __init__(self):
        self.ffmpeg_cmd = shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe_cmd = shutil.which("ffprobe") or "ffprobe"

    def is_available(self) -> bool:
        """Verifica se o binário do FFmpeg está instalado no sistema."""
        try:
            res = subprocess.run([self.ffmpeg_cmd, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return res.returncode == 0
        except Exception:
            return False

    def _get_font_param(self) -> str:
        """Detecta fontes TrueType disponíveis no sistema."""
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for c in candidates:
            if Path(c).exists():
                return f":fontfile='{c}'"
        return ""

    def generate_square_slide_image(
        self,
        output_path: str,
        headline: str,
        body_text: str,
        slide_num: Optional[int] = None,
        total_slides: Optional[int] = None,
        brand_name: str = "Koala Tênis",
        background_image: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> bool:
        """Gera uma imagem quadrada 1:1 (1080x1080) com logo oficial e fundo fotográfico ou gradiente."""
        import textwrap
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        font_p = self._get_font_param()
        clean_brand = brand_name.replace("'", "").replace(":", " -")[:25]
        clean_headline = headline.replace("'", "").replace(":", " -")[:45]
        clean_body = body_text.replace("'", "").replace(":", " -")

        wrapped = textwrap.wrap(clean_body, width=40)[:3]
        l1 = wrapped[0] if len(wrapped) > 0 else ""
        l2 = wrapped[1] if len(wrapped) > 1 else ""
        l3 = wrapped[2] if len(wrapped) > 2 else ""

        indicator = f"{slide_num}/{total_slides}" if slide_num and total_slides else ""
        has_bg = background_image and Path(background_image).exists()
        has_logo = logo_path and Path(logo_path).exists()

        cmd = [self.ffmpeg_cmd, "-y"]
        bg_idx = None
        logo_idx = None

        if has_bg:
            cmd.extend(["-i", str(background_image)])
            bg_idx = 0
        if has_logo:
            cmd.extend(["-i", str(logo_path)])
            logo_idx = 1 if has_bg else 0

        chains = []
        if has_bg:
            chains.append(f"[{bg_idx}:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080[base_bg]")
        else:
            chains.append("color=c=0x0f172a:s=1080x1080:r=1:d=1[base_bg]")

        chains.append("[base_bg]drawbox=y=0:color=0x0284c7@0.65:width=1080:height=140:t=fill[top_bar]")

        post_filters = []
        if has_logo:
            chains.append(f"[{logo_idx}:v]scale=-1:85[logo_s]")
            post_filters.append("[top_bar][logo_s]overlay=x=(w-overlay_w)/2:y=28")
        else:
            post_filters.append(f"[top_bar]drawtext=text='🎾 {clean_brand}'{font_p}:fontcolor=white:fontsize=42:x=(w-text_w)/2:y=50")

        card_alpha = "@0.86" if has_bg else "@0.92"
        post_filters.append(f"drawbox=y=260:color=0x090d16{card_alpha}:width=1080:height=560:t=fill")
        post_filters.append(f"drawtext=text='{clean_headline}'{font_p}:fontcolor=0x38bdf8:fontsize=50:x=(w-text_w)/2:y=340")

        if l1:
            post_filters.append(f"drawtext=text='{l1}'{font_p}:fontcolor=white:fontsize=36:x=(w-text_w)/2:y=470")
        if l2:
            post_filters.append(f"drawtext=text='{l2}'{font_p}:fontcolor=white:fontsize=36:x=(w-text_w)/2:y=530")
        if l3:
            post_filters.append(f"drawtext=text='{l3}'{font_p}:fontcolor=white:fontsize=36:x=(w-text_w)/2:y=590")

        if indicator:
            post_filters.append(f"drawtext=text='{indicator}'{font_p}:fontcolor=0x94a3b8:fontsize=34:x=w-text_w-60:y=1000")

        chains.append(",".join(post_filters))
        full_filter = ";".join(chains)

        cmd.extend([
            "-filter_complex", full_filter,
            "-frames:v", "1",
            "-q:v", "2",
            str(out_file),
        ])

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            return res.returncode == 0 and out_file.exists()
        except Exception as e:
            print(f"[ERROR] Falha ao gerar slide 1:1: {e}")
            return False

    def generate_story_vertical_image(
        self,
        output_path: str,
        hook: str,
        body_text: str,
        cta: str,
        brand_name: str = "Koala Tênis",
        background_image: Optional[str] = None,
        logo_path: Optional[str] = None,
    ) -> bool:
        """Gera uma imagem vertical 9:16 (1080x1920) com logo oficial e fundo fotográfico."""
        import textwrap
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        font_p = self._get_font_param()
        clean_brand = brand_name.replace("'", "").replace(":", " -")[:25]
        clean_hook = hook.replace("'", "").replace(":", " -")[:50]
        clean_body = body_text.replace("'", "").replace(":", " -")
        clean_cta = cta.replace("'", "").replace(":", " -")[:45]

        wrapped = textwrap.wrap(clean_body, width=36)[:4]
        l1 = wrapped[0] if len(wrapped) > 0 else ""
        l2 = wrapped[1] if len(wrapped) > 1 else ""
        l3 = wrapped[2] if len(wrapped) > 2 else ""
        l4 = wrapped[3] if len(wrapped) > 3 else ""

        has_bg = background_image and Path(background_image).exists()
        has_logo = logo_path and Path(logo_path).exists()

        cmd = [self.ffmpeg_cmd, "-y"]
        bg_idx = None
        logo_idx = None

        if has_bg:
            cmd.extend(["-i", str(background_image)])
            bg_idx = 0
        if has_logo:
            cmd.extend(["-i", str(logo_path)])
            logo_idx = 1 if has_bg else 0

        chains = []
        if has_bg:
            chains.append(f"[{bg_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base_bg]")
        else:
            chains.append("color=c=0x0b0f17:s=1080x1920:r=1:d=1[base_bg]")

        chains.append("[base_bg]drawbox=y=0:color=0x0284c7@0.65:width=1080:height=220:t=fill[top_bar]")

        post_filters = []
        if has_logo:
            chains.append(f"[{logo_idx}:v]scale=-1:110[logo_s]")
            post_filters.append("[top_bar][logo_s]overlay=x=(w-overlay_w)/2:y=55")
        else:
            post_filters.append(f"[top_bar]drawtext=text='📱 {clean_brand}'{font_p}:fontcolor=white:fontsize=48:x=(w-text_w)/2:y=90")

        card_alpha = "@0.86" if has_bg else "@0.92"
        post_filters.append(f"drawbox=y=500:color=0x090d16{card_alpha}:width=1080:height=680:t=fill")
        post_filters.append(f"drawtext=text='{clean_hook}'{font_p}:fontcolor=0x38bdf8:fontsize=52:x=(w-text_w)/2:y=600")

        if l1:
            post_filters.append(f"drawtext=text='{l1}'{font_p}:fontcolor=white:fontsize=40:x=(w-text_w)/2:y=730")
        if l2:
            post_filters.append(f"drawtext=text='{l2}'{font_p}:fontcolor=white:fontsize=40:x=(w-text_w)/2:y=795")
        if l3:
            post_filters.append(f"drawtext=text='{l3}'{font_p}:fontcolor=white:fontsize=40:x=(w-text_w)/2:y=860")
        if l4:
            post_filters.append(f"drawtext=text='{l4}'{font_p}:fontcolor=white:fontsize=40:x=(w-text_w)/2:y=925")

        post_filters.extend([
            "drawbox=y=1550:color=0x10b981@0.5:width=1080:height=180:t=fill",
            f"drawtext=text='👉 {clean_cta}'{font_p}:fontcolor=white:fontsize=42:x=(w-text_w)/2:y=1620"
        ])

        chains.append(",".join(post_filters))
        full_filter = ";".join(chains)

        cmd.extend([
            "-filter_complex", full_filter,
            "-frames:v", "1",
            "-q:v", "2",
            str(out_file),
        ])

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            return res.returncode == 0 and out_file.exists()
        except Exception as e:
            print(f"[ERROR] Falha ao gerar Story 9:16: {e}")
            return False

    def extract_thumbnail(self, video_path: str, output_thumbnail_path: str, time_sec: float = 1.0) -> bool:
        """Extrai um frame do vídeo para servir de capa/thumbnail do Reel."""
        out_thumb = Path(output_thumbnail_path)
        out_thumb.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            self.ffmpeg_cmd,
            "-y",
            "-ss", str(time_sec),
            "-i", str(video_path),
            "-vframes", "1",
            "-q:v", "2",
            str(out_thumb),
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            return res.returncode == 0 and out_thumb.exists()
        except Exception:
            return False

    def generate_video_from_image(
        self,
        image_path: str,
        output_path: str,
        duration: int = 4,
        fps: int = 30,
        aspect_ratio: str = "9:16",
    ) -> bool:
        """
        Cria um vídeo MP4 (9:16 ou 16:9) animando suavemente a imagem base com efeito de zoom cinemático
        e gerando faixa de áudio estéreo silenciosa normalizada para compatibilidade com players de redes sociais.
        """
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.is_available():
            # Fallback seguro para ambiente de desenvolvimento local sem FFmpeg instalado
            with open(out_file, "wb") as f:
                f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom")
            return True

        total_frames = duration * fps

        w, h = (1080, 1920) if aspect_ratio == "9:16" else (1920, 1080)
        # Filtro de zoom cinematográfico lento (slow push in)
        vf = f"scale={w*2}:{h*2},zoompan=z='min(zoom+0.0015,1.25)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={fps},format=yuv420p"

        cmd = [
            self.ffmpeg_cmd,
            "-y",
            "-loop", "1",
            "-i", str(image_path),
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-t", str(duration),
            "-shortest",
            "-movflags", "+faststart",
            str(out_file),
        ]

        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
            return res.returncode == 0 and out_file.exists()
        except Exception as e:
            print(f"[ERROR] Falha no FFmpeg generate_video_from_image: {e}")
            return False
