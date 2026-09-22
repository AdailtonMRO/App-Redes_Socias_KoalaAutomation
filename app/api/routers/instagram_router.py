"""
Roteador para Testes e Diagnóstico do Instagram / Meta Graph API
Permite testar a conexão com 1 clique pela interface web.
"""
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.instagram.validator import InstagramValidator

router = APIRouter(prefix="/api/instagram", tags=["Instagram"])
validator = InstagramValidator()


class TestConnectionRequest(BaseModel):
    access_token: Optional[str] = None
    account_id: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None


@router.post("/test-connection")
async def test_instagram_connection(payload: TestConnectionRequest):
    """
    Testa a conectividade com a Meta Graph API.
    Se o payload estiver vazio, utiliza as credenciais configuradas no ambiente (.env).
    """
    result = await validator.validate_connection(
        access_token=payload.access_token,
        account_id=payload.account_id,
        app_id=payload.app_id,
        app_secret=payload.app_secret,
    )
    return result
