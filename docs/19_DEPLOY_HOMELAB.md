# 🖥️ Guia Completo de Deploy no HomeLab (homelabaws · 10.0.0.119)

> **Documento:** `19_DEPLOY_HOMELAB.md`
> **Versão:** 1.0.0
> **Data:** 2026-09-22
> **Aplica-se a:** Todos os deploys no servidor HomeLab do projeto Koala Automation

---

## 1. Visão Geral da Infraestrutura

| Item | Valor |
|------|-------|
| Servidor | homelabaws |
| IP da rede interna | 10.0.0.119 |
| Registry Docker local | localhost:5000 |
| Porta DSV (Desenvolvimento) | 8082 |
| Porta HMG (Homologação) | 8083 |
| Porta PRD (Produção) | 8084 |
| Porta do painel web | 8085 |
| Container name DSV | social-media-koala-dsv |
| Container name HMG | social-media-koala-hmg |
| Container name PRD | social-media-koala-prd |
| Rede Docker | koala-network |
| Endpoint de saúde | /health |

**Mapeamento de ambientes:**

```
DSV (Desenvolvimento)  -> branch: feature/*, fix/*, etc. -> Pipeline: snapshot.yml
HMG (Homologação)      -> branch: PR para main          -> Pipeline: start-release.yml
PRD (Produção)         -> branch: main (após merge)     -> Pipeline: finish-release.yml
```

---

## 2. Deploy Automático via GitHub Actions (Método Preferencial)

### Pré-requisitos para deploy automático

O deploy automático funciona somente se o **runner self-hosted** estiver ativo no servidor.

**Verificar status do runner:**
```bash
# No servidor HomeLab
ssh usuario@10.0.0.119
sudo systemctl status actions.runner.*.service
```

**Se o runner estiver parado, iniciar:**
```bash
sudo systemctl start actions.runner.*.service
sudo systemctl enable actions.runner.*.service  # para auto-start
```

### Fluxo de deploy automático por ambiente

#### DSV — Deploy de Desenvolvimento (Snapshot)
**Trigger:** Push em qualquer branch que NÃO seja `main`

```bash
# No computador de desenvolvimento
git checkout -b feature/minha-nova-funcionalidade
git add .
git commit -m "feat(módulo): descrição da funcionalidade"
git push origin feature/minha-nova-funcionalidade
```

**O que acontece automaticamente:**
1. GitHub Actions detecta o push
2. `snapshot.yml` é disparado no runner self-hosted
3. Imagem é construída com tag `{VERSION}-{RUN_NUMBER}-SNAPSHOT`
4. Imagem é enviada para `localhost:5000`
5. Container DSV é recriado na porta 8082
6. Healthcheck valida `/health` (12 tentativas × 5s = máx 60s)
7. Sumário é gerado na aba Actions do GitHub

**Validar o deploy:**
```bash
curl http://10.0.0.119:8082/health
# Esperado: {"status": "ok"} (HTTP 200)
```

---

#### HMG — Deploy de Homologação (Release Candidate)
**Trigger:** Abertura ou atualização de Pull Request para `main`

```bash
# Abrir PR via GitHub UI ou CLI
gh pr create --title "feat: nome da funcionalidade" --base main
```

**O que acontece automaticamente:**
1. `start-release.yml` é disparado
2. Imagem é construída com tag `{VERSION}-RC.{RUN_NUMBER}`
3. Deploy é feito em DSV (8082) E HMG (8083)
4. Healthchecks são validados em ambos

**Validar o deploy:**
```bash
curl http://10.0.0.119:8082/health  # DSV
curl http://10.0.0.119:8083/health  # HMG
```

---

#### PRD — Deploy de Produção (Release Final)
**Trigger:** Merge do Pull Request na branch `main`

**O que acontece automaticamente:**
1. `finish-release.yml` é disparado
2. Tag Git `v{VERSION}` é criada
3. Imagem é construída com tag `{VERSION}` e `latest`
4. Deploy é feito em PRD (8084)
5. Healthcheck valida PRD

**Validar o deploy:**
```bash
curl http://10.0.0.119:8084/health  # PRD
```

---

## 3. Deploy Manual (Fallback — Sem Runner Ativo)

Use este procedimento quando:
- O runner self-hosted estiver offline
- Houver urgência e a pipeline estiver lenta
- Precisar fazer hotfix direto em produção

### Passo 1 — Conectar ao servidor

```bash
ssh usuario@10.0.0.119
```

### Passo 2 — Navegar até o diretório do projeto

```bash
cd /caminho/do/projeto/social-media-koala
# Confirmar o local correto:
ls -la | grep Dockerfile
```

### Passo 3 — Atualizar o código

```bash
# Verificar branch atual
git status
git branch

# Baixar as últimas alterações
git fetch origin
git pull origin [nome-da-branch]

# Confirmar a versão
cat VERSION
```

### Passo 4 — Verificar as variáveis de ambiente

```bash
# Conferir se o .env está configurado corretamente
cat .env | grep -v "=" | head -20   # listar apenas chaves (sem valores)

# NÃO execute: cat .env (exibe valores secretos no terminal)
```

### Passo 5 — Build da imagem Docker

```bash
# Ler versão atual
VERSION=$(cat VERSION | tr -d '\r\n')
AMBIENTE="dsv"   # ou hmg, prd

# Build da imagem
docker build \
  -t localhost:5000/social-media-koala:${VERSION}-manual-${AMBIENTE} \
  -t localhost:5000/social-media-koala:${AMBIENTE}-latest \
  .

# Verificar se o build foi bem-sucedido
docker images | grep social-media-koala
```

### Passo 6 — Garantir a rede Docker

```bash
docker network inspect koala-network > /dev/null 2>&1 || \
  docker network create koala-network
```

### Passo 7 — Subir o container

#### Para DSV (porta 8082):
```bash
docker rm -f social-media-koala-dsv || true

docker run -d \
  --name social-media-koala-dsv \
  --restart unless-stopped \
  --network koala-network \
  -p 8082:8080 \
  -e ENVIRONMENT=DSV \
  -e APP_PORT=8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/profiles:/app/profiles \
  --env-file .env \
  localhost:5000/social-media-koala:${VERSION}-manual-dsv
```

#### Para HMG (porta 8083):
```bash
docker rm -f social-media-koala-hmg || true

docker run -d \
  --name social-media-koala-hmg \
  --restart unless-stopped \
  --network koala-network \
  -p 8083:8080 \
  -e ENVIRONMENT=HMG \
  -e APP_PORT=8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/profiles:/app/profiles \
  --env-file .env \
  localhost:5000/social-media-koala:${VERSION}-manual-hmg
```

#### Para PRD (porta 8084):
```bash
docker rm -f social-media-koala-prd || true

docker run -d \
  --name social-media-koala-prd \
  --restart unless-stopped \
  --network koala-network \
  -p 8084:8080 \
  -e ENVIRONMENT=PRD \
  -e APP_PORT=8080 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/profiles:/app/profiles \
  --env-file .env \
  localhost:5000/social-media-koala:${VERSION}-manual-prd
```

### Passo 8 — Validar o deploy (Healthcheck)

```bash
# Aguardar inicialização (30 segundos)
sleep 30

# Checar saúde do container
PORTA=8082   # Ajustar conforme o ambiente

for i in {1..12}; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORTA}/health || true)
  if [ "$STATUS" -eq 200 ]; then
    echo "✅ Healthcheck OK! Container está saudável."
    break
  fi
  echo "⏳ Tentativa $i/12: Status ${STATUS}. Aguardando 5s..."
  sleep 5
done

if [ "$STATUS" -ne 200 ]; then
  echo "❌ Healthcheck FALHOU! Verificar logs:"
  docker logs social-media-koala-dsv --tail 50
fi
```

### Passo 9 — Verificar logs do container

```bash
# Logs em tempo real
docker logs -f social-media-koala-dsv

# Últimas 100 linhas
docker logs social-media-koala-dsv --tail 100

# Com timestamps
docker logs social-media-koala-dsv --timestamps
```

---

## 4. Operações de Manutenção

### Reiniciar um container sem rebuild

```bash
docker restart social-media-koala-dsv
```

### Parar um container

```bash
docker stop social-media-koala-dsv
```

### Ver status de todos os containers do projeto

```bash
docker ps --filter "name=social-media-koala" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Limpar imagens antigas (liberação de disco)

```bash
# Listar imagens do projeto
docker images | grep social-media-koala

# Remover imagens não usadas por nenhum container
docker image prune -f

# Remover imagem específica
docker rmi localhost:5000/social-media-koala:[TAG]
```

### Acessar o shell do container em execução

```bash
docker exec -it social-media-koala-dsv /bin/bash
```

### Backup dos volumes antes de deploy

```bash
# Backup dos dados antes de qualquer deploy em PRD
tar -czf backup_data_$(date +%Y%m%d_%H%M%S).tar.gz data/
tar -czf backup_profiles_$(date +%Y%m%d_%H%M%S).tar.gz profiles/
```

---

## 5. Rollback de Versão

### Rollback automático via GitHub Actions

Usar o workflow `redeploy.yml` via `workflow_dispatch` no GitHub:
1. Acessar o repositório no GitHub
2. Ir em Actions → "Redeploy Controlado"
3. Clicar em "Run workflow"
4. Selecionar a versão de rollback e o ambiente
5. Confirmar e monitorar a execução

### Rollback manual

```bash
# Listar versões disponíveis no registry local
curl http://localhost:5000/v2/social-media-koala/tags/list | python3 -m json.tool

# Fazer rollback para uma versão específica
VERSION_ROLLBACK="1.0.5"
PORTA=8084
CONTAINER_NAME="social-media-koala-prd"

docker rm -f ${CONTAINER_NAME} || true

docker run -d \
  --name ${CONTAINER_NAME} \
  --restart unless-stopped \
  --network koala-network \
  -p ${PORTA}:8080 \
  -e ENVIRONMENT=PRD \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/profiles:/app/profiles \
  localhost:5000/social-media-koala:${VERSION_ROLLBACK}

echo "Rollback para ${VERSION_ROLLBACK} realizado. Validando..."
sleep 15
curl http://localhost:${PORTA}/health
```

---

## 6. Diagnóstico de Problemas Comuns

| Sintoma | Diagnóstico | Solução |
|---------|-------------|---------|
| Container não inicia | `docker logs social-media-koala-dsv` | Ver seção 7 (Erros comuns) |
| /health retorna 500 | Variável de ambiente faltando | Conferir .env e recriar container |
| /health não responde (timeout) | Container na porta errada | Verificar `docker ps` e mapeamento de portas |
| Build falha com "no space left" | Disco cheio | `docker system prune -f` e `docker volume prune -f` |
| Runner offline | GitHub Actions mostrando "queued" indefinidamente | `sudo systemctl start actions.runner.*.service` |
| Imagem não encontrada no registry | Push não foi feito | Executar `docker push localhost:5000/...` manualmente |

---

## 7. Checklist de Deploy em Produção (PRD)

Antes de qualquer merge para `main` e deploy em PRD, confirmar:

```
[ ] Todos os testes passam (CI verde)
[ ] Healthcheck em HMG está OK há pelo menos 10 minutos
[ ] CHANGELOG está atualizado com a versão correta
[ ] .env.example está atualizado se novas variáveis foram adicionadas
[ ] VERSION foi incrementado corretamente
[ ] Backup de data/ e profiles/ foi realizado no servidor
[ ] Equipe foi notificada sobre o deploy
[ ] Janela de manutenção (se necessária) está comunicada
[ ] Plano de rollback está documentado e testado
```

---

## 8. Monitoramento Pós-Deploy

Após qualquer deploy em PRD, monitorar por pelo menos 15 minutos:

```bash
# Verificar saúde continuamente
watch -n 10 'curl -s http://localhost:8084/health'

# Monitorar logs em tempo real
docker logs -f social-media-koala-prd 2>&1 | grep -E "ERROR|WARNING|CRITICAL"

# Verificar uso de recursos
docker stats social-media-koala-prd --no-stream
```

---

*Última revisão: 2026-09-22*
*Responsável: Engenharia Koala Automation*
