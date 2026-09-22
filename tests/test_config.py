"""
Testes Unitários da API de Configurações
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_config_masked():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "ENVIRONMENT" in data
    assert "TELEGRAM_BOT_TOKEN_SET" in data
    assert "INSTAGRAM_ACCESS_TOKEN_SET" in data
