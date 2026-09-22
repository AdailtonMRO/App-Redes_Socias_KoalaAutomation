# 📜 Registro Histórico de Mudanças (Changelog)

Todas as alterações notáveis deste projeto são registradas neste arquivo.

---

## [1.4.0] — 2026-09-22

### 🎾 Content Radar Puro em Notícias e Geração de Story Estático 9:16 com Logo
- **Remoção Completa da Ponte DIY de Máquina de Bolas:** O Content Radar passa a atuar 100% como curador de notícias esportivas de alta relevância (TenisBrasil, ge.globo, Tenis News, WTA, CBT, ATP), eliminando a forçação de ganchos sobre máquinas de bolas caseiras.
- **Formato Exclusivo Story (Imagem Estática 9:16):** As oportunidades do Radar agora geram exclusivamente imagens estáticas verticais (1080x1920) em vez de vídeos, contendo a manchete e o resumo diagramado do assunto pesquisado pela IA.
- **Logomarca no Canto Inferior Direito:** A imagem do Story agora sobrepõe obrigatoriamente a logomarca oficial do perfil no canto inferior direito (`x=w-overlay_w-50:y=h-overlay_h-50`), com fallback para badge de marca caso não haja arquivo.
- **Asset Oficial `profiles/koalatenis_logo.png`:** Criada a logomarca transparente em alta definição para o `@koalatenis_` e vinculada no `profiles/koalatenis.json`.
- **Rebalanceamento de Pesos (`ResearchScorer`):** Ajustados os pesos heurísticos para priorizar astros brasileiros (João Fonseca, Bia Haddad, Luisa Stefani, Thiago Wild, CBT), torneios do Grand Slam e circuito profissional.
- **Resiliência de Renderização:** Suporte a renderização via FFmpeg nativo e fallback automático de alta resolução via Pillow para ambientes sem o binário do FFmpeg.

---

## [1.3.0] — 2026-09-22


### 📡 Expansão Completa do Content Radar (Portais Brasileiros, Rotação Anti-Repetição e Ponte DIY)
- **Novos Adapters Especializados:**
  - `BrazilianTennisAdapter`: Coleta em tempo real via feeds RSS nativos de TenisBrasil (UOL), Tenis News e Diário do Tênis.
  - `SportsPortalsAdapter`: Monitora notícias de tênis filtradas nos maiores portais de mídia esportiva do Brasil (ge.globo, ESPN Brasil e UOL Esporte).
  - `WTAAndCBTAdapter`: Acompanhamento segmentado de tênis feminino (Bia Haddad Maia, Luisa Stefani, Laura Pigossi) e competições nacionais/juvenis da Confederação Brasileira de Tênis (CBT, Copa Davis, BJK Cup).
  - `NewsAdapter`: Modernizado com query dinâmica abrangente sem aspas restritivas que sufocavam os resultados.
- **Mecanismo Dinâmico de Anti-Repetição:**
  - Histórico de manchetes recentes em memória para evitar que o `/radar` traga os mesmos tópicos em chamadas subsequentes.
  - Cláusula de exclusão dinâmica de temas recentes no prompt enviado ao Google Gemini.
  - Botão interativo `🔄 Atualizar Notícias` no Telegram Bot com parâmetro `refresh=True` para forçar geração de novos ângulos.
- **Ponte Estratégica Koala Tênis Aprimorada no Gemini:**
  - Prompt calibrado com astros do tênis nacional e internacional (João Fonseca, Bia Haddad, Luisa Stefani, Alcaraz, Sinner, Djokovic) conectando a alta performance e técnicas de jogo diretamente à montagem e calibração da Máquina Lançadora de Bolas DIY.
- **Suporte Robusto a Modelos no ContentOpportunityScorer:**
  - Cascata automática de modelos Gemini (`gemini-3-flash-preview`, `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-2.5-flash-preview`) com substituição preventiva de modelos descontinuados.

---

## [1.2.2] — 2026-09-22


### 🎬 Correção Definitiva do Google Veo e Schemas com AliasChoices
- **Correção de Parâmetro Inválido no Google Veo 3.1:** Removido o parâmetro `"personGeneration": "allow_adult"` (não suportado na API v1beta do Veo 3.1), permitindo que a geração de vídeo real via IA conclua com código HTTP 200.
- **Pydantic AliasChoices nos Schemas de Conteúdo:** Adicionado suporte flexível a chaves em português e inglês (`title`/`titulo`/`tema`, `hook`/`gancho`, `scenes`/`cenas`, etc.) com valores padrão seguros, impedindo que variações de resposta do Gemini disparem fallbacks indevidos para o gerador sintético.
- **Lista de Fallback de Modelos Gemini:** `GeminiClient` agora percorre automaticamente uma lista de modelos (`gemini-3-flash-preview`, `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.1-flash-lite`) em caso de picos de demanda temporários (503/429).
- **Roteiros de Fallback Alinhados ao Koala Tênis DIY:** Atualizado o gerador mock para criar narrativas de alta autoridade focadas na construção da máquina lançadora de bolas e consistência em quadra.
- **Robustez no Envio de Vídeos no Telegram:** Adicionado tratamento de erro com retry em texto puro caso haja falha de formatação Markdown na legenda do vídeo.

---

## [1.2.1] — 2026-09-22

### 🎬 Correção e Modernização dos Modelos Google AI (Gemini 3.6, Image Lite e Veo 3.1)
- **Atualização do Modelo Veo para `veo-3.1-lite-generate-preview`:** Substituído o modelo descontinuado `veo-2.0-generate-001` pela versão moderna 3.1 Lite com suporte nativo na API Key do projeto. Duração calibrada para 4 segundos.
- **Correção no Download de Vídeos Veo:** Adicionada autenticação com API Key na URL de download dos artefatos da Google Files API (`&key=...`), prevenindo erros 403/404 pós-renderização.
- **Atualização do Gemini Text para `gemini-3.6-flash`:** Migrado do obsoleto `gemini-2.5-flash` para `gemini-3.6-flash` garantindo geração instantânea de roteiros estruturados em JSON sem avisos de descontinuação.
- **Geração de Imagens via `gemini-3.1-flash-lite-image`:** Suporte a geração de imagens 1K usando `responseModalities: ["IMAGE"]` com fallback robusto para fotos esportivas de alta definição.
- **Saneamento do FFmpeg no Cinema Motion Engine:** Limpeza de declarações redundantes de comandos na renderização de vídeos verticais locais.

---

## [1.2.0] — 2026-09-22

### 🤖 Governança de Agentes de IA
- Criado o sistema formal de regras para agentes de IA em `.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md` com 8 regras inegociáveis cobrindo documentação, versionamento, segurança e deploy. (`governança`)
- Adicionado template e primeiro ADR (ADR-001) em `docs/archive/` documentando a decisão arquitetural de adoção do sistema de governança. (`docs/archive/`)

### 📚 Documentação
- Especificação completa do Content Radar, contrato normalizado ResearchItem, cronograma diário e 6 pilares de conteúdo do Koala Tênis (`docs/18_CONTENT_RADAR.md`)
- Criado `docs/19_DEPLOY_HOMELAB.md`: guia completo de deploy no servidor HomeLab (10.0.0.119), cobrindo deploy automático via GitHub Actions, deploy manual passo a passo, rollback, troubleshooting e checklist PRD. (`docs/`)
- Atualizado `docs/00_INDEX.md`: adicionadas seções de Governança de Agentes de IA, ADR e tabela de scripts de automação. (`docs/00_INDEX.md`)
- Atualizado `docs/00_REGRAS_E_DIRETRIZES.md`: adicionadas Seções 11 (Governança para Agentes de IA) e 12 (Deploy no HomeLab). (`docs/00_REGRAS_E_DIRETRIZES.md`)

### 🛠️ Scripts de Automação
- Criado `scripts/changelog_update.py`: script CLI para adicionar entradas padronizadas ao CHANGELOG sem edição manual. (`scripts/`)
- Criado `scripts/pre_deploy_check.py`: script de validação automática que verifica VERSION, CHANGELOG, .env.example, ausência de credenciais hardcoded e existência de documentos obrigatórios antes de qualquer deploy. (`scripts/`)

---

## [1.1.0] — 2026-09-21

### 🚀 Suporte a Múltiplos Formatos do Instagram (Carrossel, Reels, Stories, Feed)
- **Suporte Oficial a Carrosséis (Slides 1:1):** Geração de 4 a 7 slides didáticos sequenciais com contadores visuais, títulos destacados e diagramação limpa via FFmpeg.
- **Envio em Formato de Álbum no Telegram (`sendMediaGroup`):** O operador humano recebe os slides agrupados como um carrossel real no Telegram para análise prévia acompanhado do card de decisão.
- **Containers de Carrossel na Meta Graph API:** Implementação do fluxo de criação de itens de carrossel individuais (`is_carousel_item="true"`) e agrupamento no container pai `media_type="CAROUSEL"`.
- **Formato Stories (9:16):** Geração de mídias verticais com ganchos rápidos, sugestão de enquetes interativas e call to action.
- **Formato Feed Post (1:1):** Criação de posts tradicionais de imagem única de autoridade e legenda completa.
- **Menu Dinâmico de Formatos no Bot do Telegram:** Ao executar `/novo` e selecionar a marca, o usuário escolhe intuitivamente entre `[🎬 Reel]`, `[📱 Story]`, `[🖼️ Feed]` e `[📚 Carrossel]`.
- **Detecção de Fontes no Dockerfile:** Inclusão do pacote `fonts-dejavu-core` no container para renderização tipográfica TrueType de alta nitidez.

---

## [1.0.0] — 2026-09-21

### 🚀 Novas Funcionalidades
- Esteira Multimodal de Menor Custo Operacional (gemini-3.1-flash-lite + gemini-3.1-flash-lite-image 1K + veo-3.1-lite Image-to-Video 720p 4s) com cálculo automático de custos e fallback FFmpeg cinemático (`app/ai`)
- Comando /radar e botão no menu principal com geração de publicação direta a partir das oportunidades selecionadas pelo Radar (`app/bot`)
- Content Radar: Motor proativo de inteligência com arquitetura de adaptadores desacoplados (Google Trends, ATP, ITF, News) e foco estratégico na conversão para o projeto de Máquina Lançadora de Bolas DIY Koala Tênis (`app/research`)
- **Painel Web de Configurações (`http://<IP>:8085`):** Interface Dark Studio com abas para Instagram & Meta, Google Gemini, Telegram Bot, Perfis de Automação, Diagnóstico e Tutorial Passo a Passo.
- **Suporte Multi-Contas:** Capacidade de cadastrar e gerenciar múltiplas marcas do Instagram no mesmo servidor, cada uma com seu próprio ID, token e tom de voz.
- **Botão de Teste Individual por Perfil:** Validação de conectividade direta de cada perfil com a Meta Graph API.
- **Telegram Bot Completo:** Polling assíncrono com validação estrita de usuário autorizado, comandos `/start`, `/novo`, `/status`, `/fila`, `/perfis` e botões interativos inline.
- **Motor de Roteiros com Google Gemini:** Geração estruturada em JSON (Pydantic) com ganchos de retenção, cenas, narração, legendas e hashtags.
- **Renderizador FFmpeg 9:16:** Geração automatizada de mídias verticais (1080x1920) e thumbnails em conformidade com as diretrizes de Reels da Meta.
- **Orquestrador de Conteúdo e Aprovação Humana:** Fluxo semi-automático onde nenhum conteúdo é publicado sem aprovação explícita no Telegram (`✅ PUBLICAR NO INSTAGRAM`).
- **DevOps & CI/CD AppSpace 2:** Workflows do GitHub Actions para CI, Snapshot (DSV), Release Candidate (DSV/HMG), Produção (PRD) e Redeploy.

### 🛡️ Segurança e Infraestrutura
- Auditoria do servidor `homelabaws` (`10.0.0.119`) concluída com sucesso, com mapeamento para a porta `8085` para evitar conflito com o Nextcloud na `8080`.
- Mascaramento de tokens e senhas na API.
- Execução em container com usuário não-root `appuser`.
