"""
Módulo de Filtragem Estratégica e Oportunidades de Conteúdo com Google Gemini.
Responsável por pegar os dados brutos de tendências e notícias e criar a PONTE
com o objetivo de negócio central do Koala Tênis: incentivar os tenistas a
montarem sua própria máquina lançadora de bolas DIY.
"""
import json
from typing import List, Dict, Any, Optional
import httpx

from app.config import get_settings
from app.research.models import ResearchItem, ContentOpportunity

settings = get_settings()

SYSTEM_PROMPT_CONTENT_RADAR = """Você é o Diretor de Estratégia de Conteúdo e Conversão do projeto Koala Tênis (@koalatenis_).

MISSÃO CRÍTICA DO PERFIL:
O foco principal e absoluto do @koalatenis_ é FAZER COM QUE AS PESSOAS MONTEM A SUA PRÓPRIA MÁQUINA LANÇADORA DE BOLAS DE TÊNIS (projeto DIY / Faça Você Mesmo / Engenharia Acessível).
Para atrair o público, o perfil publica conteúdos ricos, divertidos e de alta autoridade sobre o universo do tênis (ATP, biomecânica de saque, forehand, drills, tecnologia).
Porém, TODO CONTEÚDO ESTRATÉGICO deve servir como TOPO OU MEIO DE FUNIL para despertar o desejo ou a necessidade de ter uma máquina de repetição.

SUA TAREFA:
Receba uma lista de notícias, tendências e dados do circuito (ResearchItems).
Para cada item analisado, você deve:
1. Avaliar a relevância e o potencial de engajamento no Instagram (Reels/Carrossel/Feed).
2. Classificar em um dos 6 Pilares:
   - 🎾 Tênis Profissional
   - 🧠 Aprendizado & Biomecânica
   - ⚙️ Tecnologia no Tênis
   - 🔧 DIY & Engenharia
   - 🔥 Tendências
   - 😂 Conteúdo Leve
3. CRIAR A "PONTE KOALA DIY" (diy_ball_machine_angle):
   Como conectar essa notícia/tendência com o treinamento por repetição ou a montagem da máquina de bolas?
   Exemplo: Se Alcaraz bateu recorde de saque -> Ângulo: Como o amador pode treinar devolução na mesma velocidade regulando os motores da máquina DIY.
4. Definir uma nota de relevância estratégica de 1 a 10.
5. Sugerir o melhor formato (REELS, CAROUSEL, FEED ou STORIES).

Responda ESTRITAMENTE em formato JSON com uma lista de oportunidades no formato:
{
  "opportunities": [
    {
      "headline": "Título magnético do post/vídeo",
      "theme": "Tema resumido",
      "source_reference": "Nome da fonte original",
      "pillar": "Pilar temático",
      "relevance_score": 9,
      "diy_ball_machine_angle": "Explicação detalhada de como linkar com a máquina de bolas DIY",
      "suggested_format": "REELS",
      "why_it_matters": "Por que o público vai querer assistir e compartilhar"
    }
  ],
  "featured_headline": "Título da melhor oportunidade para publicar hoje",
  "daily_briefing": "Resumo executivo de 2 parágrafos sobre o cenário de hoje"
}
"""


class ContentOpportunityScorer:
    """Filtra, ranqueia e contextualiza notícias para o universo Koala Tênis usando Gemini."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_TEXT_MODEL or "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def score_and_filter(
        self,
        items: List[ResearchItem],
        profile_data: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[ContentOpportunity]:
        """
        Recebe itens coletados por qualquer adapter e devolve as oportunidades
        lapidadas e conectadas à máquina lançadora de bolas.
        """
        if not items:
            return self._generate_fallback_opportunities(top_k)

        if not self.api_key:
            return self._generate_mock_opportunities(items, top_k)

        # Monta payload com dados compactos dos itens
        items_payload = [item.to_compact_dict() for item in items[:15]]
        profile_context = profile_data or {
            "name": "Koala Tênis",
            "username": "@koalatenis_",
            "goal": "Incentivar tenistas a montarem sua própria máquina lançadora de bolas DIY",
            "pillars": ["Tênis Profissional", "Treinamento", "Tecnologia", "DIY / Robótica", "Humor"],
        }

        user_prompt = f"""PERFIL DO CLIENTE:
{json.dumps(profile_context, ensure_ascii=False, indent=2)}

ITENS RECENTES COLETADOS PELO RADAR (ÚLTIMAS 24H):
{json.dumps(items_payload, ensure_ascii=False, indent=2)}

Analise os itens acima, selecione os {top_k} melhores e crie as oportunidades com a ponte estratégica para a máquina DIY de bolas.
"""

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_CONTENT_RADAR}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.6,
                "response_mime_type": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)

            if resp.status_code != 200:
                print(f"[WARN] Gemini API retornou status {resp.status_code}. Ativando mock scorer.")
                return self._generate_mock_opportunities(items, top_k)

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return self._generate_mock_opportunities(items, top_k)

            text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            clean_json = text_content.strip().removeprefix("```json").removesuffix("```").strip()
            parsed = json.loads(clean_json)

            raw_opps = parsed.get("opportunities", [])
            opportunities: List[ContentOpportunity] = []

            for raw in raw_opps[:top_k]:
                opp = ContentOpportunity(
                    headline=raw.get("headline", "Oportunidade de Tênis"),
                    theme=raw.get("theme", "Treinamento de Tênis"),
                    source_reference=raw.get("source_reference", "Content Radar"),
                    pillar=raw.get("pillar", "🧠 Aprendizado & Biomecânica"),
                    relevance_score=int(raw.get("relevance_score", 8)),
                    diy_ball_machine_angle=raw.get(
                        "diy_ball_machine_angle",
                        "Conectar com o treino repetitivo e consistência usando a máquina de bolas caseira.",
                    ),
                    suggested_format=raw.get("suggested_format", "REELS"),
                    why_it_matters=raw.get("why_it_matters", "Gera alta retenção e educa o jogador."),
                )
                opportunities.append(opp)

            return opportunities
        except Exception as e:
            print(f"[ERROR] Erro ao processar oportunidades no Gemini: {e}")
            return self._generate_mock_opportunities(items, top_k)

    def _generate_mock_opportunities(self, items: List[ResearchItem], limit: int) -> List[ContentOpportunity]:
        """Gera oportunidades estruturadas sem custo de API com base nos itens reais coletados."""
        opps: List[ContentOpportunity] = []
        for idx, item in enumerate(items[:limit]):
            opps.append(
                ContentOpportunity(
                    research_item_id=item.id,
                    headline=f"Como treinar igual aos profissionais: O segredo de {item.title[:45]}",
                    theme=item.title,
                    source_reference=item.source_name,
                    pillar="🔧 DIY & Engenharia" if "machine" in item.title.lower() or "tecnologia" in item.title.lower() else "🧠 Aprendizado & Biomecânica",
                    relevance_score=9 - idx if (9 - idx) >= 5 else 6,
                    diy_ball_machine_angle=(
                        "Demonstrar que profissionais só atingem consistência com repetição exaustiva, "
                        "e que qualquer tenista amador pode ter esse mesmo volume construindo sua própria "
                        "máquina lançadora com componentes acessíveis."
                    ),
                    suggested_format="REELS",
                    why_it_matters="Conecta a admiração pelo tênis profissional com uma solução prática e empoderadora para o jogador.",
                )
            )
        return opps

    def _generate_fallback_opportunities(self, limit: int) -> List[ContentOpportunity]:
        """Garante que nunca retorne vazio mesmo em ausência total de internet."""
        return [
            ContentOpportunity(
                headline="Por que os tenistas profissionais treinam com 500 bolas por hora?",
                theme="Volume de treino e repetição motora no tênis",
                source_reference="Koala Intelligence",
                pillar="🔧 DIY & Engenharia",
                relevance_score=10,
                diy_ball_machine_angle="Mostrar a anatomia da máquina de bolas DIY e como dois motores de alta rotação criam o efeito topspin perfeito.",
                suggested_format="REELS",
                why_it_matters="Desmistifica a tecnologia e prova que construir a própria máquina é acessível e viável.",
            )
        ]
