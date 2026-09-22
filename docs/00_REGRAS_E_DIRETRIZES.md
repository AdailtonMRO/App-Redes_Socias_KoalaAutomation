# 📜 Livro de Regras e Diretrizes de Engenharia — Projeto Social Media Automation (Instagram AI V1)

> **Status:** Documento Oficial de Governança  
> **Versão:** 1.0.0  
> **Data:** 2026-09-21  
> **Aplica-se a:** Todos os módulos, integrações, pipelines e documentações do ecossistema Koala Automation / Instagram AI.

---

## 1. Visão Geral e Princípios Fundamentais

O projeto **Social Media Automation** (com foco inicial na plataforma **Instagram AI V1**) tem como objetivo automatizar o ciclo completo de planejamento, roteirização com IA (Google Gemini), geração de mídia (Google Veo), renderização/composição (FFmpeg) e publicação oficial (Meta Graph API), com controle e governança via **Telegram Bot**.

### Princípios Inegociáveis (Core Tenets):
1. **Semi-Automação & Aprovação Humana Obrigatória:** Na V1, **nenhum conteúdo é publicado sem aprovação explícita** do operador via Telegram (`✅ PUBLICAR`). Não existe publicação autônoma silenciosa.
2. **Document-Driven Development (DDD):** O código deve refletir a documentação e vice-versa. Se não está documentado ou testado, não é considerado entregue.
3. **Segurança de Credenciais & Isolamento:** Credenciais de redes sociais e chaves de IA jamais trafegam em repositórios Git, logs ou respostas de erro. Toda execução ocorre em container Docker isolado.
4. **Resiliência a Falhas & Conexão Configurável:** As contas das redes sociais pertencem ao usuário e devem ser configuráveis dinamicamente (via arquivo de perfil JSON e variáveis de ambiente declarativas), com validação prévia de conexão e escopos de acesso.
5. **Governança DevOps Corporativa:** Adoção estrita do padrão de esteira CI/CD **AppSpace 2 / d9i3-templates** com versionamento semântico, imagens snapshot/release candidate/latest e deploy com healthcheck contínuo.

---

## 2. Regras de Conexão e Configuração de Redes Sociais pelo Usuário (Instagram)

### 2.1 Modelo de Conexão do Usuário
- O sistema é **multi-perfil**: o usuário pode ter mais de uma marca/perfil configurada.
- Cada perfil deve residir em um arquivo declarativo no diretório `profiles/<nome_do_perfil>.json`.
- A aplicação não deve conter dados de usuários ou contas hardcoded em código-fonte.

### 2.2 Estrutura do Perfil (`profiles/<perfil>.json`)
Todo perfil de rede social deve seguir a estrutura:
```json
{
  "id": "koalatenis",
  "name": "Koala Tênis",
  "platform": "instagram",
  "username": "@koalatenis_",
  "instagram_account_id_env": "INSTAGRAM_ACCOUNT_ID_KOALATENIS",
  "niche": ["tênis", "tecnologia", "DIY", "engenharia"],
  "audience": ["tenistas amadores", "professores de tênis", "makers"],
  "tone": ["moderno", "técnico", "didático", "descontraído"],
  "objectives": ["engajamento", "autoridade", "venda"],
  "video_format": "9:16",
  "preferred_duration": "20-30s",
  "cta": "Conheça o curso Koala Tênis",
  "avoid": ["informações inventadas", "promessas exageradas"]
}
```

### 2.3 Regras para a API Oficial da Meta (Instagram Graph API)
1. **Tipo de Conta Exigida:** Instagram Professional Account (Creator ou Business), vinculada a uma Página do Facebook correspondente.
2. **Permissões Mínimas de Token:**
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
3. **Credenciais Necessárias no `.env`:**
   - `INSTAGRAM_APP_ID`: ID do aplicativo Meta for Developers.
   - `INSTAGRAM_APP_SECRET`: Chave secreta do aplicativo Meta.
   - `INSTAGRAM_ACCESS_TOKEN`: Token de longa duração (Page / User Long-Lived Token com validade estendida de 60 dias ou System User Token).
   - `INSTAGRAM_ACCOUNT_ID`: Instagram Business Account ID (ID numérico do perfil profissional).
4. **Fluxo de Publicação de Reels da Meta:**
   - **Etapa 1:** O vídeo renderizado deve estar disponível em uma URL pública acessível via HTTPS ou transmitido via upload resumível (Resumable Upload API da Meta).
   - **Etapa 2 (Criação do Container):** Envio de requisição POST para `/{instagram_account_id}/media` com `media_type=REELS`, `video_url` e `caption`.
   - **Etapa 3 (Polling de Status):** Monitoramento do container através de GET `/{container_id}?fields=status_code` até o status ser `FINISHED` (com backoff e timeout de segurança).
   - **Etapa 4 (Publicação Efetiva):** POST para `/{instagram_account_id}/media_publish` com `creation_id={container_id}`.
   - **Etapa 5 (Persistência):** Armazenamento do `instagram_media_id` retornado na tabela `contents`.
5. **Validação Prévia de Conexão:**
   - O sistema deve dispor de um comando/função de teste de conexão (`validate_instagram_credentials()`) que verifica se o token é válido, se não está expirado e se a conta do Instagram está acessível antes de permitir a submissão de vídeos à fila.

---

## 3. Regras de Inteligência Artificial e Conteúdo (Gemini & Veo)

### 3.1 Geração de Texto e Roteiro (Gemini)
- Toda saída da IA deve ser **estritamente tipada em JSON estruturado**, utilizando schema definido (Pydantic).
- O prompt do Gemini deve receber obrigatoriamente: dados do perfil, objetivo da postagem, tema fornecido pelo usuário e regras de restrição do perfil ("avoid").
- **Proibição de Alucinação Comercial:** A IA nunca deve inventar preços, especificações técnicas ou ofertas comerciais que não constem na configuração do perfil. Se faltar informação, ela deve abster-se ou solicitar esclarecimento.
- **Auto-Correção de JSON:** Em caso de resposta inválida do modelo, o orquestrador deve registrar o erro, tentar auto-correção imediata e, se persistir, interromper o fluxo sem seguir para a geração de vídeo.

### 3.2 Geração de Vídeo (Veo / Google GenAI)
- **Chamadas Assíncronas Obrigatórias:** A chamada para geração de vídeo deve salvar o `operation_id` retornado e efetuar polling com intervalo mínimo seguro (ex: 5 a 10 segundos com exponencial backoff e timeout limite de 5 minutos).
- **Formato Vertical:** Resolução padronizada para 9:16 (1080x1920 ou proporcional suportado pela API), codec H.264 / AAC.
- **Gestão de Custos e Mocks:**
  - Em ambientes de teste e desenvolvimento automatizado (`ci.yml` ou testes locais), utilizar **mocks e geradores sintéticos**.
  - Somente acionar geração real no Veo mediante comando explícito do operador, prevenindo consumo acidental de créditos da API.

---

## 4. Regras de Processamento de Vídeo e Multimídia (FFmpeg)

1. **Abstração Centralizada:** É proibido espalhar invocações de `subprocess.Popen("ffmpeg ...")` pela base de código. Todas as chamadas ao FFmpeg devem ser encapsuladas em uma classe especializada `FFmpegProcessor` no módulo `app/video/`.
2. **Funções Obrigatórias do Processador:**
   - Concatenação de cenas geradas em arquivo único (`concat_demuxer`).
   - Ajuste de proporção para 9:16 com padding/letterbox se necessário.
   - Normalização de áudio (EBU R128 ou volume padrão) e mixagem de trilha/narração.
   - Extração automática de frame para Thumbnail/Capa (`thumbnail.jpg`).
3. **Limpeza de Arquivos Temporários:**
   - Arquivos intermediários de cenas devem ser gerados em `data/temp/<content_id>/` e purgados após a criação do vídeo final consolidado em `data/videos/`.

---

## 5. Regras de Interface e Controle via Telegram Bot

1. **Autorização Rígida de Usuário:**
   - O bot só aceita e responde a comandos vindos de IDs de usuário configurados em `TELEGRAM_ALLOWED_USER_ID`. Requisições de terceiros devem ser sumariamente descartadas e logadas como alerta de segurança.
2. **Comandos Mínimos Obrigatórios:**
   - `/start` — Boas-vindas, status do sistema e menu de atalhos.
   - `/novo` — Inicia o assistente guiado de criação de novo Reel.
   - `/status` — Visão geral de saúde dos serviços (Gemini, Instagram, Banco, Disco).
   - `/fila` — Lista conteúdos aguardando aprovação ou em processamento.
   - `/historico` — Exibe os últimos conteúdos produzidos e publicados.
   - `/perfis` — Lista os perfis de redes sociais ativos no sistema.
3. **Protocolo de Aprovação Humana do Reel:**
   - Ao concluir a renderização, o bot envia o arquivo de vídeo MP4 e um card com as opções:
     - `✅ PUBLICAR`: Transiciona o estado para `APPROVED` -> `PUBLISHING` -> `PUBLISHED`.
     - `🔄 REFAZER`: Solicita feedback em texto natural e gera nova versão (`version = n+1`) mantendo histórico.
     - `✏️ ALTERAR`: Permite ajuste fino de legenda, hashtags ou CTA sem regenerar o vídeo.
     - `❌ DESCARTAR`: Transiciona para `REJECTED` e remove mídias da fila ativa.

---

## 6. Regras de Persistência e Banco de Dados (SQLite & Repository Pattern)

1. **SQLite na V1:** Utilizado na V1 pela portabilidade e simplicidade, encapsulado com SQLAlchemy ou camada Repository pura.
2. **Isolamento de Persistência:** A lógica de negócio nunca deve executar SQL direto; deve sempre interagir via `ProfileRepository`, `ContentRepository`, `GenerationRepository` e `ActionRepository`.
3. **Máquina de Estados Inviolável:**
   ```text
   DRAFT ──► GENERATING_SCRIPT ──► GENERATING_VIDEO ──► PROCESSING_VIDEO ──► WAITING_APPROVAL
                                                                                  │
                ┌───────────────────────────┬─────────────────────────────────────┤
                ▼                           ▼                                     ▼
           REGENERATING                 REJECTED                               APPROVED
                │                                                                 │
                └────────► (Volta ao ciclo)                                       ▼
                                                                              PUBLISHING
                                                                                  │
                                                                                  ▼
                                                                              PUBLISHED
                                                                                  │
                                                                                  ▼
                                                                           (Estado Final)
   ```
   *Nota: O estado `PUBLISHED` jamais pode retornar para estados anteriores sem intervenção manual de auditoria.*

---

## 7. Regras de DevOps, CI/CD e Arquitetura Docker (Padrão AppSpace 2)

Seguindo a especificação corporativa do documento `Configuracao da estrutura.md`:

### 7.1 Arquivos Obrigatórios na Raiz
- `VERSION`: Arquivo com a versão semântica inicial (ex: `1.0.0`).
- `.github/configs/pipeline-config.yml`: Metadados da aplicação, stack Python, local registry `localhost:5000` e flags de qualidade.
- `.github/configs/deploy-config.yml`: Definição declarativa dos ambientes `DSV`, `HMG` e `PRD`, portas e limites de recursos.

### 7.2 Esteira de 5 Workflows GitHub Actions
1. **`ci.yml`**: Executa no GitHub (`ubuntu-latest`) em todo `push` ou `pull_request` para a `main`. Faz lint, typecheck e testes unitários.
2. **`snapshot.yml`**: Executa no runner self-hosted (`build-linux-x64`) em branches de desenvolvimento. Gera tag dinâmica `${VERSION}-${RUN_NUMBER}-SNAPSHOT`, faz build Docker, envia para `localhost:5000` e realiza deploy automático em `DSV` com validação de healthcheck.
3. **`start-release.yml`**: Executa em PRs para `main`. Gera tag Release Candidate `${VERSION}-RC.${RUN_NUMBER}`, faz deploy em `DSV` e `HMG` com validações de saúde.
4. **`finish-release.yml`**: Executa após merge na `main`. Cria tag Git `v${VERSION}`, publica imagem `:latest` e `:${VERSION}`, e faz deploy em `PRD`.
5. **`redeploy.yml`**: Disparado via `workflow_dispatch` com parâmetros de versão e ambiente para rollbacks e redeploys controlados.

### 7.3 Endpoints de Saúde (Healthcheck)
- `/health`: Retorna `{ "status": "ok" }` (HTTP 200) para monitoramento do container e da esteira de CI/CD.
- `/ready`: Retorna o status detalhado das conexões (banco de dados, token do Instagram, chave do Gemini).

---

## 8. Regras de Estruturação e Manutenção da Documentação (`docs/`)

O diretório `docs/` deve conter e manter atualizados os seguintes arquivos padronizados:

| Arquivo | Descrição |
| :--- | :--- |
| `00_INDEX.md` | Índice geral e mapa de navegação de toda a documentação. |
| `01_REQUIREMENTS.md` | Requisitos funcionais, regras de negócio e limites de escopo da V1. |
| `02_SERVER_AUDIT.md` | Diagnóstico completo do host/servidor antes de implantação. |
| `03_ARCHITECTURE.md` | Desenho da arquitetura, diagramas Mermaid e fluxo de dados. |
| `04_INSTALLATION.md` | Guia passo a passo de setup e execução local/servidor. |
| `05_DOCKER.md` | Especificação de containers, volumes, redes e comandos de manutenção. |
| `06_CONFIGURATION.md` | Manual de todas as variáveis de ambiente, `.env` e chaves. |
| `07_TELEGRAM.md` | Guia do bot Telegram: criação via BotFather, IDs, comandos e telas. |
| `08_GEMINI.md` | Especificação dos prompts, schemas JSON e integração Google GenAI. |
| `09_VIDEO_GENERATION.md` | Documentação de geração assíncrona com Veo e pooling de operações. |
| `10_FFMPEG.md` | Especificação técnica de filtros, concatenações e conversões FFmpeg. |
| `11_INSTAGRAM.md` | **Manual completo de conexão do usuário com Instagram / Meta Graph API**. |
| `12_DATABASE.md` | Modelagem relacional, tabelas SQLite e regras de migração. |
| `13_SECURITY.md` | Políticas de sigilo de chaves, firewall, permissões e sanitização de logs. |
| `14_TESTS.md` | Plano de testes, execução de mocks e cobertura de código. |
| `15_TROUBLESHOOTING.md` | Guia de resolução de problemas comuns e códigos de erro de APIs. |
| `16_OPERATIONS.md` | Procedimentos operacionais: backup, restauração, logs e updates. |
| `17_CHANGELOG.md` | Histórico cronológico de mudanças e versões. |

### 8.1 Regra de "Realidade vs Expectativa"
A documentação deve refletir estritamente o estado real do projeto. Se uma integração depende de credenciais que o usuário ainda não forneceu, a documentação deve registrar explicitamente:
> `🟡 Implementado no código; aguardando credenciais reais para validação fim a fim.`

---

## 9. Regra de Stop Points (Paradas Estratégicas para Intervenção Humana)

Sempre que a execução técnica encontrar um bloqueio que dependa de credenciais ou autorizações externas do usuário (ex: criação do app no Facebook Developers, geração de token de usuário, API Key do Gemini), o agente deve emitir um **STOP POINT padronizado**, contendo:
1. **O que ocorreu:** Descrição objetiva do bloqueio.
2. **Por que ocorreu:** Qual permissão/chave é necessária.
3. **O que já foi implementado:** Estado atual do código.
4. **O que o usuário precisa fazer:** Passo a passo com links oficiais.
5. **Como validar após o preenchimento:** Comando ou teste para certificar a liberação.

---

## 10. Regras de Versionamento e Padrão de Commits

1. Seguir a convenção **Conventional Commits**:
   - `feat:` Nova funcionalidade
   - `fix:` Correção de bug
   - `docs:` Alterações na documentação
   - `test:` Inclusão ou ajuste de testes
   - `chore:` Configurações, dependências ou CI/CD
2. **Proteção de Branches:** Commits diretos na branch `main` são restritos aos merges de Pull Requests aprovados via esteira `start-release.yml` e `finish-release.yml`.
