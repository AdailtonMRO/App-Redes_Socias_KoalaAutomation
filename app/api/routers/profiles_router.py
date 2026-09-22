"""
Roteador CRUD de Perfis de Redes Sociais
Permite cadastrar, editar e remover múltiplos perfis na interface web.
"""
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.profiles.manager import ProfileManager, ProfileSchema
from app.database.database import get_db
from app.database.repository import ProfileRepository
from app.config import get_settings
import json

router = APIRouter(prefix="/api/profiles", tags=["Perfis"])
manager = ProfileManager()


@router.get("", response_model=List[Dict[str, Any]])
def list_profiles():
    """Lista todos os perfis cadastrados."""
    return manager.list_profiles()


@router.get("/{profile_id}")
def get_profile(profile_id: str):
    """Obtém detalhes de um perfil específico."""
    profile = manager.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return profile.model_dump()


@router.post("")
def save_profile(profile: ProfileSchema, db: Session = Depends(get_db)):
    """Cria ou atualiza um perfil em arquivo JSON e sincroniza no banco SQLite."""
    try:
        # Salva em profiles/<id>.json
        manager.save_profile(profile)

        # Sincroniza na tabela profiles do SQLite
        repo = ProfileRepository(db)
        repo.upsert(
            profile_id=profile.id,
            name=profile.name,
            username=profile.username,
            config_json=json.dumps(profile.model_dump(), ensure_ascii=False),
        )

        return {"success": True, "message": f"Perfil '{profile.name}' salvo com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar perfil: {str(e)}")


@router.delete("/{profile_id}")
def delete_profile(profile_id: str):
    """Exclui um perfil do sistema."""
    success = manager.delete_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return {"success": True, "message": f"Perfil '{profile_id}' removido com sucesso."}


@router.post("/{profile_id}/test-connection")
async def test_profile_connection(profile_id: str):
    """Testa a conexão com o Instagram especificamente para este perfil."""
    profile = manager.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    from app.instagram.validator import InstagramValidator
    from app.config import get_settings
    settings = get_settings()

    # Obtém token específico do perfil ou usa o global
    token = profile.instagram_access_token or settings.INSTAGRAM_ACCESS_TOKEN
    account_id = profile.instagram_account_id or settings.INSTAGRAM_ACCOUNT_ID

    validator = InstagramValidator()
    result = await validator.validate_connection(access_token=token, account_id=account_id)
    return result


@router.post("/{profile_id}/logo")
async def upload_profile_logo(profile_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Faz o upload e vincula a logomarca do perfil."""
    profile = manager.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")

    settings = get_settings()
    logos_dir = Path(settings.DATA_DIR) / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "logo.png").suffix.lower() or ".png"
    logo_filename = f"logo_{profile_id}{ext}"
    logo_path = logos_dir / logo_filename

    content = await file.read()
    with open(logo_path, "wb") as f:
        f.write(content)

    profile.logo_path = str(logo_path)
    profile.logo_url = f"/media/logos/{logo_filename}"
    manager.save_profile(profile)

    repo = ProfileRepository(db)
    repo.upsert(
        profile_id=profile.id,
        name=profile.name,
        username=profile.username,
        config_json=json.dumps(profile.model_dump(), ensure_ascii=False),
    )

    return {
        "success": True,
        "logo_path": str(logo_path),
        "logo_url": profile.logo_url,
        "message": f"Logomarca da marca '{profile.name}' enviada e vinculada com sucesso!",
    }

