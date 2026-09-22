# 🐨 Koala Automation — Agente Editorial de Redes Sociais com IA

> **v2.0.0** — Sistema completo de **inteligência editorial autônoma** para Instagram, com pesquisa proativa de notícias, geração multimodal de conteúdo (Google Gemini + Veo + FFmpeg), aprovação humana via Telegram, coleta de métricas e **Learning Loop** de aprendizado contínuo.

---

## 🚀 Funcionalidades Principais

### 📡 Content Radar — Inteligência de Pauta
- Varredura paralela em **7+ fontes especializadas** (TenisBrasil, Tenis News, ge.globo, ESPN, WTA, CBT, ATP, ITF, Google Trends).
- Curadoria e scoring com **Google Gemini** baseado no DNA do perfil.
- Anti-repetição dinâmica: histórico persistido no SQLite, sem repetições entre rodadas.
- Oportunidades entregues no Telegram com botões de ação direta.

### 🧠 Cérebro Editorial (Profile DNA)
- Cada perfil possui um DNA completo: `Identity`, `Content`, `Business`, `Style` e `Strategy`.
- Prompts dinâmicos do Gemini gerados com base na personalidade do perfil ativo.

### 🎬 Geração de Conteúdo Multimodal
- Roteiros em JSON estruturado com `audio_script` e `main_visual_prompt` separados.
- Vídeos verticais 9:16 via **Google Veo** (com polling de operações longas e download automático).
- Fallback cinematográfico via **FFmpeg** com tipografia cinética e gradiente dinâmico.
- Formatos suportados: **Reels, Stories, Feed Posts e Carrosséis**.

### 📊 Métricas pós-publicação
- Coleta automática via **Meta Graph API** (`/insights`): plays, likes, comentários, compartilhamentos, salvamentos, alcance e taxa de engajamento calculada.
- Dados persistidos no SQLite e consultáveis via comando `/metrics` no Telegram.

### 🔄 Learning Loop
- As métricas dos últimos posts são injetadas no prompt de curadoria do Radar a cada ciclo.
- O Gemini aprende quais temas e formatos geram mais engajamento e ajusta automaticamente a seleção de oportunidades.

### 🤖 Governança Humana (Telegram Bot)
- Nenhum conteúdo é publicado sem aprovação explícita via Telegram.
- Comandos: `/novo`, `/radar`, `/fila`, `/status`, `/perfis`, `/metrics`.
- Cards interativos com prévia do vídeo/imagem e opções: `✅ PUBLICAR`, `🔄 REFAZER`, `✏️ ALTERAR`, `❌ DESCARTAR`.

### 🖥️ Painel Web de Configuração
- Interface Dark Studio em `http://localhost:8080`.
- Configuração de Instagram (Meta Graph API), Google Gemini, Telegram e perfis de automação.
- Diagnóstico ao vivo e teste de conectividade por conta.

### ⚙️ DevOps & CI/CD (Padrão AppSpace 2)
- Versionamento semântico (`VERSION`).
- Workflows do GitHub Actions: CI, Snapshot (DSV), Release Candidate (HMG) e Produção (PRD).
- Rollback automático via `redeploy.yml`.

---

## 🛠️ Como Executar

### Via Docker Compose (Recomendado)

```bash
docker compose up -d --build
```
Painel web: 👉 **`http://localhost:8080`**

### Execução Local com Python

```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m app.main
```

---

## 📁 Estrutura Principal

```text
app/
├── ai/           # Gemini (roteiros JSON), Veo (vídeo), prompts e schemas Pydantic
├── bot/          # Telegram Bot — polling, handlers e teclados inline
├── database/     # ORM SQLite, modelos, repositórios (conteúdo, radar, métricas)
├── instagram/    # Meta Graph API client (publicação + insights)
├── profiles/     # Profile DNA e gerenciador de perfis JSON
├── research/     # Content Radar, adapters de fontes e scoring Gemini
├── services/     # Orquestrador de conteúdo (ContentOrchestrator)
└── static/       # Interface Web (Dark Studio)

docs/
├── 17_CHANGELOG.md                     # Registro histórico de versões
├── 18_CONTENT_RADAR.md                 # Documentação do Radar de Conteúdo
├── 19_DEPLOY_HOMELAB.md                # Guia de deploy no servidor HomeLab
└── 20_ARQUITETURA_ALVO_KOALA_AUTOMATION.md  # Arquitetura V2 e Roadmap
```

---

## 📚 Documentação
- [Índice Geral](docs/00_INDEX.md) | [Regras e Diretrizes](docs/00_REGRAS_E_DIRETRIZES.md)
- [Guia Instagram](docs/11_INSTAGRAM.md) | [Deploy HomeLab](docs/19_DEPLOY_HOMELAB.md)
- [Arquitetura V2](docs/20_ARQUITETURA_ALVO_KOALA_AUTOMATION.md) | [Changelog](docs/17_CHANGELOG.md)

