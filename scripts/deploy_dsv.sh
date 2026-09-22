#!/bin/bash
# ============================================================
# KOALA AUTOMATION — Script de Deploy v2.0.0 no HomeLab
# Servidor: 10.0.0.119 | Ambiente: DSV | Porta: 8082
# Executar DENTRO do servidor após `ssh usuario@10.0.0.119`
# ============================================================
set -e

# --- Configurações ---
PROJECT_DIR="/app/social-media-koala"   # ← Ajuste se necessário
CONTAINER_NAME="social-media-koala-dsv"
PORT="8082"
IMAGE_TAG="2.0.0-dsv"
REGISTRY="localhost:5000"

echo "==================================================="
echo "🐨 KOALA AUTOMATION — Deploy v2.0.0 (DSV)"
echo "==================================================="

# 1. Navegar até o projeto
cd "${PROJECT_DIR}"
echo "✅ Diretório: $(pwd)"

# 2. Verificar branch e atualizar código
echo ""
echo "📥 Atualizando código do GitHub..."
git fetch origin
git pull origin main
echo "✅ Branch: $(git branch --show-current) | Commit: $(git rev-parse --short HEAD)"
echo "✅ Versão: $(cat VERSION)"

# 3. Backup dos dados antes do deploy
echo ""
echo "💾 Fazendo backup dos dados..."
BACKUP_TS=$(date +%Y%m%d_%H%M%S)
tar -czf "/tmp/backup_data_${BACKUP_TS}.tar.gz" data/ 2>/dev/null || echo "⚠️  Sem data/ para backup"
tar -czf "/tmp/backup_profiles_${BACKUP_TS}.tar.gz" profiles/ 2>/dev/null || echo "⚠️  Sem profiles/ para backup"
echo "✅ Backup salvo em /tmp/"

# 4. Garantir rede Docker
echo ""
echo "🔗 Verificando rede Docker..."
docker network inspect koala-network > /dev/null 2>&1 || docker network create koala-network
echo "✅ Rede koala-network OK"

# 5. Build da imagem
echo ""
echo "🏗️  Construindo imagem Docker..."
docker build \
  -t "${REGISTRY}/social-media-koala:${IMAGE_TAG}" \
  -t "${REGISTRY}/social-media-koala:dsv-latest" \
  .
echo "✅ Build concluído: ${IMAGE_TAG}"

# 6. Push para registry local
echo ""
echo "📤 Enviando para registry local..."
docker push "${REGISTRY}/social-media-koala:${IMAGE_TAG}"
docker push "${REGISTRY}/social-media-koala:dsv-latest"

# 7. Parar e remover container antigo
echo ""
echo "♻️  Substituindo container..."
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# 8. Subir novo container
docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  --network koala-network \
  -p "${PORT}:8080" \
  -e ENVIRONMENT=DSV \
  -e APP_PORT=8080 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/profiles:/app/profiles" \
  --env-file .env \
  "${REGISTRY}/social-media-koala:${IMAGE_TAG}"

echo "✅ Container '${CONTAINER_NAME}' iniciado na porta ${PORT}"

# 9. Healthcheck
echo ""
echo "🏥 Aguardando healthcheck..."
sleep 15

SUCCESS=false
for i in $(seq 1 12); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/health" || true)
  if [ "$STATUS" = "200" ]; then
    echo "✅ Healthcheck OK! (tentativa ${i}/12)"
    SUCCESS=true
    break
  fi
  echo "⏳ Tentativa ${i}/12: HTTP ${STATUS}. Aguardando 5s..."
  sleep 5
done

echo ""
if [ "$SUCCESS" = true ]; then
  echo "==================================================="
  echo "🎉 DEPLOY v2.0.0 CONCLUÍDO COM SUCESSO!"
  echo "==================================================="
  echo "🌐 Painel Web:   http://10.0.0.119:8082"
  echo "🏥 Health:       http://10.0.0.119:${PORT}/health"
  echo "📋 Logs:         docker logs -f ${CONTAINER_NAME}"
  echo ""
  # Resposta do /health
  echo "--- /health response ---"
  curl -s "http://localhost:${PORT}/health" | python3 -m json.tool 2>/dev/null || curl -s "http://localhost:${PORT}/health"
else
  echo "❌ HEALTHCHECK FALHOU! Verificando logs..."
  docker logs "${CONTAINER_NAME}" --tail 50
  exit 1
fi
