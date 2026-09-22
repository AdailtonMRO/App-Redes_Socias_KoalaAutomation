"""
Serviço Validador de Conexão com o Instagram / Meta Graph API
Usado pela Interface Web e CLI para atestar que o usuário configurou o acesso corretamente.
"""
from typing import Dict, Any, Optional
from app.instagram.client import MetaGraphClient


class InstagramValidator:
    def __init__(self, client: Optional[MetaGraphClient] = None):
        self.client = client or MetaGraphClient()

    async def validate_connection(
        self,
        access_token: Optional[str] = None,
        account_id: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Executa bateria de testes de conectividade sem publicar nada."""
        client = MetaGraphClient(access_token=access_token) if access_token else self.client

        # 1. Verifica se credenciais foram fornecidas
        target_token = access_token or client.access_token
        target_account = account_id or self.client.access_token

        if not target_token:
            return {
                "success": False,
                "stage": "CREDENTIALS_CHECK",
                "message": "Token de Acesso (INSTAGRAM_ACCESS_TOKEN) não fornecido.",
                "remediation": "Gere um token de acesso na Meta for Developers e insira no campo de configuração.",
            }

        # 2. Testa debug_token ou chamada básica ao Graph API
        token_info = await client.get_token_debug_info(input_token=target_token)
        if not token_info.get("valid", False):
            return {
                "success": False,
                "stage": "TOKEN_VALIDATION",
                "message": f"Token inválido ou expirado. Detalhes: {token_info.get('error')}",
                "remediation": "Gere um novo User Token ou Long-Lived Token com validade de 60 dias.",
            }

        # 3. Testa acesso à conta profissional do Instagram
        if account_id:
            account_data = await client.get_instagram_account(account_id=account_id)
            if not account_data.get("success", False):
                err = account_data.get("error", {})
                return {
                    "success": False,
                    "stage": "ACCOUNT_ACCESS",
                    "message": f"Não foi possível acessar a conta ID {account_id}. Verifique se é uma conta Business/Creator.",
                    "details": err,
                    "remediation": "Confirme se o ID numérico é o instagram_business_account obtido via Graph API Explorer.",
                }
            acc = account_data.get("account", {})
            return {
                "success": True,
                "stage": "READY",
                "message": f"Conexão validada com sucesso para @{acc.get('username', 'usuario')} ({acc.get('name')})!",
                "account": acc,
                "token_info": token_info,
            }

        return {
            "success": True,
            "stage": "TOKEN_OK",
            "message": "Token de acesso válido! Informe o ID da Conta do Instagram para validação completa.",
            "token_info": token_info,
        }
