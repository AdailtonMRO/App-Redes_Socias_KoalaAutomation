"""
Testes Unitários do Gerenciador de Perfis
"""
import pytest
from app.profiles.manager import ProfileManager, ProfileSchema


def test_list_and_get_profiles():
    manager = ProfileManager()
    profiles = manager.list_profiles()
    assert isinstance(profiles, list)
    assert len(profiles) >= 1

    koala = manager.get_profile("koalatenis")
    assert koala is not None
    assert koala.name == "Koala Tênis"
    assert koala.username == "@koalatenis_"
    assert "tênis" in koala.niche
