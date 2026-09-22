"""
Cliente HTTP da Meta Graph API v21.0
Suporta teste de conta, criação de container de mídia para Reels, polling e publicação.
"""
from typing import Dict, Any, Optional, List
import httpx
from app.config import get_settings

settings = get_settings()


class MetaGraphClient:
    def __init__(self, access_token: Optional[str] = None, api_version: str = "v21.0"):
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    async def get_token_debug_info(self, input_token: Optional[str] = None) -> Dict[str, Any]:
        """Inspeciona um token para verificar validade, permissões e tempo de expiração."""
        token = input_token or self.access_token
        if not token:
            return {"valid": False, "error": "Token não configurado"}

        # Se houver App ID e App Secret, usa debug_token oficial da Meta
        if settings.INSTAGRAM_APP_ID and settings.INSTAGRAM_APP_SECRET:
            app_token = f"{settings.INSTAGRAM_APP_ID}|{settings.INSTAGRAM_APP_SECRET}"
            url = f"{self.base_url}/debug_token"
            params = {"input_token": token, "access_token": app_token}
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    return {
                        "valid": data.get("is_valid", False),
                        "scopes": data.get("scopes", []),
                        "expires_at": data.get("expires_at", 0),
                        "app_id": data.get("app_id"),
                        "type": data.get("type"),
                    }
                return {"valid": False, "error": resp.text}

        # Fallback sem App Secret: testa endpoint me?fields=id,name
        url = f"{self.base_url}/me"
        params = {"access_token": token, "fields": "id,name"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return {"valid": True, "data": resp.json()}
            return {"valid": False, "error": resp.text}

    async def get_instagram_account(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Consulta dados da conta profissional do Instagram."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        if not target_account or not self.access_token:
            return {"success": False, "error": "Account ID ou Access Token ausentes"}

        url = f"{self.base_url}/{target_account}"
        params = {
            "access_token": self.access_token,
            "fields": "id,username,name,profile_picture_url,followers_count",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return {"success": True, "account": resp.json()}
            return {"success": False, "status_code": resp.status_code, "error": resp.json()}

    async def create_reel_container(self, video_url: str, caption: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria o container assíncrono para publicação do Reel."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media"
        payload = {
            "access_token": self.access_token,
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "container_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    async def create_story_container(self, media_url: str, is_video: bool = False, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria container de mídia para Story do Instagram (9:16)."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media"
        payload = {
            "access_token": self.access_token,
            "media_type": "STORIES",
        }
        if is_video:
            payload["video_url"] = media_url
        else:
            payload["image_url"] = media_url

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "container_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    async def create_feed_post_container(self, image_url: str, caption: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria container de post de imagem tradicional para o Feed (1:1 ou 4:5)."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media"
        payload = {
            "access_token": self.access_token,
            "image_url": image_url,
            "caption": caption,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "container_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    async def create_carousel_item_container(self, image_url: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria container de um slide individual para compor um carrossel."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media"
        payload = {
            "access_token": self.access_token,
            "image_url": image_url,
            "is_carousel_item": "true",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "container_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    async def create_carousel_container(self, children_ids: List[str], caption: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Cria o container pai do Carrossel agregando todos os slides."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media"
        payload = {
            "access_token": self.access_token,
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "container_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    async def check_container_status(self, container_id: str) -> Dict[str, Any]:
        """Verifica o status de processamento do container de mídia."""
        url = f"{self.base_url}/{container_id}"
        params = {"access_token": self.access_token, "fields": "status_code"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return {"success": True, "status_code": resp.json().get("status_code")}
            return {"success": False, "error": resp.json()}

    async def publish_media(self, container_id: str, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Publica qualquer container (Reel, Story, Feed ou Carrossel) após estar pronto."""
        target_account = account_id or settings.INSTAGRAM_ACCOUNT_ID
        url = f"{self.base_url}/{target_account}/media_publish"
        payload = {
            "access_token": self.access_token,
            "creation_id": container_id,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, data=payload)
            if resp.status_code == 200:
                return {"success": True, "media_id": resp.json().get("id")}
            return {"success": False, "error": resp.json()}

    # Alias para compatibilidade
    publish_reel = publish_media
