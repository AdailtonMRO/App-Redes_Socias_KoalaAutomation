# 20. Arquitetura Alvo: Koala Automation

Este documento atua como a "constituição técnica" do projeto, definindo o estado atual, a visão de futuro e as regras arquiteturais para a evolução do Koala Automation.

## 1. Novo Objetivo do Produto

**Visão Completa:**
Construir um agente de inteligência editorial e produção de conteúdo para redes sociais, capaz de pesquisar continuamente o ambiente externo, identificar oportunidades relevantes para cada perfil, transformar essas oportunidades em conteúdos originais, submetê-los à aprovação humana, publicar nas redes sociais e aprender com os resultados para melhorar continuamente as próximas decisões.

**Visão Curta:**
Descobrir o que merece virar conteúdo, criar com IA, publicar com aprovação humana e aprender com os resultados.

---

## 2. Arquitetura Atual

A versão atual do projeto (V1) possui os componentes fundamentais, mas eles operam de forma parcialmente desconectada:

*   **Infraestrutura:** FastAPI, Docker, SQLite (🟢 Adequado)
*   **Geração:** Gemini, Veo, FFmpeg (🟢 Implementado)
*   **Governança:** Telegram (🟢 Implementado)
*   **Distribuição:** Instagram/Meta (🟢 Implementado)
*   **Inteligência/Radar:** Content Radar com 7 adapters (Google Trends, Notícias, ATP, WTA, etc.) (🟢 Implementado, mas funciona mais como agregador de notícias).
*   **Lacunas Críticas — STATUS V2.0.0:**
    *   ✅ Radar agora conhece profundamente o DNA de cada perfil (Etapa 1).
    *   ✅ Memória do Radar persistida em SQLite via `RadarRepository` (Etapa 2).
    *   ✅ Métricas pós-publicação coletadas via Graph API e armazenadas (Etapa 4).
    *   ✅ Ciclo de aprendizado (Learning Loop) ativo — métricas alimentam o Radar (Etapa 5).

---

## 3. Arquitetura Alvo

O fluxo ideal desenhado para a arquitetura alvo transforma o sistema de um simples automatizador para um **agente editorial autônomo**:

```text
┌──────────────┐
│   INTERNET   │
└──────┬───────┘
       │
┌─────────▼─────────┐
│   CONTENT RADAR   │
│                   │
│   notícias        │
│   tendências      │
│   eventos         │
│   comunidades     │
│   tecnologia      │
└─────────┬─────────┘
          │
          ▼
┌─────────────────┐
│ RESEARCH MEMORY │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ GEMINI — EDITOR  │
│                  │
│   contexto       │
│   DNA do perfil  │
│   histórico      │
│   estratégia     │
└────────┬─────────┘
         │
         ▼
CONTENT OPPORTUNITY
         │
         ▼
┌───────────┐
│ TELEGRAM  │
│ HUMAN     │
└─────┬─────┘
   APROVAR
      │
      ▼
CONTENT GENERATOR
      │
┌────────────┼────────────┐
▼            ▼            ▼
Gemini       Veo        FFmpeg
│            │            │
└────────────┼────────────┘
             ▼
          PREVIEW
             │
             ▼
         TELEGRAM
          APROVAR
             │
             ▼
         INSTAGRAM
             │
             ▼
         MÉTRICAS
             │
             ▼
      PERFORMANCE DB
             │
             ▼
          GEMINI
             │
             └──────────► RADAR
```

---

## 4. Responsabilidade de Cada Módulo

### 4.1 Content Radar
Deve separar a coleta de fatos da decisão editorial.
`SOURCE` ↓ `FACT / SIGNAL` ↓ `RESEARCH ITEM` ↓ `EDITORIAL ANALYSIS` ↓ `CONTENT OPPORTUNITY`
O Radar coleta o que aconteceu ou o que está em alta, mas não decide sozinho se é um bom conteúdo.

### 4.2 DNA do Perfil
A fundação de toda decisão do agente. Deve ser expandido para conter:
*   **Identidade:** Quem somos, público, posicionamento, autoridade.
*   **Conteúdo:** Pilares, subtemas, assuntos prioritários/proibidos, formatos.
*   **Negócio:** Produtos, serviços, objetivos, CTAs.
*   **Estilo:** Tom, vocabulário, ritmo, estética.
*   **Estratégia:** Frequência, proporção, estágio do funil.

### 4.3 Memória Editorial (Research Memory)
Persistência do Radar em banco de dados (`research_items`, `research_sources`, `content_opportunities`, `radar_runs`). O agente precisa saber o que já foi analisado no passado para não repetir conteúdo.

### 4.4 Gemini como Cérebro
O Gemini deixa de ser apenas um "gerador de texto" e assume três papéis sob um mesmo contexto:
1.  **Estrategista:** Define pilares, frequência, aprendizado.
2.  **Editor:** Avalia oportunidades, define ângulo e formato.
3.  **Criador:** Gera roteiro, legenda e cenas.

### 4.5 Telegram como Governança Humana
Interface de decisão. O Telegram não deve ser um painel administrativo complexo, mas sim o ponto onde o humano aprova, rejeita ou ajusta o que o agente propõe (Radar, Fila, Histórico, Status).

### 4.6 Pipeline de Produção
Orquestração de ferramentas (Gemini, Veo, FFmpeg) baseada no `Content Opportunity` gerado e aprovado.

### 4.7 Instagram/Meta
Módulo final da distribuição. Recebe os artefatos gerados e realiza a publicação.

### 4.8 Métricas
Coleta de resultados reais pós-publicação (alcance, visualizações, likes, comentários, salvamentos, compartilhamentos, retenção).

### 4.9 Learning Loop (Aprendizado)
O motor de evolução contínua. Cruza as métricas com o conteúdo gerado para extrair padrões (ex: "Vídeos sobre biomecânica geram mais salvamentos") e retroalimentar a estratégia do Radar.

---

## 5. Modelo de Dados Futuro (Evolução)

Para suportar a arquitetura alvo, o modelo de dados precisará evoluir:

1.  **Radar DB:**
    *   `research_items`: Os fatos brutos e sinais coletados.
    *   `research_sources`: Fontes de onde os dados vieram.
    *   `content_opportunities`: As análises editoriais do Gemini sobre os research items.
    *   `radar_runs`: Histórico de execuções do Radar.
2.  **Métricas DB:**
    *   `content_metrics`: Dados de performance vinculados ao `content_id` e `instagram_media_id`.

---

## 6. Roadmap V1 → V2

A evolução será disciplinada e dividida em 5 etapas progressivas:

*   **ETAPA 1 — Consolidar o Cérebro Editorial:** ✅ **Concluída**
    Estrutura rica de `Profile DNA` criada e conectada ao Gemini via `build_prompt_by_format`.
*   **ETAPA 2 — Persistir o Radar:** ✅ **Concluída**
    Memória do Radar movida para SQLite (tabelas `radar_runs`, `research_items`, `content_opportunities`).
*   **ETAPA 3 — Transformar Oportunidade em Conteúdo:** ✅ **Concluída**
    Schema enriquecido com `audio_script` e `main_visual_prompt`; Veo consome prompt visual consolidado.
*   **ETAPA 4 — Métricas:** ✅ **Concluída**
    Coleta de resultados reais via Graph API implementada e persistida no SQLite.
*   **ETAPA 5 — Learning Loop:** ✅ **Concluída**
    Métricas retroalimentam o Gemini curador nas próximas rodadas do Radar.

---

## 7. O Que NÃO Desenvolver Agora

Para manter o foco no ciclo editorial, as seguintes tecnologias e complexidades estão **vetadas** neste momento:

❌ PostgreSQL ou outros SGBDs complexos (SQLite é suficiente).
❌ Redis ou sistemas de cache distribuído.
❌ Kubernetes ou orquestração complexa de containers.
❌ Múltiplos agentes de IA independentes (Multi-Agent framework).
❌ Fine-tuning de modelos LLM.
❌ Dashboard complexo de BI/Analytics customizado.
❌ Publicação 100% autônoma (sem aprovação humana).
❌ Scraping indiscriminado (além das APIs e RSS já configurados).

---

## 8. Critérios de Aceite para a Arquitetura Alvo

1.  O Radar deve coletar informações independentemente do perfil, e o cruzamento deve ocorrer na fase de Oportunidade.
2.  Toda oportunidade editorial gerada pelo Gemini deve considerar explicitamente o "DNA do Perfil".
3.  Nenhuma sugestão do Radar pode ser perdida por reinício do container (persistência de memória).
4.  O humano (via Telegram) sempre tem a palavra final antes da geração final e antes da publicação.
5.  O sistema deve ser capaz de mostrar por que uma decisão editorial foi tomada.
