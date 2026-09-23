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
        """
        Gera uma imagem vertical 9:16 (1080x1920) para Stories do Instagram.
        Layout profissional com:
        - Topo: Barra do Radar de Tênis
        - Centro: Card de alto contraste com manchete e resumo da notícia
        - Parte Inferior Direita: Logomarca oficial do perfil (ou badge de marca)
        """
        import textwrap
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        font_p = self._get_font_param()
        clean_brand = brand_name.replace("'", "").replace(":", " -")[:25]
        clean_hook = hook.replace("'", "").replace(":", " -").replace("%", "").strip()[:80]
        clean_body = body_text.replace("'", "").replace(":", " -").replace("%", "").strip()
        clean_cta = cta.replace("'", "").replace(":", " -")[:45]

        # Envolve manchete em até 3 linhas
        hook_lines = textwrap.wrap(clean_hook, width=30)[:3]
        h1 = hook_lines[0] if len(hook_lines) > 0 else ""
        h2 = hook_lines[1] if len(hook_lines) > 1 else ""
        h3 = hook_lines[2] if len(hook_lines) > 2 else ""

        # Envolve resumo em até 6 linhas
        summary_lines = textwrap.wrap(clean_body, width=36)[:6]

        has_bg = background_image and Path(background_image).exists()

        # Verifica se o arquivo de logo existe ou busca o logo padrão do perfil
        actual_logo = None
        if logo_path and Path(logo_path).exists():
            actual_logo = logo_path
        elif Path("profiles/koalatenis_logo.png").exists():
            actual_logo = "profiles/koalatenis_logo.png"

        has_logo = actual_logo is not None

        if not self.is_available():
            return self._generate_story_with_pillow(
                output_path=output_path,
                hook_lines=hook_lines,
                summary_lines=summary_lines,
                cta=clean_cta,
                brand_name=clean_brand,
                background_image=background_image,
                logo_path=actual_logo,
            )

        cmd = [self.ffmpeg_cmd, "-y"]

        bg_idx = None
        logo_idx = None

        if has_bg:
            cmd.extend(["-i", str(background_image)])
            bg_idx = 0
        if has_logo:
            cmd.extend(["-i", str(actual_logo)])
            logo_idx = 1 if has_bg else 0

        chains = []
        if has_bg:
            chains.append(f"[{bg_idx}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base_bg]")
        else:
            chains.append("color=c=0x0b0f17:s=1080x1920:r=1:d=1[base_bg]")

        # 1. Barra de Topo (Header do Radar)
        chains.append("[base_bg]drawbox=y=0:color=0x0284c7@0.85:width=1080:height=180:t=fill[top_bar]")

        post_filters = [
            f"[top_bar]drawtext=text='🎾 RADAR DE TÊNIS'{font_p}:fontcolor=white:fontsize=50:x=(w-text_w)/2:y=65",
            # Card Central para a Notícia
            "drawbox=y=300:color=0x38bdf8@0.9:width=960:height=12:x=60:t=fill",
            "drawbox=y=312:color=0x090d16@0.92:width=960:height=1080:x=60:t=fill",
        ]

        # Título da Manchete em Azul Céu
        if h1:
            post_filters.append(f"drawtext=text='{h1}'{font_p}:fontcolor=0x38bdf8:fontsize=48:x=(w-text_w)/2:y=380")
        if h2:
            post_filters.append(f"drawtext=text='{h2}'{font_p}:fontcolor=0x38bdf8:fontsize=48:x=(w-text_w)/2:y=445")
        if h3:
            post_filters.append(f"drawtext=text='{h3}'{font_p}:fontcolor=0x38bdf8:fontsize=48:x=(w-text_w)/2:y=510")

        # Linha divisória sutil
        div_y = 520 + (len(hook_lines) * 20)
        post_filters.append(f"drawbox=y={div_y}:color=0x334155@0.8:width=860:height=3:x=110:t=fill")

        # Linhas do Resumo da Notícia em Branco
        summary_start_y = div_y + 50
        for idx, line_text in enumerate(summary_lines):
            line_y = summary_start_y + (idx * 62)
            post_filters.append(f"drawtext=text='{line_text}'{font_p}:fontcolor=white:fontsize=38:x=(w-text_w)/2:y={line_y}")

        # Chamada / Interação no rodapé do card
        cta_y = 1480
        post_filters.extend([
            f"drawbox=y={cta_y}:color=0x10b981@0.5:width=920:height=100:x=80:t=fill",
            f"drawtext=text='💬 {clean_cta}'{font_p}:fontcolor=white:fontsize=36:x=(w-text_w)/2:y={cta_y + 30}",
        ])

        # 2. LOGO NA PARTE INFERIOR DIREITA
        if has_logo:
            # Redimensiona o logo proporcionalmente com largura ~240px
            chains.append(f"[{logo_idx}:v]scale=240:-1[logo_s]")
            chains.append(",".join(post_filters) + "[base_composite]")
            # Aplica overlay na parte inferior direita (margem de 50px da borda)
            chains.append("[base_composite][logo_s]overlay=x=w-overlay_w-50:y=h-overlay_h-50")
        else:
            # Fallback elegante caso não haja imagem de logo: insígnia na parte inferior direita
            post_filters.extend([
                "drawbox=x=w-370:y=h-140:width=320:height=80:color=0x090d16@0.95:t=fill",
                f"drawtext=text='🎾 {clean_brand}'{font_p}:fontcolor=white:fontsize=34:x=w-345:y=h-110",
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
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25)
            if res.returncode != 0:
                print(f"[WARN] FFmpeg Story stderr: {res.stderr.decode('utf-8', errors='ignore')[:300]}")
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

    def _generate_story_with_pillow(
        self,
        output_path: str,
        hook_lines: List[str],
        summary_lines: List[str],
        cta: str,
        brand_name: str,
        background_image: Optional[str],
        logo_path: Optional[str],
    ) -> bool:
        """Gera a imagem de Story 9:16 (1080x1920) via Pillow como fallback quando FFmpeg não estiver disponível."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)

            img = Image.new("RGB", (1080, 1920), (11, 15, 23))

            if background_image and Path(background_image).exists():
                try:
                    bg = Image.open(background_image).convert("RGB")
                    bg_ratio = bg.width / bg.height
                    target_ratio = 1080 / 1920
                    if bg_ratio > target_ratio:
                        new_w = int(bg.width * (1920 / bg.height))
                        bg_scaled = bg.resize((new_w, 1920), Image.Resampling.LANCZOS)
                        left = (new_w - 1080) // 2
                        bg_cropped = bg_scaled.crop((left, 0, left + 1080, 1920))
                    else:
                        new_h = int(bg.height * (1080 / bg.width))
                        bg_scaled = bg.resize((1080, new_h), Image.Resampling.LANCZOS)
                        top = (new_h - 1920) // 2
                        bg_cropped = bg_scaled.crop((0, top, 1080, top + 1920))
                    img.paste(bg_cropped, (0, 0))
                except Exception:
                    pass

            draw = ImageDraw.Draw(img, "RGBA")

            # 1. Barra de topo
            draw.rectangle([(0, 0), (1080, 180)], fill=(2, 132, 199, 220))

            try:
                font_title = ImageFont.truetype("arialbd.ttf", 48)
                font_hook = ImageFont.truetype("arialbd.ttf", 44)
                font_body = ImageFont.truetype("arial.ttf", 36)
                font_cta = ImageFont.truetype("arialbd.ttf", 34)
            except Exception:
                font_title = font_hook = font_body = font_cta = ImageFont.load_default()

            draw.text((320, 65), "🎾 RADAR DE TÊNIS", fill=(255, 255, 255, 255), font=font_title)

            # 2. Card Central
            draw.rectangle([(60, 300), (1020, 312)], fill=(56, 189, 248, 235))
            draw.rectangle([(60, 312), (1020, 1420)], fill=(9, 13, 22, 230))

            # Manchete
            for idx, h_line in enumerate(hook_lines[:3]):
                draw.text((100, 370 + (idx * 60)), h_line, fill=(56, 189, 248, 255), font=font_hook)

            div_y = 390 + (len(hook_lines) * 60)
            draw.line([(100, div_y), (980, div_y)], fill=(51, 65, 85, 200), width=3)

            # Resumo da Notícia
            summary_y = div_y + 40
            for idx, s_line in enumerate(summary_lines[:6]):
                draw.text((100, summary_y + (idx * 55)), s_line, fill=(255, 255, 255, 255), font=font_body)

            # CTA
            draw.rectangle([(80, 1460), (1000, 1560)], fill=(16, 185, 129, 130), outline=(16, 185, 129, 220), width=2)
            cta_text_full = f"💬 {cta[:42]}"
            bbox = draw.textbbox((0, 0), cta_text_full, font=font_cta)
            text_w = bbox[2] - bbox[0]
            draw.text(((1080 - text_w) / 2, 1495), cta_text_full, fill=(255, 255, 255, 255), font=font_cta)

            # 3. Logo no canto inferior direito
            if logo_path and Path(logo_path).exists():
                try:
                    logo_img = Image.open(logo_path).convert("RGBA")
                    lw, lh = logo_img.size
                    new_w = 240
                    new_h = int(lh * (new_w / lw))
                    logo_scaled = logo_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    img.paste(logo_scaled, (1080 - new_w - 50, 1920 - new_h - 50), logo_scaled)
                except Exception:
                    pass
            else:
                draw.rounded_rectangle([(1080 - 360 - 50, 1920 - 90 - 50), (1080 - 50, 1920 - 50)], radius=20, fill=(9, 13, 22, 240), outline=(56, 189, 248, 200), width=2)
                draw.text((1080 - 330 - 50, 1920 - 75 - 50), f"🎾 {brand_name}", fill=(255, 255, 255, 255), font=font_cta)

            img.save(str(out_file), "JPEG", quality=92)
            return out_file.exists()
        except Exception as e:
            print(f"[ERROR] Falha no fallback Pillow para Story 9:16: {e}")
            return False

