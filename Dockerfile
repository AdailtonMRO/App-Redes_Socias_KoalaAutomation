# Imagem base Python 3.12 slim
FROM python:3.12-slim

# Metadados
LABEL maintainer="Koala Automation Team"
LABEL description="Instagram AI V1 — Social Media Automation"

# Evita criação de arquivos .pyc e buffer de stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema: FFmpeg nativo para processamento de vídeo e curl para healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root por segurança
RUN useradd -m -u 1000 appuser

# Diretório de trabalho
WORKDIR /app

# Instalação de dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Criação das pastas de dados e permissões
RUN mkdir -p /app/data/videos /app/data/temp /app/data/thumbnails /app/profiles /app/logs \
    && chown -R appuser:appuser /app

# Copia código da aplicação
COPY --chown=appuser:appuser . .

# Alterna para o usuário não-root
USER appuser

# Porta interna padrão do container
EXPOSE 8080

# Healthcheck interno do Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
