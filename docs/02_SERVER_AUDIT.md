# 🔍 Diagnóstico de Auditoria do Servidor (Fase 0)

> **Data da Auditoria:** 2026-09-21  
> **Servidor:** `homelabaws` (`10.0.0.119`)  
> **Usuário Operacional:** `executamais`  
> **Status:** Concluído com Sucesso

---

## 1. Dados do Sistema Operacional e Hardware
- **Sistema Operacional:** Ubuntu 26.04.1 LTS (GNU/Linux 7.0.0-31-generic x86_64)
- **Memória RAM:** 7.2 GiB Total | **Disponível:** 5.3 GiB (Uso: ~1.9 GiB)
- **Espaço em Disco:** 914 GB Total | **Livre:** 720 GB (Uso: 18%)
- **Docker Engine:** Versão 29.8.1 (Nativo via APT)
- **Docker Compose:** Versão 5.5.1 (Plugin Oficial)
- **Permissões Docker:** O usuário `executamais` opera `docker` e `docker compose` sem `sudo`.

---

## 2. Containers Existentes no Servidor (Home Labs)
| Container ID | Nome | Imagem | Porta Externa | Finalidade |
| :--- | :--- | :--- | :--- | :--- |
| `3cbabbb867a2` | `nextcloud` | `nextcloud:apache` | **`8080`** | Nuvem pessoal Nextcloud |
| `b7287422456b` | `excm-dsv` | `localhost:5000/a25031/excm:1.0.0-3-SNAPSHOT` | **`8082`** | Aplicação corporativa DSV |
| `36577244af47` | `excm-registry` | `registry:2` | **`5000`** | Registry Docker Local |
| `00ec08f2b6e0` | `excm-postgres`| `postgres:16-alpine` | `5432` | Banco PostgreSQL compartilhado |
| `dfc3fd9a07e2` | `excm-redis` | `redis:7-alpine` | `6379` | Cache Redis |
| `4ebcfd1aa64e` | `qbittorrent` | `linuxserver/qbittorrent` | `8081`, `6881` | Gerenciador de downloads |
| Outros | `sonarr`, `radarr`, `prowlarr`, `flaresolverr`, `ministack` | Diversas | Diversas | Multimídia / AWS local |

---

## 3. Decisão de Conflito de Portas (CRÍTICO)

> [!CAUTION]
> **Conflito de Porta Identificado:**  
> A porta padrão **`8080` já está em uso pelo container `nextcloud`**, e a porta **`8082` já está em uso pelo container `excm-dsv`**.
>
> **Decisão de Engenharia:**  
> Para não interromper nenhum serviço do servidor, o projeto **Instagram AI** utilizará a porta externa **`8085`** mapeada para a porta interna `8080` do container:
> ```yaml
> ports:
>   - "8085:8080"
> ```
> O painel web de configuração do usuário responderá em:  
> 👉 **`http://10.0.0.119:8085`**

---

## 4. Localização do Projeto no Servidor
- **Diretório Escolhido:** `/home/executamais/instagram-ai`
- **Rede Docker:** Rede isolada `koala-network` (bridge).
