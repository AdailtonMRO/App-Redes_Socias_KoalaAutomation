"""
Prompts e Schemas Estruturados para Geração de Conteúdo com IA (Google Gemini)
Suporta os 4 formatos oficiais do Instagram: REELS, STORIES, FEED e CAROUSEL.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# --- ESQUEMAS PARA REELS ---
class SceneSchema(BaseModel):
    scene_number: int = Field(..., description="Número sequencial da cena")
    duration: int = Field(default=5, description="Duração estimada em segundos (ex: 3 a 7 segundos)")
    description: str = Field(..., description="Descrição visual do que acontece na cena")
    visual_prompt: str = Field(..., description="Prompt detalhado em inglês para o modelo de vídeo Veo")
    narration: str = Field(..., description="Texto da locução ou legenda de tela correspondente")


class ReelScriptSchema(BaseModel):
    format: str = Field("REELS", description="Formato da publicação")
    title: str = Field(..., description="Título interno do Reel")
    hook: str = Field(..., description="Gancho magnético dos primeiros 3 segundos para reter atenção")
    objective: str = Field(..., description="Objetivo principal (engajamento, autoridade, venda)")
    script: str = Field(..., description="Roteiro narrativo completo")
    scenes: List[SceneSchema] = Field(..., description="Lista de cenas sequenciais que compõem o Reel")
    caption: str = Field(..., description="Legenda completa formatada para publicação no Instagram")
    hashtags: List[str] = Field(default_factory=list, description="Lista de 5 a 10 hashtags estratégicas")
    cta: str = Field(..., description="Chamada para ação final direcionando para o perfil/link")


# --- ESQUEMA PARA STORIES (9:16) ---
class StoryScriptSchema(BaseModel):
    format: str = Field("STORIES", description="Formato da publicação")
    title: str = Field(..., description="Tema central do Story")
    stickers_recommended: List[str] = Field(default_factory=list, description="Adesivos recomendados (enquete, caixinha de perguntas, link)")
    hook: str = Field(..., description="Frase de impacto inicial")
    body: str = Field(..., description="Mensagem rápida direta e informal")
    visual_prompt: str = Field(..., description="Prompt visual em 9:16")
    call_to_action: str = Field(..., description="Interação esperada (ex: responda a enquete, mande DM)")


# --- ESQUEMA PARA POST DE FEED TRADICIONAL (1:1 ou 4:5) ---
class FeedPostSchema(BaseModel):
    format: str = Field("FEED", description="Formato da publicação")
    title: str = Field(..., description="Título do post")
    headline: str = Field(..., description="Manchete principal na imagem do post")
    visual_prompt: str = Field(..., description="Prompt para imagem quadrada 1:1 de alta definição")
    caption: str = Field(..., description="Texto rico e aprofundado para leitura no feed")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags para alcance")
    cta: str = Field(..., description="Pergunta final para incentivar comentários e salvamentos")


# --- ESQUEMA PARA POST CARROSSEL (SLIDES 1:1) ---
class CarouselSlideSchema(BaseModel):
    slide_number: int = Field(..., description="Número sequencial do slide (1 a 7)")
    slide_title: str = Field(..., description="Título curto e impactante do slide")
    slide_body: str = Field(..., description="Texto explicativo conciso (máximo 2 a 3 frases)")
    visual_prompt: str = Field(..., description="Descrição visual do design do slide")


class CarouselSchema(BaseModel):
    format: str = Field("CAROUSEL", description="Formato carrossel multi-slides")
    title: str = Field(..., description="Tema do carrossel")
    cover_hook: str = Field(..., description="Título irresistível da Capa (Slide 1) que faz a pessoa arrastar")
    slides: List[CarouselSlideSchema] = Field(..., description="Sequência de 4 a 7 slides educativos")
    caption: str = Field(..., description="Legenda completa que complementa o carrossel")
    hashtags: List[str] = Field(default_factory=list, description="Hashtags estratégicas")
    cta: str = Field("Salve este carrossel e compartilhe!", description="Chamada final para ação no último slide")


SYSTEM_PROMPT_MULTI_FORMAT = """Você é um Diretor Criativo e Especialista em Crescimento de Redes Sociais com foco no Instagram.
Seu papel é criar conteúdos com alta retenção e engajamento no formato especificado pelo usuário (REELS, STORIES, FEED ou CAROUSEL).

DIRETRIZES:
1. Respeite as características do formato solicitado:
   - REELS: Vídeo 9:16 com gancho forte nos primeiros 3 segundos.
   - STORIES: Comunicação rápida, informal e com sugestão de adesivos interativos.
   - FEED: Imagem única marcante com legenda profunda e educativa.
   - CAROUSEL: Conteúdo em etapas lógicas, didático e de alto valor prático para salvar.
2. NUNCA invente preços ou promessas que violem a lista de restrições ("avoid") da marca.
3. Responda ESTRITAMENTE em formato JSON compatível com o formato solicitado.
"""


def build_prompt_by_format(profile_data: dict, topic: str, content_format: str = "REELS") -> str:
    """Monta o prompt específico para cada tipo de formato."""
    base_info = f"""MARCA / PERFIL:
- Nome: {profile_data.get('name')}
- Username: {profile_data.get('username')}
- Nichos: {', '.join(profile_data.get('niche', []))}
- Público-Alvo: {', '.join(profile_data.get('audience', []))}
- Tom de Voz: {', '.join(profile_data.get('tone', []))}
- CTA Padrão: {profile_data.get('cta')}
- O que EVITAR: {', '.join(profile_data.get('avoid', []))}

TEMA DO CONTEÚDO:
"{topic}"
"""
    fmt = content_format.upper()
    if fmt == "CAROUSEL":
        return base_info + "\nCrie um CARROSSEL EDUCATIVO com 5 a 6 slides no formato JSON especificado. O Slide 1 deve ser uma Capa magnética que força o usuário a arrastar para o lado."
    elif fmt == "STORIES":
        return base_info + "\nCrie uma sequência de STORIES em formato 9:16 com linguagem rápida, engajadora e sugestão de sticker interativo."
    elif fmt == "FEED":
        return base_info + "\nCrie um POST DE FEED tradicional com manchete de capa de alta autoridade e legenda completa, espaçada e estruturada para debate nos comentários."
    else:
        return base_info + "\nCrie um roteiro viral de REEL (Vídeo 9:16) com gancho nos 3 primeiros segundos, lista de cenas cinematográficas e legenda com hashtags."
