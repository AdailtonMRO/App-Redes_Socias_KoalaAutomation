#!/usr/bin/env python3
"""
pre_deploy_check.py — Verificação completa antes de qualquer deploy
Projeto: Koala Automation — Social Media Automation

Uso:
  python scripts/pre_deploy_check.py --env dsv
  python scripts/pre_deploy_check.py --env prd --strict

Retorna:
  0  → Todos os checks passaram (deploy pode prosseguir)
  1  → Um ou mais checks falharam (BLOQUEAR deploy)
"""

import argparse
import re
import sys

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

ROOT = Path(__file__).parent.parent

CHECKS = []
ERRORS = []
WARNINGS = []


def check(name: str, ok: bool, error_msg: str, is_critical: bool = True):
    status = "OK" if ok else ("ERRO" if is_critical else "AVISO")
    icon = "✅" if ok else ("❌" if is_critical else "⚠️")
    print(f"  {icon} [{status}] {name}")
    if not ok:
        if is_critical:
            ERRORS.append(f"{name}: {error_msg}")
        else:
            WARNINGS.append(f"{name}: {error_msg}")


def check_version_file():
    version_file = ROOT / "VERSION"
    if not version_file.exists():
        check("Arquivo VERSION existe", False, "Arquivo VERSION não encontrado na raiz")
        return
    content = version_file.read_text(encoding="utf-8").strip()
    semver_pattern = r"^\d+\.\d+\.\d+$"
    is_valid = bool(re.match(semver_pattern, content))
    check(f"VERSION contém SemVer válido ({content})", is_valid,
          f"Conteúdo inválido: '{content}'. Esperado: MAJOR.MINOR.PATCH")


def check_changelog():
    changelog = ROOT / "docs" / "17_CHANGELOG.md"
    if not changelog.exists():
        check("CHANGELOG existe", False, "docs/17_CHANGELOG.md não encontrado")
        return

    content = changelog.read_text(encoding="utf-8")
    version_file = ROOT / "VERSION"
    if version_file.exists():
        current_version = version_file.read_text(encoding="utf-8").strip()
        has_version = f"[{current_version}]" in content
        check(f"CHANGELOG contém entrada para versão {current_version}", has_version,
              f"Versão {current_version} não encontrada no CHANGELOG. Adicione a entrada.")


def check_env_example():
    env_file = ROOT / ".env"
    env_example = ROOT / ".env.example"

    if not env_example.exists():
        check(".env.example existe", False, ".env.example não encontrado")
        return

    if env_file.exists():
        env_keys = set()
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                env_keys.add(line.split("=")[0].strip())

        example_keys = set()
        for line in env_example.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                example_keys.add(line.split("=")[0].strip())

        missing_in_example = env_keys - example_keys
        if missing_in_example:
            check(".env.example está sincronizado com .env", False,
                  f"Chaves faltando no .env.example: {', '.join(sorted(missing_in_example))}")
        else:
            check(".env.example está sincronizado com .env", True, "")
    else:
        check(".env.example existe", True, "", is_critical=False)


def check_no_hardcoded_secrets():
    """Verifica se há credenciais hardcoded em arquivos Python"""
    secret_patterns = [
        r'["\']AIza[A-Za-z0-9_-]{35}["\']',  # Google API Key
        r'["\'][A-Za-z0-9]{64}["\']',          # Possible token (64 chars)
        r'password\s*=\s*["\'][^${}][^"\']+["\']',
        r'secret\s*=\s*["\'][^${}][^"\']+["\']',
    ]
    app_files = list((ROOT / "app").rglob("*.py")) if (ROOT / "app").exists() else []
    found_secrets = []

    for py_file in app_files:
        try:
            content = py_file.read_text(encoding="utf-8")
            for pattern in secret_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # Verificar se é apenas um exemplo ou comentário
                    for line in content.splitlines():
                        if re.search(pattern, line, re.IGNORECASE) and not line.strip().startswith("#"):
                            found_secrets.append(f"{py_file.relative_to(ROOT)}:{content.splitlines().index(line)+1}")
                            break
        except Exception:
            pass

    no_secrets = len(found_secrets) == 0
    check("Sem credenciais hardcoded no código", no_secrets,
          f"Possíveis credenciais encontradas em: {', '.join(found_secrets[:3])}")


def check_dockerfile():
    dockerfile = ROOT / "Dockerfile"
    check("Dockerfile existe", dockerfile.exists(), "Dockerfile não encontrado na raiz")


def check_required_docs():
    required_docs = [
        "docs/00_INDEX.md",
        "docs/17_CHANGELOG.md",
        "docs/19_DEPLOY_HOMELAB.md",
    ]
    for doc_path in required_docs:
        doc = ROOT / doc_path
        check(f"Documento {doc_path} existe", doc.exists(),
              f"{doc_path} não encontrado. Criar antes do deploy.",
              is_critical=False)


def check_index_updated():
    """Verifica se todos os arquivos em docs/ estão referenciados no INDEX"""
    index_file = ROOT / "docs" / "00_INDEX.md"
    if not index_file.exists():
        return
    index_content = index_file.read_text(encoding="utf-8")
    docs_files = [f.name for f in (ROOT / "docs").glob("*.md") if f.name != "00_INDEX.md"]
    missing_from_index = [f for f in docs_files if f not in index_content]
    ok = len(missing_from_index) == 0
    check("Todos os docs/ estão referenciados no INDEX", ok,
          f"Arquivos não referenciados: {', '.join(missing_from_index)}",
          is_critical=False)


def main():
    parser = argparse.ArgumentParser(description="Verificação pré-deploy do projeto Koala Automation")
    parser.add_argument("--env", choices=["dsv", "hmg", "prd"], default="dsv",
                        help="Ambiente de destino")
    parser.add_argument("--strict", action="store_true",
                        help="Tratar avisos como erros")
    args = parser.parse_args()

    print(f"\n🔍 Verificação Pré-Deploy — Ambiente: {args.env.upper()}")
    print("=" * 60)

    check_version_file()
    check_changelog()
    check_env_example()
    check_no_hardcoded_secrets()
    check_dockerfile()
    check_required_docs()
    check_index_updated()

    print("=" * 60)

    if WARNINGS:
        print(f"\n⚠️  {len(WARNINGS)} aviso(s):")
        for w in WARNINGS:
            print(f"   • {w}")

    if ERRORS:
        print(f"\n❌ {len(ERRORS)} erro(s) crítico(s) encontrado(s):")
        for e in ERRORS:
            print(f"   • {e}")
        print("\n🚫 DEPLOY BLOQUEADO. Corrija os erros acima antes de prosseguir.\n")
        sys.exit(1)
    elif WARNINGS and args.strict:
        print("\n🚫 DEPLOY BLOQUEADO (modo --strict). Corrija os avisos acima.\n")
        sys.exit(1)
    else:
        print(f"\n✅ Todos os checks passaram! Deploy em {args.env.upper()} pode prosseguir.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
