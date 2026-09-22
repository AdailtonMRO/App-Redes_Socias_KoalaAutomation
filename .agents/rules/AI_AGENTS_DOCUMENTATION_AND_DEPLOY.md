# 🤖 REGRAS OBRIGATÓRIAS PARA TODOS OS AGENTES DE IA
## Projeto: Koala Automation — Social Media Automation
### Vigência: Permanente · Aplica-se a: TODOS os agentes, sessões e tarefas

> **AVISO CRÍTICO:** Estas regras NÃO são sugestões. São pré-requisitos **inegociáveis** para
> qualquer alteração de código, configuração, documentação ou infraestrutura.
> Um agente que ignora estas regras está em **violação de governança** do projeto.

---

## REGRA 0 — ANTES DE QUALQUER ALTERAÇÃO

Antes de modificar qualquer arquivo, o agente DEVE verificar:

| Pergunta | Ação obrigatória se "Sim" |
|----------|---------------------------|
| Esta mudança altera comportamento visível ao usuário? | Documentar em CHANGELOG + módulo afetado |
| Esta mudança altera configuração de ambiente (.env, Docker, portas)? | Atualizar `06_CONFIGURATION.md` + `05_DOCKER.md` |
| Esta mudança altera arquitetura ou fluxo de dados? | Atualizar `03_ARCHITECTURE.md` |
| Esta mudança adiciona ou remove dependências? | Atualizar `requirements.txt` + `04_INSTALLATION.md` |
| Esta mudança exige ação do operador humano no servidor? | Emitir STOP POINT + guia em `19_DEPLOY_HOMELAB.md` |
| Esta mudança quebra compatibilidade com versão anterior? | Incrementar versão MAJOR no `VERSION` + alertar usuário |

---

## REGRA 1 — DOCUMENTAÇÃO OBRIGATÓRIA A CADA ALTERAÇÃO

### 1.1 Atualizar o CHANGELOG a cada modificação

Toda e qualquer modificação de código ou configuração **deve** ter uma entrada em
`docs/17_CHANGELOG.md` seguindo o formato Keep a Changelog:

```markdown
## [VERSÃO] — AAAA-MM-DD

### 🚀 Novas Funcionalidades
- Descrição objetiva da feature. (módulo afetado)

### 🐛 Correções de Bugs
- Descrição do bug corrigido e causa raiz. (módulo afetado)

### 🔧 Melhorias Técnicas
- Refactoring, otimização, melhoria de performance.

### 📚 Documentação
- Documentos criados, atualizados ou corrigidos.

### 🛡️ Segurança
- Correções de vulnerabilidade ou endurecimento de configuração.

### ⚠️ Breaking Changes
- O que quebrou e como migrar. OBRIGATÓRIO se MAJOR version bump.

### 🗑️ Removidos
- Funcionalidades ou arquivos removidos definitivamente.
```

**Regras de escrita do CHANGELOG:**
- Usar linguagem objetiva e técnica em português brasileiro
- Sempre referenciar o módulo ou arquivo afetado
- Entradas devem ser compreensíveis por um humano que não viu o código

### 1.2 Atualizar o documento técnico correspondente

| Se modificar... | Atualizar também... |
|-----------------|---------------------|
| `app/ai/` ou prompts | `docs/08_GEMINI.md` |
| `app/video/` ou FFmpeg | `docs/10_FFMPEG.md` |
| `app/instagram/` ou Meta API | `docs/11_INSTAGRAM.md` |
| `app/telegram/` | `docs/07_TELEGRAM.md` |
| `app/database/` ou models | `docs/12_DATABASE.md` |
| `app/research/` | `docs/18_CONTENT_RADAR.md` |
| `.env` ou `.env.example` | `docs/06_CONFIGURATION.md` |
| `Dockerfile` ou `docker-compose.yml` | `docs/05_DOCKER.md` |
| `requirements.txt` | `docs/04_INSTALLATION.md` |
| Fluxo principal de dados | `docs/03_ARCHITECTURE.md` |
| Testes em `tests/` | `docs/14_TESTS.md` |
| Scripts de operação | `docs/16_OPERATIONS.md` |

### 1.3 Arquivar decisões arquiteturais relevantes

Para mudanças significativas (novas features, breaking changes, mudanças de arquitetura),
criar ou atualizar `docs/archive/AAAA-MM-DD_DESCRICAO.md` com:
- **Contexto:** Por que a mudança foi feita
- **Decisão técnica:** Qual abordagem foi escolhida e por quê
- **Alternativas descartadas:** O que foi considerado mas não adotado
- **Impacto:** O que pode ser afetado por esta mudança

---

## REGRA 2 — VERSIONAMENTO SEMÂNTICO OBRIGATÓRIO

Atualizar o arquivo `VERSION` conforme a natureza da mudança:

```
MAJOR.MINOR.PATCH
  |     |     |-- Bug fix, correção de documentação, ajuste cosmético
  |     |-------- Nova funcionalidade retrocompatível, nova integração
  |-------------- Breaking change, refatoração arquitetural, mudança de API
```

**Exemplos práticos:**
- Corrigir um bug no parser de resposta do Gemini: 1.0.0 -> 1.0.1
- Adicionar suporte a Stories além de Reels: 1.0.0 -> 1.1.0
- Migrar de SQLite para PostgreSQL: 1.0.0 -> 2.0.0

**O agente NUNCA deve:**
- Deixar `VERSION` desatualizado após uma mudança relevante
- Usar versões com sufixos não padronizados (ex: 1.0.0-beta, 1.0.0-dev)
- Decrementar a versão

---

## REGRA 3 — PREPARAÇÃO PARA DEPLOY NO HOMELAB

### 3.1 Checklist pré-deploy obrigatório

Antes de qualquer mudança que será deployada, verificar:

```
[ ] O arquivo VERSION foi atualizado?
[ ] O CHANGELOG foi atualizado com a entrada da versão correta?
[ ] O .env.example foi atualizado se novas variáveis foram adicionadas?
[ ] Os testes passam (ou existe justificativa documentada)?
[ ] O Dockerfile está válido e o container sobe sem erros?
[ ] O endpoint /health responde HTTP 200 após o build?
[ ] Não há credenciais, tokens ou senhas hardcoded no código?
[ ] As novas variáveis foram documentadas em 06_CONFIGURATION.md?
```

### 3.2 Commit com mensagem no padrão Conventional Commits

```
feat(módulo): descrição curta da mudança

- Detalhe 1 do que foi implementado
- Detalhe 2 do que foi alterado

Closes #issue (se aplicável)
```

### 3.3 Instrução de deploy manual obrigatória (fallback)

Se a pipeline CI/CD NÃO puder ser executada automaticamente, gerar ao final da tarefa:

```
INSTRUCOES DE DEPLOY MANUAL
Versão: X.Y.Z | Data: AAAA-MM-DD | Ambiente: DSV / HMG / PRD

PASSO 1: Conectar ao servidor HomeLab
  ssh usuario@10.0.0.119
  cd /caminho/do/projeto
  git pull origin [branch-name]

PASSO 2: Build e deploy
  docker build -t localhost:5000/social-media-koala:[VERSAO] .
  docker compose up -d --force-recreate

PASSO 3: Validação
  curl http://localhost:[PORTA]/health
  Esperado: {"status": "ok"} HTTP 200

Ver guia completo em: docs/19_DEPLOY_HOMELAB.md
```

---

## REGRA 4 — ESTRUTURA DE ARQUIVOS DE DOCUMENTAÇÃO

O agente DEVE garantir que os seguintes arquivos existam e estejam atualizados:

```
docs/
├── 00_INDEX.md              <- ATUALIZAR ao adicionar qualquer novo doc
├── 00_REGRAS_E_DIRETRIZES.md
├── 17_CHANGELOG.md          <- ATUALIZAR A CADA MUDANÇA
├── 19_DEPLOY_HOMELAB.md     <- ATUALIZAR quando houver mudanças de infra
└── archive/                 <- Histórico imutável de decisões arquiteturais
    └── AAAA-MM-DD_TEMA.md
```

**O agente NUNCA deve:**
- Deletar entradas anteriores do CHANGELOG
- Sobrescrever docs/archive/ — arquivos neste diretório são imutáveis
- Criar documentação duplicada sem referenciar no 00_INDEX.md

---

## REGRA 5 — SEGURANÇA DE CREDENCIAIS (INEGOCIÁVEL)

O agente NUNCA deve:
- Inserir valores reais de tokens, senhas, API keys ou URLs privadas em qualquer arquivo
- Commitar arquivos .env com valores reais (apenas .env.example com valores dummy)
- Exibir, logar ou retornar valores de variáveis de ambiente secretas em mensagens de saída
- Criar scripts que leem credenciais de argumentos de linha de comando (--token=xyz)

Se precisar referenciar uma credencial, DEVE usar placeholder:
```bash
# Correto
export GEMINI_API_KEY="sua_chave_aqui"

# Proibido
export GEMINI_API_KEY="AIzaSy...xyz"
```

---

## REGRA 6 — FLUXO DE TRABALHO PADRÃO DO AGENTE

Para QUALQUER tarefa de desenvolvimento, seguir este fluxo:

1. ENTENDER    -> Ler documentação existente antes de codar
2. PLANEJAR    -> Definir escopo, módulos e impacto
3. IMPLEMENTAR -> Escrever código limpo e testável
4. TESTAR      -> Verificar funcionamento (unit/integração)
5. DOCUMENTAR  -> CHANGELOG + doc do módulo + INDEX  [NUNCA OPCIONAL]
6. VERSIONAR   -> Atualizar VERSION conforme SemVer
7. PREPARAR    -> Gerar instruções de deploy (auto/manual)
8. REPORTAR    -> Comunicar ao usuário o que foi feito

---

## REGRA 7 — COMUNICAÇÃO COM O OPERADOR HUMANO

### 7.1 Relatório pós-tarefa obrigatório

Ao final de cada tarefa, emitir um resumo com:

```markdown
## Resumo da Tarefa Concluída

**O que foi feito:**
- Item 1
- Item 2

**Arquivos modificados:**
- caminho/do/arquivo.py — descrição da mudança
- docs/17_CHANGELOG.md — entrada adicionada para v[X.Y.Z]

**Versão:** [anterior] -> [nova]

**Status de Deploy:**
- Automático: [ATIVO via snapshot.yml | REQUER runner self-hosted]
- Manual: Ver instruções em docs/19_DEPLOY_HOMELAB.md

**Ações pendentes para o operador:**
- [ ] Ação que só o humano pode fazer
```

### 7.2 STOP POINTS

Quando encontrar um bloqueio que requer intervenção humana, emitir:

```markdown
## STOP POINT — [TÍTULO DO BLOQUEIO]

**O que ocorreu:** Descrição objetiva.
**Por que ocorreu:** Qual permissão, chave ou ação externa é necessária.
**O que já foi implementado:** Estado atual do código/configuração.
**O que o operador precisa fazer:**
  1. Passo um
  2. Passo dois
**Como validar após a ação:**
  $ comando de validação
```

---

## REGRA 8 — MANUTENÇÃO PERIÓDICA DA DOCUMENTAÇÃO

Quando solicitado ou quando perceber inconsistências, auditar:
- Se o 00_INDEX.md reflete todos os arquivos em docs/
- Se o 17_CHANGELOG.md tem entradas para todas as versões no histórico do Git
- Se o 03_ARCHITECTURE.md corresponde ao código atual
- Se o .env.example contém todas as variáveis usadas no código

---

Última revisão: 2026-09-22
Responsável: Engenharia Koala Automation
Este documento é gerenciado pelo sistema de regras dos agentes de IA.
