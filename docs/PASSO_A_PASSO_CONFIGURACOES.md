# 📖 Guia Passo a Passo: Configuração do Instagram, IA (Gemini) e Telegram

> **Objetivo:** Manual prático e ilustrado para guiar qualquer usuário na obtenção de credenciais e configuração da automação no Painel Web (`http://<IP_DO_SERVIDOR>:8085`).

---

## 📸 PARTE 1: Configuração do Instagram (Meta Graph API)

Para publicar Reels automaticamente e de forma 100% oficial e segura (sem risco de bloqueios), a Meta exige o uso da **Instagram Graph API**.

### Etapa 1.1: Pré-Requisitos da Conta no Celular
1. Abra o aplicativo do **Instagram** no celular.
2. Acesse seu perfil > **Configurações e privacidade** > **Tipo e ferramentas da conta** > Mude para **Conta Profissional** (Comercial/Business ou Criador de Conteúdo/Creator).
3. Conecte o seu Instagram a uma **Página do Facebook** que você gerencia (se não tiver, crie uma Página gratuita no Facebook).

---

### Etapa 1.2: Criar o Aplicativo no Portal Meta for Developers
1. Acesse pelo computador: [developers.facebook.com](https://developers.facebook.com/) e faça login.
2. No menu superior, clique em **Meus Apps** (My Apps) > **Criar Aplicativo** (Create App).
3. Escolha o caso de uso: **Outro** (Other) > Avançar > Selecione **Empresa** (Business).
4. Dê um nome ao seu app (ex: `Koala Automation`) e informe seu e-mail.

---

### Etapa 1.3: Adicionar a API do Instagram e Permissões
1. No painel do seu aplicativo criado, role até a lista de produtos e clique em **Configurar** no card **API do Graph do Instagram** (Instagram Graph API).
2. Acesse a ferramenta oficial: [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
3. No campo **Aplicativo da Meta**, selecione o aplicativo que você acabou de criar.
4. No campo **Permissões** (Permissions), adicione estas 4 permissões obrigatórias:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
5. Clique em **Generate Access Token** (Gerar Token de Acesso) e aprove o acesso conectando sua Página e seu Instagram.

---

### Etapa 1.4: Descobrir o seu `Instagram Account ID` (Numérico)
No **Graph API Explorer**, na barra de consulta URL (onde está escrito `GET -> me?fields=id,name`), substitua por:
```text
me/accounts?fields=name,instagram_business_account{id,username}
```
Clique em **Submit**. A resposta será semelhante a esta:
```json
{
  "data": [
    {
      "name": "Minha Página",
      "instagram_business_account": {
        "id": "17841405678912345",   <--- ESTE É O SEU INSTAGRAM_ACCOUNT_ID
        "username": "koalatenis_"
      }
    }
  ]
}
```
> Copie o número que está em `"id"` (ex: `17841405678912345`).

---

### Etapa 1.5: Gerar o Token de Longa Duração (60 Dias)
O token gerado no Explorer dura apenas 1 hora. Para torná-lo durável por 60 dias:
1. Acesse o [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).
2. Cole o token gerado e clique em **Depurar** (Debug).
3. Role até o rodapé e clique no botão azul **Estender Token de Acesso** (Extend Access Token).
4. Copie o novo token de longa duração gerado.

---

### Etapa 1.6: Inserir no Painel Web
1. Abra no navegador: `http://10.0.0.119:8085`.
2. Na aba **Instagram & Meta**:
   - Cole o **Instagram Business Account ID** (número da etapa 1.4).
   - Cole o **User / System Access Token** (token estendido da etapa 1.5).
3. Clique em **"⚡ Testar Conexão com o Instagram"**.
4. O card mostrará: `✅ Conexão Bem-Sucedida!` com o @username do seu perfil.
5. Clique em **"💾 Salvar Configurações"** no topo da tela.

---

## ✨ PARTE 2: Configuração da IA (Google Gemini & Veo)

O cérebro do sistema utiliza o Google Gemini para analisar sua marca e criar roteiros estratégicos, e o modelo Google Veo para gerar vídeos cinematográficos em formato vertical 9:16.

### Etapa 2.1: Obter a Chave de API Gratuita
1. Acesse o portal oficial: [aistudio.google.com](https://aistudio.google.com/).
2. Faça login com sua conta do Google.
3. No menu lateral esquerdo, clique no botão azul **Get API key** (Obter Chave de API).
4. Clique em **Create API key** (Criar Chave de API) > Selecione um projeto do Google Cloud ou crie um novo padrão.
5. Copie a chave gerada (iniciada por `AIzaSy...`).

---

### Etapa 2.2: Inserir no Painel Web
1. No seu Painel Web (`http://10.0.0.119:8085`), acesse a aba **Google Gemini & Veo**.
2. No campo **Google Gemini API Key**, cole a sua chave `AIzaSy...`.
3. Escolha o modelo de texto:
   - **Gemini 2.5 Flash** *(Recomendado: ultrarrápido, excelente para roteiros e muito econômico)*.
4. Escolha o modelo de vídeo:
   - **Google Veo 2.0** *(Gera os vídeos verticais)* ou **Mock Generator** *(Modo teste sem custo)*.
5. Clique em **"💾 Salvar Configurações"** no topo.

---

## ✈️ PARTE 3: Configuração do Telegram Bot (Controle e Aprovação)

O Telegram é a ferramenta de controle remoto. Por ele você pede novos Reels e aprova com 1 clique antes de publicar.

### Etapa 3.1: Criar o seu Bot com o @BotFather
1. No aplicativo do Telegram (no celular ou computador), pesquise por: **`@BotFather`** (verifique se possui o selo azul de verificado).
2. Inicie a conversa e envie o comando:
   ```text
   /newbot
   ```
3. O BotFather perguntará:
   - *Nome de exibição do bot:* Exemplo: `Koala Reels Automation`
   - *Username do bot (deve terminar em `bot`):* Exemplo: `KoalaReelsAutomation_bot`
4. O BotFather responderá com o seu **HTTP API Token**:
   ```text
   Use this token to access the HTTP API:
   7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ  <--- ESTE É O SEU TELEGRAM_BOT_TOKEN
   ```
   Copie este token.

---

### Etapa 3.2: Descobrir o seu ID de Usuário (Segurança Obrigatória)
Para que ninguém além de você possa mandar comandos para o seu bot:
1. No Telegram, pesquise pelo bot: **`@userinfobot`**.
2. Clique em **Iniciar** (`/start`).
3. Ele responderá com o seu perfil:
   ```text
   Id: 123456789  <--- ESTE É O SEU TELEGRAM_ALLOWED_USER_ID
   First: Seu Nome
   ```
   Copie o seu número de **Id**.

---

### Etapa 3.3: Inserir no Painel Web
1. No Painel Web, acesse a aba **Telegram Bot**.
2. No campo **Telegram Bot Token**, cole o token fornecido pelo BotFather.
3. No campo **Telegram User ID Autorizado**, cole o seu ID numérico do `@userinfobot`.
4. Clique em **"💾 Salvar Configurações"** no topo.

---

## 👤 PARTE 4: Configuração dos Perfis de Automação (Multi-Contas)

Se você tem mais de uma conta do Instagram ou quer calibrar o tom de voz da IA:
1. Acesse a aba **Perfis de Automação**.
2. Clique em **"✏️ Editar"** no perfil existente ou **"+ Adicionar Novo Perfil"** para uma nova marca.
3. Preencha:
   - **Nome da Marca:** Ex: `Koala Tênis`
   - **Username:** Ex: `@koalatenis_`
   - **Instagram Account ID:** O ID numérico daquela conta (se diferente da principal).
   - **Nichos:** Ex: `tênis, raquetes, treinamento, makers, tecnologia`
   - **Tom de Voz:** Ex: `técnico, didático, descontraído, motivador`
   - **Chamada para Ação (CTA):** Ex: `Clique no link da bio para conferir a nova coleção!`
   - **O que Evitar (Regras Anti-Alucinação):** Ex: `não inventar preços de raquetes, não prometer resultados milagrosos`
4. Clique em **Salvar Perfil**.
5. No card do perfil, clique no botão **"⚡ Testar"** para confirmar a conectividade!

---

## 🎯 Resumo da Operação Diária

Após essa configuração única de 5 minutos, você nunca mais precisa abrir o código:

```text
Você no Telegram           IA do Sistema                   Instagram
     │                           │                             │
     ├──── /novo ───────────────►│                             │
     │                           ├─ Gemini cria roteiro        │
     │                           ├─ Veo gera cenas 9:16        │
     │                           ├─ FFmpeg monta o vídeo       │
     │◄─── Envia vídeo pronto ───┤                             │
     │     com botões            │                             │
     │                           │                             │
     ├──── [✅ PUBLICAR] ────────►│                             │
     │                           ├──── Publica Reel oficial ──►│
     │◄─── Link do Reel postado ─┤                             │
```
