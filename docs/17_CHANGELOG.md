# 📜 Registro Histórico de Mudanças (Changelog)

Todas as alterações notáveis deste projeto são registradas neste arquivo.

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
