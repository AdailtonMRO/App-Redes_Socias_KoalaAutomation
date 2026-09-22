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
        self.model = model or settings.GEMINI_TEXT_MODEL or "gemini-3-flash-preview"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.candidate_models = [self.model, "gemini-3-flash-preview", "gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.1-flash-lite"]
        # Remove duplicatas preservando a ordem
        seen = set()
        self.candidate_models = [m for m in self.candidate_models if not (m in seen or seen.add(m))]

    async def generate_content(
        self,
        profile_data: Dict[str, Any],
        topic: str,
        content_format: str = "REELS",
    ) -> Dict[str, Any]:
        """Gera conteúdo estruturado de acordo com o formato escolhido com fallback automático entre modelos."""
        fmt = content_format.upper()

        if not self.api_key:
            return self._generate_mock_content(profile_data, topic, fmt)

        user_prompt = build_prompt_by_format(profile_data, topic, fmt)
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_MULTI_FORMAT}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "response_mime_type": "application/json",
            },
        }

        last_error = None
        for m in self.candidate_models:
            url = f"{self.base_url}/models/{m}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(url, json=payload)

                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        continue

                    text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    clean_json = text_content.strip()
                    if clean_json.startswith("```"):
                        clean_json = clean_json.split("\n", 1)[1]
                    if clean_json.endswith("```"):
                        clean_json = clean_json.rsplit("```", 1)[0]
                    parsed = json.loads(clean_json.strip())

                    # Validação tipada com suporte a aliases
                    if fmt == "CAROUSEL":
                        validated = CarouselSchema(**parsed)
                    elif fmt == "STORIES":
                        validated = StoryScriptSchema(**parsed)
                    elif fmt == "FEED":
                        validated = FeedPostSchema(**parsed)
                    else:
                        validated = ReelScriptSchema(**parsed)

                    print(f"[INFO] Conteúdo gerado com sucesso via modelo {m} para formato {fmt}")
                    return {"success": True, "data": validated.model_dump(), "format": fmt, "source": f"gemini-api:{m}"}

                elif resp.status_code in (503, 429):
                    print(f"[WARN] Modelo {m} com alta demanda ({resp.status_code}). Tentando modelo alternativo...")
                    last_error = f"Status {resp.status_code}"
                    continue
                else:
                    print(f"[WARN] Falha na Gemini API modelo {m} ({resp.status_code}): {resp.text[:120]}")
                    last_error = f"Status {resp.status_code}"
            except Exception as e:
                print(f"[WARN] Erro ao chamar modelo {m}: {e}. Tentando próximo...")
                last_error = str(e)
                continue

        print(f"[ERROR] Todos os modelos Gemini falharam. Ativando fallback inteligente. Motivo: {last_error}")
        return self._generate_mock_content(profile_data, topic, fmt, note=last_error)

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

        # 1. Tenta gerar via Google Gemini Flash Image (Nano Banana 2 Lite / 3.1)
        if self.api_key:
            # 1.1 Tentativa primária com gemini-3.1-flash-lite-image (1K resolução, alta velocidade)
            flash_img_url = f"{self.base_url}/models/gemini-3.1-flash-lite-image:generateContent?key={self.api_key}"
            flash_payload = {
                "contents": [{"parts": [{"text": f"{prompt}, professional high quality sports photography, sharp focus, vibrant, 4k"}]}],
                "generationConfig": {"responseModalities": ["IMAGE"]},
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(flash_img_url, json=flash_payload)
                    if resp.status_code == 200:
                        cand = resp.json().get("candidates", [{}])[0]
                        parts = cand.get("content", {}).get("parts", [])
                        for p in parts:
                            if "inlineData" in p and "data" in p["inlineData"]:
                                img_bytes = base64.b64decode(p["inlineData"]["data"])
                                if out_file:
                                    with open(out_file, "wb") as f:
                                        f.write(img_bytes)
                                    print(f"[INFO] Imagem gerada com sucesso pelo Gemini 3.1 Flash Image: {out_file}")
                                    return str(out_file)
                    else:
                        print(f"[WARN] Gemini 3.1 Flash Image retornou status {resp.status_code}: {resp.text[:120]}")
            except Exception as e:
                print(f"[WARN] Falha na chamada da API Gemini Flash Image: {e}")

            # 1.2 Tentativa secundária com Imagen 3
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
            # REELS de alta retenção voltado para Koala Tênis e DIY
            mock_data = {
                "format": "REELS",
                "title": f"Como Dominar {topic.title()} com Tecnologia DIY",
                "hook": f"Pare de gastar fortunas em treinos! Veja como {topic} pode transformar sua consistência em quadra.",
                "objective": "autoridade e conversão",
                "script": (
                    f"A repetição exaustiva é o único segredo dos profissionais. "
                    f"Em vez de pagar caro por máquinas importadas, você pode montar seu próprio lançador de bolas com engenharia acessível "
                    f"e treinar {topic} todos os dias."
                ),
                "scenes": [
                    {
                        "scene_number": 1,
                        "duration": 4,
                        "description": "Close dinâmico do movimento e impacto em alta velocidade",
                        "visual_prompt": "Cinematic close-up of a tennis ball being launched at high speed on red clay court, dynamic camera angle, 9:16 vertical video",
                        "narration": f"Quer dominar {topic}? O segredo não é força, é repetição inteligente.",
                    },
                    {
                        "scene_number": 2,
                        "duration": 4,
                        "description": "Demonstração técnica da máquina lançadora e execução do golpe",
                        "visual_prompt": "Athlete hitting repetitive forehands fed by automated ball machine, sunny outdoor tennis court, vertical 9:16 4k",
                        "narration": "Com a máquina lançadora caseira, você treina 500 bolas por hora sem depender de ninguém.",
                    },
                ],
                "caption": (
                    f"🎾 O segredo que os clubes não te contam sobre {topic}!\n\n"
                    f"Consistência se constrói com repetição. E você não precisa gastar R$ 15.000 em uma máquina importada.\n\n"
                    f"Siga o perfil @koalatenis_ para acompanhar o projeto DIY passo a passo!\n\n"
                    f"{cta}"
                ),
                "hashtags": ["#tenis", "#diy", "#maquinalancadora", "#treinotenis", "#koalatenis", "#reelsbrasil"],
                "cta": cta,
            }

        return {"success": True, "data": mock_data, "format": fmt, "source": "mock_generator", "note": note}
