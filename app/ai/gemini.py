"""
Cliente de Inteligência Artificial com Google Gemini API
Gera roteiros estratégicos e publicações para REELS, STORIES, FEED e CARROSSEL.
"""
import json
from typing import Dict, Any, Optional
import httpx
from app.config import get_settings
from app.ai.prompts import (
    SYSTEM_PROMPT_MULTI_FORMAT,
    ReelScriptSchema,
    StoryScriptSchema,
    FeedPostSchema,
    CarouselSchema,
    build_prompt_by_format,
)

settings = get_settings()


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_TEXT_MODEL or "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def generate_content(
        self,
        profile_data: Dict[str, Any],
        topic: str,
        content_format: str = "REELS",
    ) -> Dict[str, Any]:
        """Gera conteúdo estruturado de acordo com o formato escolhido."""
        fmt = content_format.upper()

        if not self.api_key:
            return self._generate_mock_content(profile_data, topic, fmt)

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        user_prompt = build_prompt_by_format(profile_data, topic, fmt)

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_MULTI_FORMAT}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "response_mime_type": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                print(f"[WARN] Falha na Gemini API ({resp.status_code}): {resp.text}")
                return self._generate_mock_content(profile_data, topic, fmt, note="Fallback ativado por status != 200")

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return self._generate_mock_content(profile_data, topic, fmt)

            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            clean_json = text_content.strip().removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(clean_json)

            # Validação tipada de acordo com o formato
            if fmt == "CAROUSEL":
                validated = CarouselSchema(**parsed)
            elif fmt == "STORIES":
                validated = StoryScriptSchema(**parsed)
            elif fmt == "FEED":
                validated = FeedPostSchema(**parsed)
            else:
                validated = ReelScriptSchema(**parsed)

            return {"success": True, "data": validated.model_dump(), "format": fmt, "source": "gemini-api"}
        except Exception as e:
            print(f"[ERROR] Erro ao validar JSON do Gemini para formato {fmt}: {e}")
            return self._generate_mock_content(profile_data, topic, fmt, note=str(e))

    async def generate_reel_script(self, profile_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Alias para compatibilidade retroativa com geração de Reels."""
        res = await self.generate_content(profile_data, topic, "REELS")
        return {"success": res.get("success", False), "script": res.get("data", {})}

    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        output_path: Optional[str] = None,
        keywords: Optional[str] = None,
    ) -> Optional[str]:
        """Gera imagem fotorrealista via Google Imagen 3 ou obtém foto contextual de alta definição."""
        import base64
        import random
        from pathlib import Path

        out_file = Path(output_path) if output_path else None
        if out_file:
            out_file.parent.mkdir(parents=True, exist_ok=True)

        # 1. Tenta gerar via Google Imagen 3 na Google AI Studio API
        if self.api_key:
            url = f"{self.base_url}/models/imagen-3.0-generate-002:predict?key={self.api_key}"
            payload = {
                "instances": [{"prompt": f"{prompt}, professional sports photography, high definition, sharp focus, 4k"}],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": "1:1" if aspect_ratio == "1:1" else "9:16",
                    "outputMimeType": "image/jpeg",
                },
            }
            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        predictions = data.get("predictions", [])
                        if predictions and "bytesBase64Encoded" in predictions[0]:
                            img_bytes = base64.b64decode(predictions[0]["bytesBase64Encoded"])
                            if out_file:
                                with open(out_file, "wb") as f:
                                    f.write(img_bytes)
                                print(f"[INFO] Imagem gerada com sucesso pelo Google Imagen 3: {out_file}")
                                return str(out_file)
                    else:
                        print(f"[WARN] Google Imagen 3 retornou status {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                print(f"[WARN] Falha na chamada da API Imagen 3: {e}")

        # 2. Fallback Fotográfico Contextual de Alta Resolução
        # Garante que NUNCA fique um bloco vazio se a cota do Imagen 3 estiver restrita
        photo_library = [
            "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?q=80&w=1080&auto=format&fit=crop", # Quadra e bola de tênis
            "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?q=80&w=1080&auto=format&fit=crop", # Raquete e movimento de tênis
            "https://images.unsplash.com/photo-1542144582-1ba00456b5e3?q=80&w=1080&auto=format&fit=crop", # Partida de saibro
            "https://images.unsplash.com/photo-1530915365347-e35b71eb2794?q=80&w=1080&auto=format&fit=crop", # Saque e atleta
            "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?q=80&w=1080&auto=format&fit=crop", # Detalhes da quadra de tênis
            "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?q=80&w=1080&auto=format&fit=crop", # Treinamento esportivo
        ]
        chosen_url = random.choice(photo_library)
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                r = await client.get(chosen_url)
                if r.status_code == 200 and out_file:
                    with open(out_file, "wb") as f:
                        f.write(r.content)
                    print(f"[INFO] Foto esportiva contextual aplicada como plano de fundo: {out_file}")
                    return str(out_file)
        except Exception as e:
            print(f"[WARN] Erro ao baixar foto de fallback contextual: {e}")

        return None

    def _generate_mock_content(self, profile: Dict[str, Any], topic: str, fmt: str, note: Optional[str] = None) -> Dict[str, Any]:
        """Gera conteúdos sintéticos de demonstração para qualquer um dos 4 formatos."""
        brand = profile.get("name", "Koala Tênis")
        cta = profile.get("cta", "Siga para mais dicas no link da bio!")

        if fmt == "CAROUSEL":
            mock_data = {
                "format": "CAROUSEL",
                "title": f"Guia Prático: {topic.title()}",
                "cover_hook": f"Arrasta para o lado ➡️ O segredo de {topic} que ninguém te conta!",
                "slides": [
                    {
                        "slide_number": 1,
                        "slide_title": "Slide 1: A Capa",
                        "slide_body": f"Você ainda tem dúvidas sobre {topic}? Veja este passo a passo até o final.",
                        "visual_prompt": "Capa com tipografia grande e limpa em fundo gradiente escuro",
                    },
                    {
                        "slide_number": 2,
                        "slide_title": "Slide 2: O Ponto Crítico",
                        "slide_body": "O maior erro é começar sem a postura e o ângulo correto de movimento.",
                        "visual_prompt": "Ilustração técnica do movimento correto",
                    },
                    {
                        "slide_number": 3,
                        "slide_title": "Slide 3: O Ajuste Fino",
                        "slide_body": "Ao manter a aceleração constante, seu controle e precisão sobem 40%.",
                        "visual_prompt": "Gráfico ou visual explicativo",
                    },
                    {
                        "slide_number": 4,
                        "slide_title": "Slide 4: Resumo Prático",
                        "slide_body": f"Aplique isso no seu próximo treino e comente o resultado aqui embaixo!\n{cta}",
                        "visual_prompt": "Slide final com botão de salvar e ícone de compartilhar",
                    },
                ],
                "caption": f"📚 Salve este carrossel completo para consultar sempre que for treinar {topic}!\n\nDeixe seu comentário com a sua maior dúvida!\n\n{cta}",
                "hashtags": ["#carrossel", "#dicas", "#treino", "#tenisbrasil"],
                "cta": cta,
            }
        elif fmt == "STORIES":
            mock_data = {
                "format": "STORIES",
                "title": f"Story Rápido: {topic}",
                "stickers_recommended": ["Enquete: Você já sabia dessa?", "Link na Bio"],
                "hook": f"🎾 Dica rápida do dia sobre {topic}!",
                "body": f"Passando rapidinho para lembrar que a postura correta em {topic} faz toda a diferença.\n\nVocê costuma praticar isso?",
                "visual_prompt": "Foto vertical 9:16 de bastidores ou da quadra de tênis com iluminação natural",
                "call_to_action": "Responda à enquete e me mande uma mensagem se quiser a dica completa!",
            }
        elif fmt == "FEED":
            mock_data = {
                "format": "FEED",
                "title": f"Tudo sobre {topic.title()}",
                "headline": f"Por que a maioria erra em {topic}?",
                "visual_prompt": "Post clean quadrado 1:1 com tipografia forte e logo sutil",
                "caption": (
                    f"🎾 Dominar {topic} exige consistência e técnica.\n\n"
                    f"Muitas vezes focamos apenas na força, quando o segredo está na leitura de tempo de bola e na preparação antecipada.\n\n"
                    f"👉 Salve este post e compartilhe com seu parceiro de jogo!\n\n"
                    f"{cta}"
                ),
                "hashtags": ["#tenis", "#treinamento", "#dicasdetenis", "#feedpost"],
                "cta": "Você concorda? Deixe sua opinião nos comentários!",
            }
        else:
            # REELS padrão
            mock_data = {
                "format": "REELS",
                "title": f"Segredo de {topic.title()}",
                "hook": f"Você ainda comete esse erro em {topic}? Pare agora!",
                "objective": "engajamento",
                "script": f"Descubra a técnica que transforma seu jogo em {topic}.",
                "scenes": [
                    {"scene_number": 1, "duration": 4, "description": "Gancho inicial", "visual_prompt": "Vertical action", "narration": f"Erro clássico em {topic}"},
                    {"scene_number": 2, "duration": 5, "description": "Técnica correta", "visual_prompt": "Slow motion precision", "narration": "Ajuste a rotação e ponto de impacto"},
                ],
                "caption": f"🎾 O erro mais comum em {topic}!\n\n{cta}",
                "hashtags": ["#reels", "#tenis", "#viral"],
                "cta": cta,
            }

        return {"success": True, "data": mock_data, "format": fmt, "source": "mock_generator", "note": note}
