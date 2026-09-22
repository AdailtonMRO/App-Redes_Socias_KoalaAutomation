# 🎬 Especificação de Renderização de Vídeo com FFmpeg

> **Documento Técnico:** `docs/10_FFMPEG.md`  
> **Versão:** 1.0.0

---

## 1. Padrão Técnico do Vídeo (Meta Instagram Reels)
Para conformidade com os requisitos da Meta Graph API para publicação de Reels:
- **Resolução:** 1080 x 1920 pixels (Proporção vertical 9:16).
- **Codec de Vídeo:** H.264 (`libx264`), perfil `yuv420p` (essencial para compatibilidade com players móveis).
- **Taxa de Quadros (FPS):** 30 fps.
- **Codec de Áudio:** AAC estéreo (`aac`), taxa de amostragem 44.1 kHz, bitrate 128 kbps.
- **Contêiner:** MP4 com flags para streaming rápido (`faststart`).

---

## 2. Implementação Centralizada
Todas as chamadas são executadas exclusivamente pela classe `FFmpegProcessor` no arquivo `app/video/ffmpeg.py`:
- `generate_demo_reel_video(...)`: Gera a composição visual com gradiente Dark Studio, motion typography do gancho e áudio estéreo normalizado.
- `extract_thumbnail(...)`: Extrai a capa em alta definição (`thumb_<id>.jpg`) no segundo 1.0 para pré-visualização.
