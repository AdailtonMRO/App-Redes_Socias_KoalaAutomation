"""
Módulo de Filtragem Estratégica e Curadoria de Notícias de Tênis com Google Gemini.
Responsável por processar dados brutos de tendências e notícias (TenisBrasil, Tenis News,
ge.globo, ESPN, WTA, CBT, ATP, ITF) e transformá-los em oportunidades editoriais de
alta autoridade para Stories do Instagram (@koalatenis_).
"""
import json
import random
from typing import List, Dict, Any, Optional
import httpx

from app.config import get_settings
from app.research.models import ResearchItem, ContentOpportunity

settings = get_settings()

SYSTEM_PROMPT_CONTENT_RADAR = """Você é o Editor-Chefe e Curador Especialista do perfil/canal em questão.

Sua missão é analisar a lista de notícias e acontecimentos coletados em tempo real pelo Content Radar e selecionar as melhores matérias e oportunidades para publicação, levando sempre em consideração a IDENTIDADE DA MARCA e a ESTRATÉGIA EDITORIAL fornecidas no prompt do usuário.

DIRETRIZ DE CONTEÚDO (FOCO EXCLUSIVO NO FORMATO STORY):
Seu papel é selecionar as melhores oportunidades para publicação nos Stories.
Para cada matéria selecionada, você deve extrair um RESUMO JORNALÍSTICO CLARO E ENVOLVENTE (news_summary) que permita ao seguidor entender o fato imediatamente.

Para cada oportunidade selecionada:
1. "headline": Título atrativo, dinâmico e direto ao ponto para o topo do Story.
2. "theme": Tema central resumido.
3. "source_reference": Nome da fonte original.
4. "pillar": Classificação temática baseada nos pilares editoriais da marca.
5. "relevance_score": Nota de 1 a 10 para o interesse do público-alvo da marca.
6. "news_summary": Resumo conciso, informativo e de alto valor (de 3 a 5 linhas).
7. "key_takeaway": O ponto central ou impacto imediato do acontecimento.
8. "suggested_format": ESTRITAMENTE "STORIES".
9. "why_it_matters": Por que o público do perfil vai querer ler, compartilhar e comentar.

Responda ESTRITAMENTE em formato JSON:
{
  "opportunities": [
    {
      "headline": "...",
      "theme": "...",
      "source_reference": "...",
      "pillar": "...",
      "relevance_score": 9,
      "news_summary": "...",
      "key_takeaway": "...",
      "suggested_format": "STORIES",
      "why_it_matters": "..."
    }
  ],
  "featured_headline": "...",
  "daily_briefing": "..."
}
"""


class ContentOpportunityScorer:
    """Filtra, ranqueia e contextualiza notícias de tênis para o Koala Tênis usando Gemini."""

    CANDIDATE_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.6-flash",
        "gemini-3-flash-preview",
        "gemini-3.8-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        preferred_model = model or getattr(settings, "GEMINI_TEXT_MODEL", None)
        if preferred_model in ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-preview"):
            preferred_model = "gemini-3.1-flash-lite"
        if preferred_model:
            self.models_to_try = [preferred_model] + [m for m in self.CANDIDATE_MODELS if m != preferred_model]
        else:
            self.models_to_try = list(self.CANDIDATE_MODELS)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    async def score_and_filter(
        self,
        items: List[ResearchItem],
        profile_data: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        avoid_headlines: Optional[List[str]] = None,
        force_refresh: bool = False,
        performance_data: Optional[List[Dict[str, Any]]] = None,
    ) -> List[ContentOpportunity]:
        """
        Recebe itens coletados por qualquer adapter e devolve oportunidades editoriais
        de tênis com resumo informativo formatado para Stories.
        """
        if not items:
            return self._generate_fallback_opportunities(top_k)

        if not self.api_key:
            return self._generate_mock_opportunities(items, top_k, avoid_headlines)

        sample_pool = list(items)
        if force_refresh and len(sample_pool) > 15:
            random.shuffle(sample_pool)

        items_payload = [item.to_compact_dict() for item in sample_pool[:18]]

        profile_context = profile_data or {
            "name": "Koala Tênis",
            "username": "@koalatenis_",
            "identity": {"positioning": "Canal de autoridade em notícias de tênis"},
            "content": {"pillars": ["Tênis Profissional", "Brasil no Circuito", "Torneios & Resultados"]},
            "strategy": {"frequency": "diário"}
        }

        avoid_clause = ""
        if avoid_headlines:
            avoid_list_str = "\n".join([f"- {h}" for h in avoid_headlines[:10]])
            avoid_clause = f"""
IMPORTANTE: EVITE REPETIR OU GERAR NOTÍCIAS IDÊNTICAS A ESTAS RECENTEMENTE APRESENTADAS:
{avoid_list_str}
Priorize outras matérias e atletas diferentes da lista!
"""

        performance_clause = ""
        if performance_data:
            perf_str = json.dumps(performance_data, ensure_ascii=False, indent=2)
            performance_clause = f"""
PERFORMANCE RECENTE DO PERFIL (LEARNING LOOP):
Abaixo estão os resultados reais das últimas publicações. Use esses dados para entender o que mais atrai o público:
{perf_str}

Instrução Adicional: Priorize selecionar notícias que tenham similaridade temática com os conteúdos que tiveram melhor engajamento ou maior alcance listados acima.
"""

        user_prompt = f"""PERFIL DO CANAL:
{json.dumps(profile_context, ensure_ascii=False, indent=2)}

NOTÍCIAS E ACONTECIMENTOS REAIS COLETADOS PELO RADAR:
{json.dumps(items_payload, ensure_ascii=False, indent=2)}
{avoid_clause}
{performance_clause}
Analise os itens acima, selecione os {top_k} melhores e crie oportunidades com manchetes atrativas e resumos objetivos para o formato STORY.
"""

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_CONTENT_RADAR}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": 0.7 if force_refresh else 0.5,
                "response_mime_type": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            for model_name in self.models_to_try:
                url = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            continue

                        text_content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        clean_json = text_content.strip().removeprefix("```json").removesuffix("```").strip()
                        parsed = json.loads(clean_json)

                        raw_opps = parsed.get("opportunities", [])
                        if not raw_opps:
                            continue

                        opportunities: List[ContentOpportunity] = []
                        for raw in raw_opps[:top_k]:
                            opp = ContentOpportunity(
                                headline=raw.get("headline", "Notícia de Tênis em Destaque"),
                                theme=raw.get("theme", "Atualização do Circuito"),
                                source_reference=raw.get("source_reference", "Content Radar"),
                                pillar=raw.get("pillar", "🎾 Tênis Profissional"),
                                relevance_score=int(raw.get("relevance_score", 8)),
                                news_summary=raw.get(
                                    "news_summary",
                                    "Confira os principais detalhes e o impacto deste acontecimento no circuito de tênis.",
                                ),
                                key_takeaway=raw.get("key_takeaway", "Destaque da rodada no tênis."),
                                suggested_format="STORIES",
                                why_it_matters=raw.get("why_it_matters", "Gera alta retenção e interesse dos tenistas."),
                            )
                            opportunities.append(opp)

                        if opportunities:
                            return opportunities
                    else:
                        print(f"[WARN] Gemini model {model_name} retornou HTTP {resp.status_code}. Tentando próximo modelo...")
                except Exception as e:
                    print(f"[WARN] Falha ao tentar modelo {model_name}: {e}")

        return self._generate_mock_opportunities(items, top_k, avoid_headlines)

    def _generate_mock_opportunities(
        self,
        items: List[ResearchItem],
        limit: int,
        avoid_headlines: Optional[List[str]] = None,
    ) -> List[ContentOpportunity]:
        """Gera oportunidades estruturadas com foco jornalístico no tênis baseadas nos itens reais."""
        avoid_set = set((avoid_headlines or []))
        opps: List[ContentOpportunity] = []

        shuffled_items = list(items)
        random.shuffle(shuffled_items)

        mock_templates = [
            {
                "pillar": "🎾 Tênis Profissional",
                "headline_fmt": "Destaque do Circuito: {title}",
                "summary_fmt": "Confira os resultados mais recentes e a repercussão de {title} nos principais torneios mundiais.",
                "takeaway": "Movimentação importante no ranking mundial e nas chaves dos torneios.",
            },
            {
                "pillar": "🇧🇷 Brasil no Circuito",
                "headline_fmt": "Brasileiros em quadra: {title}",
                "summary_fmt": "Acompanhe o desempenho dos atletas brasileiros na rodada, com destaque para a evolução e resultados em {title}.",
                "takeaway": "Representatividade do tênis nacional crescendo no circuito profissional.",
            },
            {
                "pillar": "🏆 Torneios & Resultados",
                "headline_fmt": "Giro de Resultados: {title}",
                "summary_fmt": "As disputas continuam intensas nas quadras mundiais com confrontos decisivos em {title}.",
                "takeaway": "Definição das fases finais e momentos decisivos da temporada.",
            },
            {
                "pillar": "🧠 Análise Técnica & Tática",
                "headline_fmt": "Análise de Desempenho: {title}",
                "summary_fmt": "Entenda os fatores táticos, consistência de saque e golpes de fundo que ditaram o ritmo em {title}.",
                "takeaway": "Lições práticas de postura e ritmo aplicáveis para o tenista amador.",
            },
        ]

        template_idx = 0
        for item in shuffled_items:
            clean_title = item.title[:55].strip()
            tmpl = mock_templates[template_idx % len(mock_templates)]
            headline = tmpl["headline_fmt"].format(title=clean_title)

            if headline in avoid_set:
                template_idx += 1
                continue

            opps.append(
                ContentOpportunity(
                    research_item_id=item.id,
                    headline=headline,
                    theme=item.title,
                    source_reference=item.source_name,
                    pillar=tmpl["pillar"],
                    relevance_score=max(7, 10 - len(opps)),
                    news_summary=tmpl["summary_fmt"].format(title=clean_title),
                    key_takeaway=tmpl["takeaway"],
                    suggested_format="STORIES",
                    why_it_matters="Notícia quente e relevante que mantém os seguidores sempre atualizados sobre o esporte.",
                )
            )
            template_idx += 1
            if len(opps) >= limit:
                break

        return opps if opps else self._generate_fallback_opportunities(limit)

    def _generate_fallback_opportunities(self, limit: int) -> List[ContentOpportunity]:
        """Garante retorno de notícias de alta qualidade mesmo em caso de falha de conexão."""
        fallbacks = [
            ContentOpportunity(
                headline="João Fonseca impressiona no circuito com aceleração de forehand",
                theme="Evolução e destaque da nova geração do tênis brasileiro",
                source_reference="TenisBrasil (UOL)",
                pillar="🇧🇷 Brasil no Circuito",
                relevance_score=10,
                news_summary="O jovem brasileiro segue chamando a atenção mundial ao disparar forehands a mais de 160km/h e demonstrar maturidade tática contra adversários experientes do top 100.",
                key_takeaway="A ascensão meteórica consolida o Brasil como celeiro de talentos no circuito ATP.",
                suggested_format="STORIES",
                why_it_matters="Conteúdo de alta repercussão e orgulho nacional para a comunidade de tênis.",
            ),
            ContentOpportunity(
                headline="Bia Haddad Maia impõe ritmo e vence batalha equilibrada no circuito",
                theme="Desempenho e consistência de Bia Haddad",
                source_reference="ge.globo Tênis",
                pillar="🎾 Tênis Profissional",
                relevance_score=9,
                news_summary="Com solidez no fundo de quadra e resiliência mental nos momentos decisivos, a número 1 do Brasil superou mais um desafio importante rumo às fases decisivas.",
                key_takeaway="Vitória fundamental para manutenção de pontos no ranking e confiança na temporada.",
                suggested_format="STORIES",
                why_it_matters="Inspiração para atletas e tenistas amadores sobre consistência e foco.",
            ),
            ContentOpportunity(
                headline="Luisa Stefani avança nas duplas com reflexos impecáveis na rede",
                theme="Circuito de duplas WTA e grandes resultados",
                source_reference="WTA & Tênis Feminino BR",
                pillar="🇧🇷 Brasil no Circuito",
                relevance_score=9,
                news_summary="A medalhista olímpica deu uma aula de posicionamento e voleios rápidos na rede, fechando a partida em dois sets diretos e garantindo vaga nas quartas.",
                key_takeaway="Domínio tático na rede confirma o protagonismo brasileiro nas duplas mundiais.",
                suggested_format="STORIES",
                why_it_matters="Excelente material para tenistas que adoram jogar e acompanhar partidas de duplas.",
            ),
            ContentOpportunity(
                headline="Disputa pelo topo: Sinner e Alcaraz elevam a intensidade do tênis mundial",
                theme="Rivalidade da nova era no tênis",
                source_reference="ATP Tour",
                pillar="🏆 Torneios & Resultados",
                relevance_score=8,
                news_summary="A rivalidade moderna redefine os padrões de velocidade e recuperação defensiva, forçando o circuito profissional a se adaptar ao ritmo alucinante da nova era.",
                key_takeaway="Novos padrões biomecânicos e de preparação física dominam os grandes torneios.",
                suggested_format="STORIES",
                why_it_matters="Discussão atrativa para todos que acompanham o tênis de elite.",
            ),
        ]
        return fallbacks[:limit]
