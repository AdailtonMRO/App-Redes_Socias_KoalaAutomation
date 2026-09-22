# 📚 Índice da Documentação — Instagram AI V1 (Koala Automation)

Bem-vindo à documentação oficial do projeto **Instagram AI V1** (Automação de Redes Sociais com IA).  
Este índice organiza todas as especificações técnicas, regras de desenvolvimento, infraestrutura e manuais operacionais.

---

## 🗂️ Mapa da Documentação

### 📌 Diretrizes e Governança
- **[00_REGRAS_E_DIRETRIZES.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/00_REGRAS_E_DIRETRIZES.md)**: Manual mestre de regras de engenharia, governança, segurança, aprovação humana e padrões de código.
- **[PASSO_A_PASSO_CONFIGURACOES.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/PASSO_A_PASSO_CONFIGURACOES.md)**: **Guia prático e ilustrado de configuração passo a passo (Instagram, Gemini e Telegram)**.
- **[Configuracao da estrutura.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/Configuracao%20da%20estrutura.md)**: Especificação da esteira de CI/CD e deployment AppSpace 2 / d9i3-templates.
- **[PROMPT_INSTAGRAM_AI_V1.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/PROMPT_INSTAGRAM_AI_V1.md)**: Especificação original completa dos requisitos funcionais do projeto.

### 🤖 Governança de Agentes de IA
- **[.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md)**: **Regras obrigatórias para todos os agentes de IA** — protocolo de documentação, versionamento, segurança e deploy.
- **[19_DEPLOY_HOMELAB.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/19_DEPLOY_HOMELAB.md)**: **Guia completo de deploy no HomeLab** (automático via CI/CD e manual como fallback) com troubleshooting e rollback.

### 🗃️ Arquivo de Decisões Arquiteturais (ADR)
- **[archive/TEMPLATE_ADR.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/archive/TEMPLATE_ADR.md)**: Template padronizado para novos registros de decisão arquitetural.
- **[archive/2026-09-22_ADR-001_Governanca_Agentes_IA.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/archive/2026-09-22_ADR-001_Governanca_Agentes_IA.md)**: ADR-001 — Adoção do sistema de governança de documentação e deploy para agentes de IA.

---

### 📘 Módulos Técnicos e Manuais
- **[01_REQUIREMENTS.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/01_REQUIREMENTS.md)**: Requisitos funcionais, não funcionais e critérios de aceite da V1.
- **[02_SERVER_AUDIT.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/02_SERVER_AUDIT.md)**: Checklist e diagnóstico de auditoria do servidor antes da implantação.
- **[02-Acesso-e-Docker.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/02-Acesso-e-Docker.md)**: Guia de acesso ao servidor e operações Docker no HomeLab.
- **[03_ARCHITECTURE.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/03_ARCHITECTURE.md)**: Desenho da arquitetura modular, fluxos e diagramas Mermaid.
- **[04_INSTALLATION.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/04_INSTALLATION.md)**: Procedimento completo de instalação e execução do sistema.
- **[05_DOCKER.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/05_DOCKER.md)**: Especificação do container, Compose, volumes e mapeamentos de portas.
- **[06_CONFIGURATION.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/06_CONFIGURATION.md)**: Dicionário completo de variáveis de ambiente (`.env`) e configurações.
- **[07_TELEGRAM.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/07_TELEGRAM.md)**: Manual do Telegram Bot, fluxo de comandos e cards de aprovação humana.
- **[08_GEMINI.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/08_GEMINI.md)**: Integração com Google Gemini (prompts, schemas JSON estruturados e validações).
- **[09_VIDEO_GENERATION.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/09_VIDEO_GENERATION.md)**: Integração com modelo de vídeo Veo (operações assíncronas, polling e downloads).
- **[10_FFMPEG.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/10_FFMPEG.md)**: Composição de vídeo vertical 9:16, normalização de áudio e extração de thumbnails.
- **[11_INSTAGRAM.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/11_INSTAGRAM.md)**: **Guia completo de configuração e conexão de conta do Instagram (Meta Graph API)**.
- **[12_DATABASE.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/12_DATABASE.md)**: Esquema do banco de dados SQLite, entidades e repositórios.
- **[13_SECURITY.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/13_SECURITY.md)**: Política de segurança, proteção de credenciais e sanitização de logs.
- **[14_TESTS.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/14_TESTS.md)**: Estratégia de testes unitários, testes de integração e mocks.
- **[15_TROUBLESHOOTING.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/15_TROUBLESHOOTING.md)**: Resolução de incidentes comuns, códigos de erro da Meta e timeouts.
- **[16_OPERATIONS.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/16_OPERATIONS.md)**: Guia de operação diária, rotinas de backup e monitoramento.
- **[17_CHANGELOG.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/17_CHANGELOG.md)**: Registro histórico de versões e modificações.
- **[18_CONTENT_RADAR.md](file:///c:/Users/Adail/Documents/App%20Redes_Socias_KoalaAutomation/docs/18_CONTENT_RADAR.md)**: **Content Radar: Motor Proativo de Inteligência de Conteúdo, Adapters e Foco DIY Máquina de Bolas**.

---

## 🎯 Status de Conformidade
| Item | Status | Observações |
| :--- | :---: | :--- |
| **Livro de Regras e Diretrizes** | ✅ Concluído | Ver `docs/00_REGRAS_E_DIRETRIZES.md` |
| **Regras para Agentes de IA** | ✅ Concluído | Ver `.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md` |
| **Guia de Deploy HomeLab** | ✅ Concluído | Ver `docs/19_DEPLOY_HOMELAB.md` |
| **Scripts de Automação** | ✅ Concluído | Ver `scripts/changelog_update.py` e `scripts/pre_deploy_check.py` |
| **Padrão de CI/CD Corporativo** | ✅ Especificado | Ver `docs/Configuracao da estrutura.md` |
| **Manual de Conexão do Instagram** | 🔄 Em elaboração | Ver `docs/11_INSTAGRAM.md` |
| **Código-Fonte da Aplicação** | ⏳ Aguardando Fase 1 | Estrutura Python / Docker a iniciar |

---

## 🛠️ Scripts de Automação

| Script | Uso | Comando de exemplo |
| :--- | :--- | :--- |
| `scripts/changelog_update.py` | Adiciona entrada padronizada ao CHANGELOG | `python scripts/changelog_update.py --version 1.2.0 --type feat --module app/research --description "Novo adapter"` |
| `scripts/pre_deploy_check.py` | Valida checklist antes de qualquer deploy | `python scripts/pre_deploy_check.py --env prd --strict` |
| `scripts/run_multimodal_pipeline.py` | Executa esteira multimodal de menor custo (Prompt -> Imagem 1K -> Vídeo 720p 4s) e calcula custos | `python scripts/run_multimodal_pipeline.py --topic "Treino de saque" --duration 4` |
