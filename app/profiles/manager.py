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


class IdentitySchema(BaseModel):
    who_we_are: str = Field(default="", description="Quem somos (Posicionamento curto)")
    audience: List[str] = Field(default_factory=list, description="Para quem falamos (Público-alvo)")
    positioning: str = Field(default="", description="Posicionamento da marca")
    authority: str = Field(default="", description="Autoridade (Por que nos ouvir)")
    personality: str = Field(default="", description="Personalidade da marca")

class ContentSchema(BaseModel):
    pillars: List[str] = Field(default_factory=list, description="Pilares editoriais")
    subthemes: List[str] = Field(default_factory=list, description="Subtemas explorados")
    priority_topics: List[str] = Field(default_factory=list, description="Assuntos prioritários")
    secondary_topics: List[str] = Field(default_factory=list, description="Assuntos secundários")
    forbidden_topics: List[str] = Field(default_factory=list, description="Assuntos proibidos (O que evitar)")
    formats: List[str] = Field(default_factory=list, description="Formatos aceitos (Reels, Feed, etc)")

class BusinessSchema(BaseModel):
    products: List[str] = Field(default_factory=list, description="Produtos oferecidos")
    services: List[str] = Field(default_factory=list, description="Serviços oferecidos")
    offers: List[str] = Field(default_factory=list, description="Ofertas vigentes")
    objectives: List[str] = Field(default_factory=list, description="Objetivos de negócio (venda, engajamento)")
    ctas: List[str] = Field(default_factory=list, description="CTAs aceitos")

class StyleSchema(BaseModel):
    tone: List[str] = Field(default_factory=list, description="Tom de voz da comunicação")
    vocabulary: List[str] = Field(default_factory=list, description="Vocabulário específico (Jargões)")
    rhythm: str = Field(default="dinâmico", description="Ritmo da edição e locução")
    aesthetics: str = Field(default="", description="Estética visual")
    references: List[str] = Field(default_factory=list, description="Perfis ou canais de referência")

class StrategySchema(BaseModel):
    frequency: str = Field(default="diário", description="Frequência de postagem")
    pillar_proportion: str = Field(default="", description="Proporção ideal dos pilares")
    content_objectives: List[str] = Field(default_factory=list, description="Objetivos por tipo de conteúdo")
    funnel_stage: str = Field(default="TOFU", description="Estágio do funil predominante")

class ProfileSchema(BaseModel):
    id: str = Field(..., description="Identificador único (slug) do perfil")
    name: str = Field(..., description="Nome de exibição da marca/perfil")
    platform: str = Field("instagram", description="Plataforma de rede social")
    username: str = Field(..., description="Nome de usuário (@perfil)")
    instagram_account_id: Optional[str] = Field(None, description="ID numérico específico da conta do Instagram")
    instagram_access_token: Optional[str] = Field(None, description="Token de acesso específico da conta (opcional, usa global se vazio)")
    instagram_account_id_env: Optional[str] = Field("INSTAGRAM_ACCOUNT_ID", description="Variável de ambiente com o ID da conta")
    instagram_token_env: Optional[str] = Field("INSTAGRAM_ACCESS_TOKEN", description="Variável de ambiente com o token de acesso")
    logo_path: Optional[str] = Field(None, description="Caminho do arquivo local da logomarca (PNG/JPG)")
    logo_url: Optional[str] = Field(None, description="URL pública ou caminho web da logomarca")

    # Novos agrupamentos do Cérebro Editorial (Profile DNA)
    identity: IdentitySchema = Field(default_factory=IdentitySchema)
    content: ContentSchema = Field(default_factory=ContentSchema)
    business: BusinessSchema = Field(default_factory=BusinessSchema)
    style: StyleSchema = Field(default_factory=StyleSchema)
    strategy: StrategySchema = Field(default_factory=StrategySchema)


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
