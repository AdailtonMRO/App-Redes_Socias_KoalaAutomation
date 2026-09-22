# 🐨 Koala Social Media Automation (Instagram AI V1)

> Sistema de automação inteligente para redes sociais com **foco no Instagram**, geração de Reels com IA (Google Gemini + Veo), composição FFmpeg, controle e aprovação humana via Telegram e **Painel Web de Configuração**.

---

## 🚀 Funcionalidades Principais

1. **Painel Web de Configurações e Onboarding (`http://localhost:8080`)**:
   - Interface moderna e responsiva (Dark Studio).
   - Configuração declarativa da conta do Instagram / Meta Graph API com **botão de teste de conexão em tempo real**.
   - Gerenciamento de chaves da Google AI (Gemini & Veo) e do Telegram Bot.
   - Cadastro e edição de múltiplos **Perfis de Automação** (nichos, público, tom de voz, CTAs).
   - Diagnóstico ao vivo de saúde do sistema e banco de dados.

2. **Geração de Conteúdo com IA**:
   - Roteiros estratégicos gerados em JSON estruturado com **Google Gemini**.
   - Vídeos verticais 9:16 gerados via **Google Veo**.
   - Concatenação, ajuste de resolução e áudio via **FFmpeg**.

3. **Governança e Aprovação Humana (Telegram Bot)**:
   - Nenhum conteúdo é publicado sem autorização prévia.
   - Opções interativas: `✅ PUBLICAR`, `🔄 REFAZER`, `✏️ ALTERAR` e `❌ DESCARTAR`.

4. **DevOps & CI/CD Corporativo (Padrão AppSpace 2)**:
   - Versionamento semântico dinâmico (`VERSION`).
   - Workflows automatizados de CI, Snapshot (DSV), Release Candidate (DSV/HMG), Produção (PRD) e Redeploy.

---

## 🛠️ Como Executar o Projeto

### Opção 1: Via Docker Compose (Recomendado)

1. Certifique-se de que o Docker e o Docker Compose estão instalados.
2. Na raiz do projeto, execute:
   ```bash
   docker compose up -d --build
   ```
3. Acesse o painel web no navegador:
   👉 **`http://localhost:8080`**

---

### Opção 2: Execução Local com Python

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor FastAPI:
   ```bash
   python -m app.main
   ```
4. Acesse no navegador:
   👉 **`http://localhost:8080`**

---

## 📁 Estrutura do Repositório

```text
├── .github/
│   ├── configs/
│   │   ├── deploy-config.yml       # Mapeamento de portas e recursos DSV/HMG/PRD
│   │   └── pipeline-config.yml     # Metadados de build e registry local
│   └── workflows/
│       ├── ci.yml                  # Validação e testes em PRs para main
│       ├── snapshot.yml            # Build e deploy automático em DSV
│       ├── start-release.yml       # Deploy simultâneo de Release Candidate (DSV/HMG)
│       ├── finish-release.yml      # Deploy em Produção (PRD) com tag Git
│       └── redeploy.yml            # Rollback e redeploy manual sob demanda
│
├── app/
│   ├── main.py                     # Ponto de entrada FastAPI e montagem estática
│   ├── config.py                   # Pydantic Settings e leitura de .env
│   ├── api/routers/                # Endpoints REST (config, profiles, instagram, health)
│   ├── database/                   # Modelos ORM SQLite e Repositórios
│   ├── profiles/                   # Gerenciador de perfis JSON
│   ├── instagram/                  # Cliente Meta Graph API e validador de conexão
│   └── static/                     # Interface Web (HTML, CSS Dark Studio, JavaScript)
│
├── docs/                           # Documentação viva e diretrizes do projeto
│   ├── 00_INDEX.md                 # Mapa de navegação de toda a documentação
│   ├── 00_REGRAS_E_DIRETRIZES.md   # Livro oficial de regras e governança
│   ├── 02-Acesso-e-Docker.md       # Arquitetura de permissões, Docker e Tailscale
│   ├── 11_INSTAGRAM.md             # Guia passo a passo de conexão com a Meta API
│   ├── Configuracao da estrutura.md# Especificação original AppSpace 2
│   └── PROMPT_INSTAGRAM_AI_V1.md   # Especificação original do Instagram AI
│
├── profiles/                       # Perfis de nicho declarativos
│   └── koalatenis.json             # Perfil padrão de demonstração
│
├── tests/                          # Bateria de testes unitários e de integração
├── Dockerfile                      # Imagem oficial Python 3.12 + FFmpeg + appuser
├── docker-compose.yml              # Orquestração local de containers
├── .env.example                    # Modelo de credenciais
└── VERSION                         # Versão semântica oficial
```

---

## 📚 Documentação Adicional
- [Livro de Regras e Diretrizes](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/00_REGRAS_E_DIRETRIZES.md)
- [Guia de Conexão com o Instagram](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/11_INSTAGRAM.md)
- [Índice Geral de Documentos](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/00_INDEX.md)
