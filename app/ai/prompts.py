"""
Prompts e Schemas Estruturados para Geração de Conteúdo com IA (Google Gemini)
Suporta os 4 formatos oficiais do Instagram: REELS, STORIES, FEED e CAROUSEL.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, AliasChoices


# --- ESQUEMAS PARA REELS ---
class SceneSchema(BaseModel):
    scene_number: int = Field(default=1, validation_alias=AliasChoices("scene_number", "numero", "cena", "scene", "id"))
    duration: int = Field(default=4, validation_alias=AliasChoices("duration", "duracao", "tempo"))
    description: str = Field(default="Cena cinematográfica de ação", validation_alias=AliasChoices("description", "descricao", "cena_descricao", "acao"))
    visual_prompt: str = Field(default="Cinematic high speed tennis vertical 9:16", validation_alias=AliasChoices("visual_prompt", "prompt_visual", "prompt", "visual", "video_prompt"))
    narration: str = Field(default="", validation_alias=AliasChoices("narration", "narracao", "locucao", "texto", "audio"))


class ReelScriptSchema(BaseModel):
    format: str = Field("REELS", validation_alias=AliasChoices("format", "formato"))
    title: str = Field("Reel Koala Tênis", validation_alias=AliasChoices("title", "titulo", "tema", "name"))
    hook: str = Field(..., validation_alias=AliasChoices("hook", "gancho", "abertura"))
    objective: str = Field(default="engajamento", validation_alias=AliasChoices("objective", "objetivo"))
    audio_script: str = Field(default="", validation_alias=AliasChoices("audio_script", "roteiro_audio", "narracao_completa"))
    main_visual_prompt: str = Field(default="", validation_alias=AliasChoices("main_visual_prompt", "prompt_visual_principal", "prompt_video"))
    script: str = Field(default="", validation_alias=AliasChoices("script", "roteiro", "narrativa", "conteudo"))
    scenes: List[SceneSchema] = Field(default_factory=list, validation_alias=AliasChoices("scenes", "cenas", "cenas_do_video"))
    caption: str = Field(default="", validation_alias=AliasChoices("caption", "legenda", "descricao_post"))
    hashtags: List[str] = Field(default_factory=list, validation_alias=AliasChoices("hashtags", "tags"))
    cta: str = Field(default="Siga @koalatenis_ para mais!", validation_alias=AliasChoices("cta", "chamada_para_acao", "call_to_action"))


# --- ESQUEMA PARA STORIES (9:16) ---
class StoryScriptSchema(BaseModel):
    format: str = Field("STORIES", validation_alias=AliasChoices("format", "formato"))
    title: str = Field("Story Koala Tênis", validation_alias=AliasChoices("title", "titulo", "tema"))
    stickers_recommended: List[str] = Field(default_factory=list, validation_alias=AliasChoices("stickers_recommended", "adesivos", "stickers"))
    hook: str = Field(default="Radar de Notícias", validation_alias=AliasChoices("hook", "gancho", "frase_impacto", "headline", "manchete", "title", "titulo"))
    body: str = Field(default="", validation_alias=AliasChoices("body", "texto", "mensagem", "corpo", "summary", "resumo", "news_summary", "conteudo"))
    visual_prompt: str = Field(default="Vertical 9:16 tennis lifestyle", validation_alias=AliasChoices("visual_prompt", "prompt_visual", "prompt"))
    call_to_action: str = Field(default="Responda aqui!", validation_alias=AliasChoices("call_to_action", "cta", "chamada_para_acao"))


# --- ESQUEMA PARA POST DE FEED TRADICIONAL (1:1 ou 4:5) ---
class FeedPostSchema(BaseModel):
    format: str = Field("FEED", validation_alias=AliasChoices("format", "formato"))
    title: str = Field("Post Koala Tênis", validation_alias=AliasChoices("title", "titulo", "tema"))
    headline: str = Field(default="Dica de Tênis", validation_alias=AliasChoices("headline", "manchete", "titulo_capa", "title", "titulo", "hook"))
    visual_prompt: str = Field(default="High quality tennis court photography 1:1", validation_alias=AliasChoices("visual_prompt", "prompt_visual", "prompt"))
    caption: str = Field(default="", validation_alias=AliasChoices("caption", "legenda", "texto"))
    hashtags: List[str] = Field(default_factory=list, validation_alias=AliasChoices("hashtags", "tags"))
    cta: str = Field(default="Deixe sua opinião nos comentários!", validation_alias=AliasChoices("cta", "chamada_para_acao", "call_to_action"))


# --- ESQUEMA PARA POST CARROSSEL (SLIDES 1:1) ---
class CarouselSlideSchema(BaseModel):
    slide_number: int = Field(default=1, validation_alias=AliasChoices("slide_number", "numero", "slide"))
    slide_title: str = Field("Dica", validation_alias=AliasChoices("slide_title", "titulo", "slide_titulo"))
    slide_body: str = Field(default="", validation_alias=AliasChoices("slide_body", "texto", "conteudo"))
    visual_prompt: str = Field(default="Minimalist sports slide layout", validation_alias=AliasChoices("visual_prompt", "prompt_visual", "prompt"))


class CarouselSchema(BaseModel):
    format: str = Field("CAROUSEL", validation_alias=AliasChoices("format", "formato"))
    title: str = Field("Carrossel Koala Tênis", validation_alias=AliasChoices("title", "titulo", "tema"))
    cover_hook: str = Field(default="Arrasta para o lado ➡️", validation_alias=AliasChoices("cover_hook", "gancho_capa", "capa", "hook", "title", "titulo"))
    slides: List[CarouselSlideSchema] = Field(default_factory=list, validation_alias=AliasChoices("slides", "slides_educativos"))
    caption: str = Field(default="", validation_alias=AliasChoices("caption", "legenda", "texto"))
    hashtags: List[str] = Field(default_factory=list, validation_alias=AliasChoices("hashtags", "tags"))
    cta: str = Field("Salve este carrossel e compartilhe!", validation_alias=AliasChoices("cta", "chamada_para_acao", "call_to_action"))


SYSTEM_PROMPT_MULTI_FORMAT = """Você é um Diretor Criativo e Especialista em Crescimento de Redes Sociais com foco no Instagram.
Seu papel é criar conteúdos com altíssima retenção, ganchos magnéticos e engajamento no formato especificado pelo usuário (REELS, STORIES, FEED ou CAROUSEL).

DIRETRIZES FUNDAMENTAIS:
1. Respeite as características do formato solicitado:
   - REELS: Vídeo 9:16 com gancho forte nos primeiros segundos. Você DEVE fornecer o `audio_script` completo, o `main_visual_prompt` em inglês (para a IA de vídeo gerar uma cena contínua de alta qualidade) e a lista de `scenes` sincronizadas.
   - STORIES: Comunicação rápida, informal e com sugestão de adesivos interativos. Forneça `title`, `hook`, `body` (resumo claro da notícia/tema) e `call_to_action`.
   - FEED: Imagem única marcante com legenda profunda e educativa. Forneça `title`, `headline`, `caption` e `cta`.
   - CAROUSEL: Conteúdo em etapas lógicas, didático e de alto valor prático para salvar. Forneça `title`, `cover_hook`, `slides` (com `slide_title` e `slide_body`) e `caption`.
2. Responda ESTRITAMENTE em formato JSON com chaves em inglês conforme o formato:
   Para REELS: {"format": "REELS", "title": "...", "hook": "...", "objective": "...", "audio_script": "...", "main_visual_prompt": "...", "script": "...", "scenes": [{"scene_number": 1, "duration": 4, "description": "...", "visual_prompt": "...", "narration": "..."}], "caption": "...", "hashtags": ["..."], "cta": "..."}
   Para STORIES: {"format": "STORIES", "title": "...", "hook": "...", "body": "...", "stickers_recommended": ["..."], "visual_prompt": "...", "call_to_action": "..."}
   Para FEED: {"format": "FEED", "title": "...", "headline": "...", "visual_prompt": "...", "caption": "...", "hashtags": ["..."], "cta": "..."}
   Para CAROUSEL: {"format": "CAROUSEL", "title": "...", "cover_hook": "...", "slides": [{"slide_number": 1, "slide_title": "...", "slide_body": "...", "visual_prompt": "..."}], "caption": "...", "hashtags": ["..."], "cta": "..."}
3. NUNCA invente preços ou promessas que violem a lista de restrições ("avoid") da marca.
"""


def build_prompt_by_format(profile_data: dict, topic: str, content_format: str = "REELS") -> str:
    """Monta o prompt específico para cada tipo de formato, injetando o Profile DNA."""
    identity = profile_data.get('identity', {})
    content = profile_data.get('content', {})
    business = profile_data.get('business', {})
    style = profile_data.get('style', {})
    strategy = profile_data.get('strategy', {})

    base_info = f"""MARCA / PERFIL:
- Nome: {profile_data.get('name')}
- Username: {profile_data.get('username')}

IDENTIDADE:
- Quem somos: {identity.get('who_we_are', '')}
- Público-Alvo: {', '.join(identity.get('audience', []))}
- Posicionamento: {identity.get('positioning', '')}
- Autoridade: {identity.get('authority', '')}
- Personalidade: {identity.get('personality', '')}

CONTEÚDO:
- Pilares: {', '.join(content.get('pillars', []))}
- O que EVITAR (Restrições): {', '.join(content.get('forbidden_topics', []))}

ESTILO E TOM:
- Tom de Voz: {', '.join(style.get('tone', []))}
- Ritmo/Dinâmica: {style.get('rhythm', '')}
- Vocabulário/Jargões: {', '.join(style.get('vocabulary', []))}

NEGÓCIO & ESTRATÉGIA:
- CTAs Aceitos: {', '.join(business.get('ctas', []))}
- Estágio do Funil: {strategy.get('funnel_stage', '')}

TEMA/OPORTUNIDADE A SER TRABALHADA:
"{topic}"
"""
    fmt = content_format.upper()
    if fmt == "CAROUSEL":
        return base_info + "\nCrie um CARROSSEL EDUCATIVO com 5 a 6 slides no formato JSON especificado. O Slide 1 deve ser uma Capa magnética que força o usuário a arrastar para o lado. Respeite o tom e o ritmo da marca."
    elif fmt == "STORIES":
        return base_info + "\nCrie uma sequência de STORIES em formato 9:16 com linguagem rápida, engajadora e sugestão de sticker interativo. Respeite o tom e o ritmo da marca."
    elif fmt == "FEED":
        return base_info + "\nCrie um POST DE FEED tradicional com manchete de capa de alta autoridade e legenda completa, espaçada e estruturada para debate nos comentários. Respeite a autoridade da marca."
    else:
        return base_info + "\nCrie um roteiro viral de REEL (Vídeo 9:16) com gancho nos primeiros segundos, lista de cenas cinematográficas (em visual_prompt para a IA de vídeo) e legenda. Siga estritamente a personalidade e estética da marca."
