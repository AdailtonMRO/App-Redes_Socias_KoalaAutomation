# Prompt Mestre — Projeto Instagram AI V1

## 1. Seu papel

Você é o **agente principal de desenvolvimento, DevOps, documentação e implantação** do projeto **Instagram AI V1**.

Você deverá trabalhar diretamente no meu **servidor Linux**, usando o ambiente já existente chamado **Home Labs**.

Seu trabalho não é apenas gerar código. Você deverá:

1. analisar o servidor antes de alterar qualquer coisa;
2. criar o ambiente Docker isolado do projeto;
3. instalar/configurar tudo que for necessário;
4. desenvolver a aplicação de acordo com esta especificação;
5. testar cada etapa;
6. corrigir erros encontrados;
7. documentar todo o processo;
8. deixar o sistema executável e reproduzível;
9. não destruir ou alterar serviços existentes no servidor.

> **Regra principal:** antes de executar qualquer instalação ou alteração no host, inspecione o ambiente e documente o que encontrou.

---

# 2. Objetivo do projeto

Construir uma aplicação chamada:

**Instagram AI**

A V1 deverá permitir que eu controle pelo **Telegram** um sistema que utiliza **Gemini/Veo** para criar Reels e, após minha aprovação explícita, publicar o conteúdo no Instagram.

Fluxo principal:

```text
Telegram
   ↓
Escolher perfil
   ↓
Escolher tema ou pedir sugestão à IA
   ↓
Gemini cria estratégia + roteiro
   ↓
Veo gera cenas/vídeo
   ↓
FFmpeg processa o vídeo
   ↓
Telegram recebe o Reel
   ↓
┌─────────────────────────────┐
│       APROVAÇÃO HUMANA      │
│                             │
│  ✅ PUBLICAR                │
│  🔄 REFAZER                 │
│  ✏️ ALTERAR                 │
│  ❌ DESCARTAR               │
└──────────────┬──────────────┘
               │
          ✅ PUBLICAR
               ↓
       Instagram API
               ↓
             REEL
```

**Nunca publicar automaticamente sem aprovação explícita do usuário na V1.**

---

# 3. Princípios de desenvolvimento

Siga estes princípios durante todo o projeto.

## 3.1 Segurança

- Nunca exponha API keys no código.
- Nunca grave tokens no Git.
- Utilize `.env`.
- Crie `.env.example` sem credenciais reais.
- Não exponha portas desnecessariamente.
- O bot Telegram deve aceitar comandos somente do meu Telegram User ID autorizado.
- Não execute comandos destrutivos no host sem necessidade.
- Não altere containers existentes.
- Não reinicie serviços existentes sem necessidade.
- Faça backup antes de alterar arquivos de configuração existentes.
- Utilize usuário não-root dentro do container sempre que possível.
- Use volumes somente onde forem necessários.

## 3.2 Isolamento

O projeto deverá rodar em seu próprio container Docker.

Não misture dependências com outros projetos existentes no Home Labs.

Nome sugerido:

```text
instagram-ai
```

Diretório sugerido:

```text
/opt/homelabs/instagram-ai
```

Porém, **não assuma que esse caminho existe**.

Primeiro inspecione o Home Labs e determine a estrutura utilizada no servidor.

## 3.3 Reprodutibilidade

Qualquer pessoa autorizada deverá conseguir reconstruir o projeto usando:

```text
Dockerfile
docker-compose.yml
.env.example
README.md
docs/
```

O README deverá explicar como reconstruir o ambiente do zero.

---

# 4. Antes de começar: inspeção obrigatória

Antes de instalar ou criar qualquer coisa, faça uma inspeção do servidor.

Verifique pelo menos:

```bash
uname -a
cat /etc/os-release
docker --version
docker compose version
df -h
free -h
nproc
lsblk
```

Verifique também:

- estrutura de `/opt`;
- estrutura do Home Labs;
- containers existentes;
- redes Docker existentes;
- volumes Docker;
- uso de CPU;
- memória disponível;
- espaço em disco;
- arquitetura da máquina;
- versão do Python existente no host, apenas para referência;
- disponibilidade do FFmpeg;
- portas utilizadas;
- existência de proxy reverso;
- existência de firewall;
- DNS/local network;
- possíveis limitações de acesso externo.

**Não instale nada ainda.**

Primeiro produza um diagnóstico.

Depois analise o diagnóstico e decida o que realmente precisa ser instalado.

---

# 5. Compatibilidade

O sistema deverá funcionar preferencialmente em:

```text
Linux
Docker
Docker Compose
Python 3.12+
```

Use versões atuais e estáveis compatíveis com as bibliotecas escolhidas.

Não fixe versões antigas sem justificativa.

Antes de utilizar uma API do Gemini/Veo, consulte a documentação oficial atual da Google para confirmar:

- modelo disponível;
- endpoint;
- SDK;
- autenticação;
- formato das requisições;
- geração assíncrona;
- download do vídeo;
- limites;
- formato vertical;
- duração suportada;
- eventuais mudanças de API.

Para Instagram, consulte a documentação oficial atual da Meta antes de implementar a publicação.

Não invente endpoints, permissões ou parâmetros.

---

# 6. Arquitetura desejada

A V1 deverá ter aproximadamente esta arquitetura:

```text
                  INTERNET
                     │
          ┌──────────┴──────────┐
          │                     │
      Telegram               Gemini
          │                     │
          │                     │
          ▼                     ▼
┌─────────────────────────────────────────┐
│           instagram-ai container        │
│                                         │
│  ┌──────────────┐                       │
│  │ Telegram Bot │                       │
│  └───────┬──────┘                       │
│          │                              │
│          ▼                              │
│  ┌──────────────────┐                   │
│  │ Orchestrator     │                   │
│  └────────┬─────────┘                   │
│           │                             │
│     ┌─────┼─────────────┐               │
│     ▼     ▼             ▼               │
│  Gemini  FFmpeg       Database          │
│     │     │             │               │
│     └─────┼─────────────┘               │
│           ▼                             │
│       /app/data                          │
│                                         │
└───────────────────────┬─────────────────┘
                        │
                        ▼
                  Instagram API
```

---

# 7. Tecnologias

Utilize, salvo justificativa técnica melhor:

### Backend

```text
Python 3.12+
FastAPI
```

### Telegram

Utilize uma biblioteca Python moderna e mantida para Telegram Bot API.

### IA

```text
Google Gemini API
Veo
```

A implementação deve separar:

```text
Gemini text/analysis
Gemini/Veo video generation
```

Não misture lógica de negócio diretamente com chamadas da API.

### Vídeo

```text
FFmpeg
```

### Banco

Na V1:

```text
SQLite
```

Prepare a camada de persistência para permitir migração futura para PostgreSQL.

### Container

```text
Docker
Docker Compose
```

---

# 8. Estrutura do projeto

Crie uma estrutura semelhante a:

```text
instagram-ai/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── .env
├── .env.example
├── README.md
│
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── bot/
│   │   ├── telegram_bot.py
│   │   ├── handlers.py
│   │   └── keyboards.py
│   │
│   ├── ai/
│   │   ├── gemini.py
│   │   ├── prompts.py
│   │   └── video_generator.py
│   │
│   ├── instagram/
│   │   └── publisher.py
│   │
│   ├── video/
│   │   ├── processor.py
│   │   └── ffmpeg.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   ├── profiles/
│   │   └── manager.py
│   │
│   └── services/
│       └── content_service.py
│
├── profiles/
│   └── koalatenis.json
│
├── data/
│   ├── videos/
│   ├── images/
│   ├── audio/
│   ├── thumbnails/
│   └── temp/
│
├── logs/
│
└── docs/
    ├── 00_INDEX.md
    ├── 01_REQUIREMENTS.md
    ├── 02_SERVER_AUDIT.md
    ├── 03_ARCHITECTURE.md
    ├── 04_INSTALLATION.md
    ├── 05_DOCKER.md
    ├── 06_CONFIGURATION.md
    ├── 07_TELEGRAM.md
    ├── 08_GEMINI.md
    ├── 09_VIDEO_GENERATION.md
    ├── 10_FFMPEG.md
    ├── 11_INSTAGRAM.md
    ├── 12_DATABASE.md
    ├── 13_SECURITY.md
    ├── 14_TESTS.md
    ├── 15_TROUBLESHOOTING.md
    ├── 16_OPERATIONS.md
    └── 17_CHANGELOG.md
```

Você pode ajustar essa estrutura se encontrar uma solução tecnicamente melhor, mas documente a alteração.

---

# 9. Perfil do Instagram

A aplicação deve trabalhar com perfis configuráveis.

Crie uma estrutura de perfil como:

```json
{
  "name": "Koala Tênis",
  "username": "@koalatenis_",
  "niche": [
    "tênis",
    "tecnologia",
    "DIY",
    "engenharia"
  ],
  "audience": [
    "tenistas amadores",
    "professores de tênis",
    "makers",
    "entusiastas de tecnologia"
  ],
  "tone": [
    "moderno",
    "técnico",
    "didático",
    "descontraído"
  ],
  "objectives": [
    "engajamento",
    "autoridade",
    "venda"
  ],
  "video_format": "9:16",
  "preferred_duration": "20-30s",
  "cta": "Conheça o curso Koala Tênis",
  "avoid": [
    "informações inventadas",
    "promessas exageradas"
  ]
}
```

Não codifique o perfil diretamente no programa.

---

# 10. Inteligência de conteúdo

O Gemini deverá receber:

```text
perfil
+
objetivo
+
tema
+
regras
+
feedback do usuário
```

e produzir uma estrutura JSON.

Exemplo:

```json
{
  "title": "...",
  "hook": "...",
  "objective": "...",
  "script": "...",
  "scenes": [
    {
      "duration": 6,
      "description": "...",
      "visual_prompt": "...",
      "narration": "..."
    }
  ],
  "caption": "...",
  "hashtags": [],
  "cta": "..."
}
```

Use **JSON estruturado**, não texto livre, sempre que a aplicação precisar consumir o resultado automaticamente.

Implemente validação do JSON.

Se o Gemini devolver conteúdo inválido:

1. registre o erro;
2. tente corrigir/reformular;
3. não continue para geração do vídeo enquanto o conteúdo não estiver válido.

---

# 11. Geração do vídeo

A V1 deve produzir Reels verticais.

Objetivo:

```text
9:16
MP4
H.264
AAC
```

A duração será determinada pela estratégia do conteúdo e pelas capacidades atuais do modelo de vídeo.

Se for necessário produzir várias cenas:

```text
Cena 1
Cena 2
Cena 3
Cena 4
      ↓
FFmpeg
      ↓
Reel final
```

Não presuma que o modelo consegue gerar diretamente um vídeo longo.

Consulte a documentação atual da API antes de implementar.

A geração de vídeo deve ser assíncrona.

O sistema deve:

```text
iniciar operação
      ↓
guardar operation_id
      ↓
consultar status
      ↓
aguardar conclusão
      ↓
baixar vídeo
      ↓
processar
```

Não faça polling agressivo.

Implemente:

- timeout;
- retry;
- backoff;
- tratamento de erro;
- registro do operation ID.

---

# 12. FFmpeg

O FFmpeg deverá:

- juntar cenas;
- ajustar resolução;
- converter formato;
- normalizar áudio;
- inserir narração quando necessário;
- inserir trilha quando aplicável;
- gerar thumbnail;
- produzir arquivo final.

Crie uma camada Python para abstrair os comandos FFmpeg.

Não espalhe comandos `subprocess` por toda a aplicação.

---

# 13. Telegram Bot

O Telegram será a principal interface da V1.

Comandos mínimos:

```text
/start
/novo
/status
/fila
/historico
/perfis
```

Menu principal:

```text
🤖 INSTAGRAM AI

🎬 Criar Reel
📋 Fila
📜 Histórico
👤 Perfis
⚙️ Configurações
```

---

# 14. Fluxo /novo

Ao executar:

```text
/novo
```

o bot deverá:

### Etapa 1

Perguntar:

```text
Qual perfil deseja trabalhar?
```

Mostrar os perfis cadastrados.

### Etapa 2

Perguntar:

```text
Você já tem um tema?
```

Botões:

```text
💡 IA escolher
✏️ Informar tema
```

### Etapa 3

Se o usuário informar tema:

Enviar para o Gemini.

Se escolher IA:

Pedir ao Gemini sugestões coerentes com o perfil.

### Etapa 4

Gerar estratégia e roteiro.

### Etapa 5

Gerar vídeo.

### Etapa 6

Processar vídeo.

### Etapa 7

Enviar para Telegram.

---

# 15. Mensagem de aprovação

O bot deverá enviar algo semelhante a:

```text
🎬 NOVO REEL

Perfil:
@koalatenis_

Tema:
...

Objetivo:
...

Duração:
...

🟡 AGUARDANDO APROVAÇÃO
```

Enviar o vídeo.

Adicionar botões:

```text
▶️ VISUALIZAR

✅ PUBLICAR

🔄 REFAZER

✏️ ALTERAR

❌ DESCARTAR
```

---

# 16. Aprovação humana

Esta regra é obrigatória:

> **Nenhum conteúdo poderá ser publicado na V1 sem uma ação explícita do usuário no Telegram.**

Quando clicar em:

```text
✅ PUBLICAR
```

o sistema deve:

1. validar se o conteúdo ainda está aguardando aprovação;
2. impedir publicação duplicada;
3. alterar status para `APPROVED`;
4. publicar;
5. registrar o ID retornado pelo Instagram;
6. alterar para `PUBLISHED`;
7. informar o resultado no Telegram.

Se ocorrer erro:

```text
ERROR
```

e informar claramente o motivo.

---

# 17. Refazer

Quando clicar:

```text
🔄 REFAZER
```

perguntar:

```text
O que deseja alterar?
```

O usuário poderá escrever livremente:

```text
"Faça um vídeo mais comercial e coloque um gancho mais forte nos primeiros 3 segundos."
```

Enviar para o Gemini:

```text
conteúdo original
+
feedback
```

Criar uma nova versão.

Não apagar a versão anterior.

Registrar:

```text
version = 2
```

---

# 18. Alteração

Quando clicar:

```text
✏️ ALTERAR
```

permitir feedback em linguagem natural.

Exemplo:

```text
"Troque a chamada final por algo mais voltado para o curso."
```

A IA deverá modificar apenas o necessário, preservando o restante do conteúdo.

---

# 19. Estados do conteúdo

Implemente uma máquina de estados:

```text
DRAFT
GENERATING_SCRIPT
GENERATING_VIDEO
PROCESSING_VIDEO
WAITING_APPROVAL
REGENERATING
APPROVED
PUBLISHING
PUBLISHED
REJECTED
ERROR
```

Evite transições inválidas.

Exemplo:

```text
PUBLISHED
```

não pode voltar para:

```text
WAITING_APPROVAL
```

sem uma ação administrativa explícita.

---

# 20. Banco de dados

Implemente pelo menos:

## profiles

```text
id
name
username
instagram_account_id
config_json
active
created_at
updated_at
```

## contents

```text
id
profile_id
title
topic
script
caption
hashtags
status
current_version
video_path
thumbnail_path
instagram_media_id
created_at
updated_at
published_at
```

## generations

```text
id
content_id
version
prompt
gemini_operation_id
video_path
created_at
```

## actions

```text
id
content_id
action
telegram_user_id
metadata
created_at
```

---

# 21. Instagram

Antes de implementar a publicação, consulte a documentação oficial atual da Meta.

Determine exatamente:

- tipo de conta necessário;
- API apropriada;
- permissões necessárias;
- fluxo de autenticação;
- criação do container de mídia;
- publicação;
- requisitos de URL pública do vídeo, se aplicável;
- limites;
- tratamento de erros.

Não invente a API.

Documente tudo em:

```text
docs/11_INSTAGRAM.md
```

Se alguma etapa exigir intervenção manual minha, pare nessa etapa e explique exatamente o que preciso fazer.

Não tente contornar permissões da Meta.

---

# 22. Credenciais

O projeto deve usar:

```text
GEMINI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_ALLOWED_USER_ID
INSTAGRAM_APP_ID
INSTAGRAM_APP_SECRET
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_ACCOUNT_ID
```

Se alguma credencial estiver faltando:

**não invente.**

Crie a configuração necessária e documente como obter a credencial.

---

# 23. Logs

Crie logs estruturados.

Registrar:

```text
timestamp
level
service
operation
content_id
message
error
```

Nunca registrar:

- API keys;
- access tokens;
- secrets;
- dados privados desnecessários.

---

# 24. Tratamento de erros

Todo serviço externo deve possuir:

```text
timeout
retry
backoff
error handling
logging
```

Diferencie:

```text
erro temporário
erro permanente
erro de configuração
erro de autenticação
erro de conteúdo
```

O Telegram deve informar erros de maneira simples.

Exemplo:

```text
❌ Não foi possível gerar o vídeo.

Motivo:
A operação do Veo expirou.

A geração será marcada como ERROR.

Use /status para verificar.
```

---

# 25. Testes

Crie testes para:

### Unitários

- configuração;
- validação do perfil;
- validação do JSON do Gemini;
- máquina de estados;
- banco;
- geração de comandos FFmpeg.

### Integração

- Telegram;
- Gemini;
- geração de vídeo;
- Instagram.

Quando uma API real exigir credencial, crie também mocks para permitir testes sem consumir créditos.

---

# 26. Health check

Implemente:

```text
/health
```

Retorno:

```json
{
  "status": "ok"
}
```

Se fizer sentido, implemente também:

```text
/ready
```

verificando:

- banco;
- configuração;
- serviços essenciais.

---

# 27. Observabilidade

Crie pelo menos:

```text
/status
```

no Telegram.

Exemplo:

```text
🤖 STATUS

Container: 🟢
Database: 🟢
Telegram: 🟢
Gemini: 🟢
FFmpeg: 🟢
Instagram: 🟢

Fila:
2 aguardando aprovação

Processando:
1
```

Não faça chamadas caras à API apenas para mostrar status.

---

# 28. Documentação obrigatória

A pasta:

```text
docs/
```

é parte obrigatória do projeto.

Documente **durante o desenvolvimento**, não apenas no final.

## 00_INDEX.md

Índice de toda documentação.

## 01_REQUIREMENTS.md

Requisitos funcionais e não funcionais.

## 02_SERVER_AUDIT.md

Tudo que foi encontrado no servidor antes da instalação.

Inclua:

- SO;
- Docker;
- recursos;
- containers existentes;
- redes;
- volumes;
- portas;
- decisões tomadas.

## 03_ARCHITECTURE.md

Arquitetura completa.

Inclua diagramas Mermaid quando útil.

## 04_INSTALLATION.md

Como instalar.

## 05_DOCKER.md

Containers, volumes, redes e comandos.

## 06_CONFIGURATION.md

`.env`, configurações e credenciais.

## 07_TELEGRAM.md

Criação do bot, comandos e funcionamento.

## 08_GEMINI.md

Modelos utilizados, API, prompts, autenticação, limitações e custos relevantes.

## 09_VIDEO_GENERATION.md

Veo, geração de cenas, polling, download e tratamento de erros.

## 10_FFMPEG.md

Processamento dos vídeos.

## 11_INSTAGRAM.md

Configuração e publicação.

## 12_DATABASE.md

Modelo de dados.

## 13_SECURITY.md

Segurança.

## 14_TESTS.md

Testes executados e resultados.

## 15_TROUBLESHOOTING.md

Problemas encontrados e soluções.

## 16_OPERATIONS.md

Como operar o sistema no dia a dia.

## 17_CHANGELOG.md

Histórico das alterações.

---

# 29. Registro de decisões

Sempre que tomar uma decisão técnica importante, registre:

```text
Data
Decisão
Motivo
Alternativas consideradas
Consequência
```

Exemplo:

```text
2026-09-21

Decisão:
Utilizar SQLite na V1.

Motivo:
Baixa complexidade e volume inicial.

Alternativa:
PostgreSQL.

Consequência:
A camada repository deve ser abstraída para permitir migração futura.
```

---

# 30. Git

Se o ambiente possuir Git e fizer sentido para o projeto:

Inicialize um repositório.

Crie:

```text
.gitignore
```

Nunca versionar:

```text
.env
data/
logs/
*.mp4
*.mov
*.wav
*.jpg
*.png
__pycache__/
```

Crie commits lógicos.

Sugestão:

```text
feat: initialize project
feat: add telegram bot
feat: add gemini integration
feat: add video generation
feat: add ffmpeg processing
feat: add instagram publisher
test: add integration tests
docs: add deployment documentation
```

---

# 31. Ordem de implementação

Não tente fazer tudo de uma vez.

Siga esta sequência:

## FASE 0 — Auditoria

- analisar servidor;
- analisar Home Labs;
- verificar Docker;
- verificar recursos;
- documentar.

## FASE 1 — Bootstrap

- criar diretório;
- criar Git;
- criar Dockerfile;
- criar Compose;
- criar `.env.example`;
- criar estrutura Python;
- criar docs.

## FASE 2 — Banco

- criar SQLite;
- models;
- repositories;
- migrations/versionamento simples.

## FASE 3 — Telegram

Implementar:

```text
/start
/novo
/status
/fila
/historico
```

Primeiro faça o fluxo funcionando sem IA.

## FASE 4 — Gemini

Implementar:

```text
perfil
+
tema
→
roteiro JSON
```

Testar.

## FASE 5 — Vídeo

Implementar:

```text
roteiro
→
Veo
→
download
→
FFmpeg
```

Testar.

## FASE 6 — Aprovação

Implementar:

```text
vídeo
→
Telegram
→
botões
```

Testar:

```text
publicar
refazer
alterar
descartar
```

## FASE 7 — Instagram

Implementar publicação real.

Antes disso, testar autenticação e permissões.

## FASE 8 — Integração ponta a ponta

Executar:

```text
/novo
→
Gemini
→
Veo
→
FFmpeg
→
Telegram
→
aprovação
→
Instagram
```

## FASE 9 — Documentação final

Atualizar todos os documentos.

## FASE 10 — Backup e operação

Documentar:

- backup;
- restore;
- atualização;
- logs;
- restart;
- troubleshooting.

---

# 32. Critérios de aceite da V1

A V1 somente será considerada concluída quando:

### Infraestrutura

- [ ] Container criado.
- [ ] Container reinicia automaticamente.
- [ ] Aplicação inicia sem erro.
- [ ] Dados persistem após restart.
- [ ] Logs funcionam.

### Telegram

- [ ] `/start` funciona.
- [ ] `/novo` funciona.
- [ ] `/status` funciona.
- [ ] `/fila` funciona.
- [ ] `/historico` funciona.
- [ ] Apenas usuário autorizado pode controlar o bot.

### Gemini

- [ ] API configurada.
- [ ] Perfil é utilizado.
- [ ] Tema é interpretado.
- [ ] Roteiro estruturado é gerado.
- [ ] JSON é validado.

### Vídeo

- [ ] Veo é chamado corretamente.
- [ ] Operação assíncrona funciona.
- [ ] Vídeo é baixado.
- [ ] FFmpeg processa.
- [ ] Reel final é 9:16.
- [ ] Thumbnail é criada.

### Aprovação

- [ ] Vídeo chega ao Telegram.
- [ ] Publicação não ocorre automaticamente.
- [ ] Aprovar funciona.
- [ ] Refazer funciona.
- [ ] Alterar funciona.
- [ ] Descartar funciona.
- [ ] Não existe publicação duplicada.

### Instagram

- [ ] Autenticação funciona.
- [ ] Publicação de Reel funciona.
- [ ] ID da publicação é armazenado.
- [ ] Resultado é informado no Telegram.

### Documentação

- [ ] Todos os documentos existem.
- [ ] README funciona para instalação.
- [ ] Procedimento de backup documentado.
- [ ] Troubleshooting documentado.
- [ ] Changelog atualizado.

---

# 33. Regra sobre bloqueios

Se encontrar qualquer bloqueio:

```text
credencial ausente
API incompatível
permissão da Meta
modelo indisponível
dependência incompatível
erro no servidor
```

não esconda o problema.

Faça:

1. identificar;
2. registrar;
3. investigar;
4. tentar solução segura;
5. documentar.

Se depender de uma ação manual minha:

```text
STOP POINT
```

Informe:

```text
O que aconteceu
Por que aconteceu
O que já foi feito
O que preciso fazer
Comando/link/configuração necessária
Como validar depois
```

Não invente uma solução.

---

# 34. Regra sobre documentação

Sempre que modificar a arquitetura ou descobrir algo importante, atualize `docs/`.

A documentação deve refletir o **estado real do servidor e do código**, não o estado planejado.

Não escreva:

> "O Instagram está funcionando."

se o teste ainda não foi executado.

Escreva:

> "Integração implementada, aguardando credencial/permissão para teste."

---

# 35. Regra sobre custos

Sempre que uma operação puder consumir créditos da API Gemini/Veo:

- sinalize;
- evite geração duplicada;
- utilize mocks nos testes quando possível;
- registre operações;
- não gere vídeos reais desnecessariamente.

Durante desenvolvimento, prefira:

```text
mock
→ teste
→ integração real
```

---

# 36. Regra sobre geração de conteúdo

O Gemini não deve inventar informações sobre o produto/perfil.

Quando o conteúdo depender de fatos específicos:

```text
perfil
produto
preço
característica técnica
estatística
resultado
```

utilize somente informações fornecidas/configuradas.

Se não houver informação:

```text
não inventar
```

O sistema deve preferir perguntar ou sinalizar a ausência.

---

# 37. Regra sobre o papel humano

A V1 é:

**SEMI-AUTOMÁTICA**

Não transforme o sistema em publicação automática.

A decisão final de publicar pertence ao usuário.

A IA:

```text
analisa
cria
sugere
gera
```

O usuário:

```text
aprova
edita
rejeita
```

O sistema:

```text
executa
registra
publica após aprovação
```

---

# 38. Resultado esperado

Ao terminar, eu quero poder entrar no servidor e executar:

```bash
cd /opt/homelabs/instagram-ai
docker compose up -d
```

e o sistema ficar disponível.

Depois, no Telegram:

```text
/start
```

E conseguir executar o fluxo completo.

---

# 39. Entrega final

Ao concluir o desenvolvimento, produza no Telegram/terminal um resumo:

```text
========================================
 INSTAGRAM AI V1 — IMPLEMENTAÇÃO
========================================

Servidor:
...

Container:
...

Status:
🟢 ...

Telegram:
🟢 ...

Gemini:
🟢 ...

Veo:
🟢 ...

FFmpeg:
🟢 ...

Instagram:
🟢 / 🟡 / 🔴

Testes:
...

Documentação:
...

Pendências:
...

Próximos passos:
...
```

Inclua também:

```text
docker compose ps
docker compose logs --tail=50
```

ou equivalentes, quando apropriado.

---

# 40. Instrução final

Comece agora.

**Não pule a auditoria do servidor.**

Primeiro:

1. inspecione o Linux;
2. inspecione o Home Labs;
3. inspecione Docker;
4. documente o diagnóstico em `docs/02_SERVER_AUDIT.md`;
5. apresente/registre as decisões de arquitetura;
6. somente depois crie o container;
7. implemente fase por fase;
8. teste cada fase;
9. corrija os erros;
10. mantenha `docs/` atualizado;
11. finalize com teste ponta a ponta.

**Não considere o projeto concluído apenas porque o código foi criado. O critério de conclusão é o fluxo real funcionando no servidor, com aprovação pelo Telegram e publicação no Instagram, respeitando todas as permissões e APIs oficiais vigentes.**

