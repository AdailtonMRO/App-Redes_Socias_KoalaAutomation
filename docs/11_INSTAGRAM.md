# 📸 Guia de Configuração e Conexão do Instagram (Meta Graph API)

> **Documento Técnico:** `docs/11_INSTAGRAM.md`  
> **Objetivo:** Orientar detalhadamente como o usuário configura o acesso à sua conta do Instagram para permitir que o sistema conecte e publique Reels automaticamente (após aprovação humana).

---

## 1. Pré-Requisitos Obrigatórios na Meta

Para que uma automação publique conteúdo no Instagram através da API oficial (sem risco de bloqueio ou banimento por web scraping não-oficial), a Meta exige o uso da **Instagram Graph API**.

### 1.1 Tipo de Conta
1. A conta do Instagram deve ser **Profissional** (tipo **Comercial / Business** ou **Criador de Conteúdo / Creator**). Contas pessoais não possuem permissão de publicação via API.
2. A conta do Instagram deve estar **obrigatoriamente vinculada a uma Página do Facebook** gerenciada pelo usuário.

---

## 2. Passo a Passo de Configuração pelo Usuário

### Passo 1: Criar o Aplicativo no Meta for Developers
1. Acesse o portal oficial [Meta for Developers](https://developers.facebook.com/).
2. Faça login com a conta do Facebook administradora da Página/Instagram.
3. Vá em **Meus Apps** (My Apps) > **Criar Aplicativo** (Create App).
4. Selecione o tipo de caso de uso: **Outro** (Other) > **Empresa** (Business).
5. Defina um nome para o app (ex: `Koala Automation Engine`) e informe seu e-mail de contato.

### Passo 2: Adicionar os Produtos Necessários
No painel do aplicativo criado, adicione os seguintes produtos:
1. **API do Graph do Instagram** (Instagram Graph API).
2. **Login do Facebook para Empresas** (Facebook Login for Business).

### Passo 3: Permissões Necessárias (Scopes)
Para a publicação de Reels e leitura de métricas básicas, o token do usuário deve ter as seguintes permissões autorizadas:
- `instagram_basic`: Leitura de informações básicas do perfil.
- `instagram_content_publish`: **Permissão obrigatória** para criar containers de mídia e publicar Reels.
- `pages_show_list`: Permite localizar as Páginas do Facebook vinculadas.
- `pages_read_engagement`: Permite obter dados de engajamento da página vinculada.

---

## 3. Obtenção do ID da Conta e Tokens de Acesso

### 3.1 Obter o `INSTAGRAM_ACCOUNT_ID` (ID Numérico)
O ID da conta do Instagram não é o @username, mas sim um identificador numérico único fornecido pela Meta.

Para consultar o ID numérico:
1. Acesse a ferramenta [Graph API Explorer](https://developers.facebook.com/tools/explorer/).
2. Selecione seu aplicativo e gere um User Token com as permissões acima.
3. No campo da consulta GET, execute:
   ```http
   GET me/accounts?fields=name,instagram_business_account{id,username}
   ```
4. A resposta conterá o ID numérico dentro de `instagram_business_account`:
   ```json
   {
     "data": [
       {
         "name": "Minha Página",
         "instagram_business_account": {
           "id": "17841400000000000",
           "username": "koalatenis_"
         }
       }
     ]
   }
   ```
5. Guarde o valor do campo `"id"` (`17841400000000000`). Este é o seu `INSTAGRAM_ACCOUNT_ID`.

### 3.2 Gerar Token de Longa Duração (Long-Lived Access Token — 60 dias)
Tokens gerados no Graph API Explorer duram apenas 1 ou 2 horas. Para automação em servidor, é necessário convertê-lo em um token de longa duração:

Execute a chamada HTTP:
```bash
curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=SEU_APP_ID&\
client_secret=SEU_APP_SECRET&\
fb_exchange_token=TOKEN_DE_CURTA_DURACAO"
```

A resposta devolverá um novo token que dura **60 dias**:
```json
{
  "access_token": "EAA...",
  "token_type": "bearer",
  "expires_in": 5184000
}
```

> 💡 **Opção Corporativa Definitiva (Token Sem Expiração):**  
> Para não precisar renovar o token a cada 60 dias, o usuário pode cadastrar um **Usuário do Sistema (System User)** dentro do Meta Business Manager (Configurações do Negócio), conceder acesso à Página e à conta do Instagram e gerar um token de acesso permanente.

---

## 4. Como Configurar no Sistema (Onboarding do Usuário)

O usuário deve configurar suas credenciais de forma declarativa e segura.

### 4.1 Configuração via `.env`
No arquivo `.env` (baseado no `.env.example`):
```ini
# Configurações Globais da Meta
INSTAGRAM_APP_ID="123456789012345"
INSTAGRAM_APP_SECRET="abcdef0123456789abcdef0123456789"

# Perfil Principal
INSTAGRAM_ACCOUNT_ID="17841400000000000"
INSTAGRAM_ACCESS_TOKEN="EAAG..."
```

### 4.2 Configuração por Perfil (`profiles/<perfil>.json`)
Caso o usuário opere múltiplos perfis (ex: Koala Tênis e outro canal), cada perfil aponta para sua respectiva variável de ambiente:
```json
{
  "id": "koalatenis",
  "name": "Koala Tênis",
  "platform": "instagram",
  "username": "@koalatenis_",
  "instagram_account_id_env": "INSTAGRAM_ACCOUNT_ID_KOALATENIS",
  "instagram_token_env": "INSTAGRAM_ACCESS_TOKEN_KOALATENIS"
}
```

---

## 5. Como o Sistema Conecta e Publica (Fluxo Técnico da Automação)

A publicação na Meta Graph API segue um processo estruturado em containers assíncronos:

```text
┌───────────────────────────┐
│   Mídia Gerada (IA/FFmpeg) │ (Armazenada localmente em data/videos ou data/media)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 1. Servidor de Mídia      │ (Disponibiliza o asset via URL HTTP/S pública ou proxy)
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 2. Criação do Container   │ POST graph.facebook.com/v21.0/{account_id}/media
│    específico do Formato  │ 
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 3. Polling de Status      │ GET graph.facebook.com/v21.0/{container_id}?fields=status_code
│    do Container           │ Aguarda status: "FINISHED"
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 4. Publicação Efetiva     │ POST graph.facebook.com/v21.0/{account_id}/media_publish
│    no Perfil              │ Retorna: { "id": "instagram_media_id" }
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│ 5. Notificação Telegram   │ Confirma publicação e salva no banco SQLite.
└───────────────────────────┘
```

### 5.1 Especificidades por Formato

1. **🎬 Reels (Vídeo 9:16):**
   - Cria container com `media_type="REELS"`, `video_url="<url>"`, `caption="<legenda>"`.
   - Requer polling de processamento até `FINISHED`.

2. **📱 Stories (Vertical 9:16):**
   - Cria container com `media_type="STORIES"`, `image_url="<url>"`.
   - Publicação direta após criação do container.

3. **🖼️ Feed Post (Quadrado 1:1):**
   - Cria container com `image_url="<url>"`, `caption="<legenda rica>"`.
   - Publicação com `creation_id`.

4. **📚 Carrossel (Multi-Slides 1:1):**
   - **Etapa 1:** Cria um container individual para cada slide com `image_url="<slide_url>"`, `is_carousel_item="true"`.
   - **Etapa 2:** Cria o container pai com `media_type="CAROUSEL"`, `children="id1,id2,id3,..."` e `caption="<legenda>"`.
   - **Etapa 3:** Publica o container pai na Meta Graph API. No Telegram, o usuário recebe a pré-visualização completa em formato de álbum (`sendMediaGroup`).

---

## 6. Ferramenta de Teste de Conexão (Validador de Acesso)

O sistema deve disponibilizar um script e rota de teste para que o usuário verifique se o acesso está funcionando sem precisar gerar um vídeo:

```bash
# Execução no container ou ambiente local:
python -m app.instagram.validator --profile koalatenis
```

**Resultado esperado:**
```text
[OK] Conectando à Meta Graph API v21.0...
[OK] Token válido. Validade restante: 58 dias.
[OK] Conta Instagram localizada: @koalatenis_ (ID: 17841400000000000).
[OK] Permissões verificadas: instagram_basic, instagram_content_publish.
[SUCCESS] Conexão com o Instagram validada com sucesso! Pronto para automatizar.
```

---

## 7. Tratamento de Erros Comuns da Meta

| Código de Erro Meta | Significado | Ação do Sistema / Usuário |
| :--- | :--- | :--- |
| `OAuthException` (190) | Token de acesso expirou ou foi revogado. | Notificar no Telegram para renovação do token. |
| `100` (`Invalid parameter`) | Formato de vídeo ou proporção inválida. | Validar que o FFmpeg gerou exatamente MP4 H.264/AAC em 9:16. |
| `2207001` (`Media upload timeout`) | O vídeo demorou a ser baixado pela Meta. | Verificar velocidade de upload e disponibilidade da URL do vídeo. |
| `2207027` (`Container not ready`) | Tentativa de publicar antes do container terminar o processamento. | Manter loop de polling até `FINISHED` antes do `media_publish`. |
| `Application does not have permission` | O app não tem a permissão `instagram_content_publish`. | Solicitar ao usuário habilitar os escopos corretos no Meta for Developers. |
