"""
Gerenciador de Perfis de Redes Sociais
Lê, valida, salva e sincroniza os perfis declarativos em JSON (profiles/*.json).
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.config import get_settings

settings = get_settings()


class ProfileSchema(BaseModel):
    id: str = Field(..., description="Identificador único (slug) do perfil")
    name: str = Field(..., description="Nome de exibição da marca/perfil")
    platform: str = Field("instagram", description="Plataforma de rede social")
    username: str = Field(..., description="Nome de usuário (@perfil)")
    instagram_account_id: Optional[str] = Field(None, description="ID numérico específico da conta do Instagram")
    instagram_access_token: Optional[str] = Field(None, description="Token de acesso específico da conta (opcional, usa global se vazio)")
    instagram_account_id_env: Optional[str] = Field("INSTAGRAM_ACCOUNT_ID", description="Variável de ambiente com o ID da conta")
    instagram_token_env: Optional[str] = Field("INSTAGRAM_ACCESS_TOKEN", description="Variável de ambiente com o token de acesso")
    niche: List[str] = Field(default_factory=list, description="Lista de tópicos/nichos de atuação")
    audience: List[str] = Field(default_factory=list, description="Público-alvo principal")
    tone: List[str] = Field(default_factory=list, description="Tom de voz da comunicação")
    objectives: List[str] = Field(default_factory=list, description="Objetivos do perfil")
    video_format: str = Field("9:16", description="Proporção do vídeo (padrão 9:16 para Reels)")
    preferred_duration: str = Field("20-30s", description="Duração média preferida")
    cta: str = Field("Siga o perfil para mais dicas!", description="Chamada para ação padrão")
    avoid: List[str] = Field(default_factory=list, description="O que a IA deve evitar alucinar ou mencionar")
    logo_path: Optional[str] = Field(None, description="Caminho do arquivo local da logomarca (PNG/JPG)")
    logo_url: Optional[str] = Field(None, description="URL pública ou caminho web da logomarca")


class ProfileManager:
    def __init__(self, profiles_dir: Optional[str] = None):
        self.profiles_dir = Path(profiles_dir or settings.PROFILES_DIR)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> List[Dict[str, Any]]:
        profiles = []
        for file in self.profiles_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    profiles.append(data)
            except Exception as e:
                print(f"[WARN] Erro ao ler perfil {file}: {e}")
        return profiles

    def get_profile(self, profile_id: str) -> Optional[ProfileSchema]:
        file_path = self.profiles_dir / f"{profile_id}.json"
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return ProfileSchema(**data)

    def save_profile(self, profile: ProfileSchema) -> Path:
        file_path = self.profiles_dir / f"{profile.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile.model_dump(), f, indent=2, ensure_ascii=False)
        return file_path

    def delete_profile(self, profile_id: str) -> bool:
        file_path = self.profiles_dir / f"{profile_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
