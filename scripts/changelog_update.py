#!/usr/bin/env python3
"""
changelog_update.py — Script de atualização padronizada do CHANGELOG
Projeto: Koala Automation — Social Media Automation

Uso:
  python scripts/changelog_update.py \
    --version 1.2.0 \
    --type feat \
    --module "app/research" \
    --description "Adicionar adapter para Google Trends"

Tipos permitidos:
  feat      → Novas Funcionalidades
  fix       → Correções de Bugs
  improve   → Melhorias Técnicas
  docs      → Documentação
  security  → Segurança
  breaking  → Breaking Changes
  removed   → Removidos
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

CHANGELOG_PATH = Path(__file__).parent.parent / "docs" / "17_CHANGELOG.md"

SECTION_TITLES = {
    "feat": "🚀 Novas Funcionalidades",
    "fix": "🐛 Correções de Bugs",
    "improve": "🔧 Melhorias Técnicas",
    "docs": "📚 Documentação",
    "security": "🛡️ Segurança",
    "breaking": "⚠️ Breaking Changes",
    "removed": "🗑️ Removidos",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Atualiza o CHANGELOG com uma nova entrada padronizada."
    )
    parser.add_argument("--version", required=True, help="Versão semântica (ex: 1.2.0)")
    parser.add_argument(
        "--type",
        required=True,
        choices=list(SECTION_TITLES.keys()),
        help="Tipo da mudança",
    )
    parser.add_argument(
        "--module",
        required=True,
        help="Módulo ou arquivo afetado (ex: app/research, Dockerfile)",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Descrição objetiva da mudança em português",
    )
    return parser.parse_args()


def read_changelog():
    if not CHANGELOG_PATH.exists():
        print(f"ERRO: Arquivo CHANGELOG não encontrado em {CHANGELOG_PATH}")
        sys.exit(1)
    return CHANGELOG_PATH.read_text(encoding="utf-8")


def write_changelog(content: str):
    CHANGELOG_PATH.write_text(content, encoding="utf-8")


def build_entry_line(module: str, description: str) -> str:
    return f"- {description} (`{module}`)"


def update_changelog(version: str, change_type: str, module: str, description: str):
    content = read_changelog()
    today = date.today().strftime("%Y-%m-%d")
    version_header = f"## [{version}] — {today}"
    section_title = f"### {SECTION_TITLES[change_type]}"
    new_entry_line = build_entry_line(module, description)

    # Verificar se a versão já existe no changelog
    if version_header in content:
        # Adicionar entrada à seção existente
        if section_title in content:
            # Seção já existe — inserir nova linha após o título
            insert_after = f"{section_title}\n"
            content = content.replace(
                insert_after,
                f"{insert_after}{new_entry_line}\n",
                1  # Apenas a primeira ocorrência
            )
            print(f"✅ Entrada adicionada à seção '{section_title}' da versão {version}.")
        else:
            # Seção não existe — criar seção antes do próximo ## ou no final do bloco da versão
            next_version_marker = "\n## ["
            if next_version_marker in content:
                insert_point = content.find(next_version_marker, content.find(version_header))
                new_section = f"\n{section_title}\n{new_entry_line}\n"
                content = content[:insert_point] + new_section + content[insert_point:]
            else:
                # Última versão no arquivo
                content = content.rstrip() + f"\n\n{section_title}\n{new_entry_line}\n"
            print(f"✅ Nova seção '{section_title}' criada na versão {version}.")
    else:
        # Versão nova — inserir após o cabeçalho e antes da versão anterior
        new_block = (
            f"{version_header}\n\n"
            f"{section_title}\n"
            f"{new_entry_line}\n\n"
            f"---\n\n"
        )
        # Inserir após a linha de introdução (primeiro bloco de texto)
        first_separator = content.find("---\n\n")
        if first_separator != -1:
            insert_point = first_separator + len("---\n\n")
            content = content[:insert_point] + new_block + content[insert_point:]
        else:
            # Fallback: inserir no início após o título
            content = content + f"\n\n{new_block}"
        print(f"✅ Nova entrada de versão {version} criada no CHANGELOG.")

    write_changelog(content)
    print(f"📄 CHANGELOG atualizado em: {CHANGELOG_PATH}")


def main():
    args = parse_args()

    print(f"\n📝 Atualizando CHANGELOG...")
    print(f"   Versão:     {args.version}")
    print(f"   Tipo:       {args.type} → {SECTION_TITLES[args.type]}")
    print(f"   Módulo:     {args.module}")
    print(f"   Descrição:  {args.description}\n")

    update_changelog(
        version=args.version,
        change_type=args.type,
        module=args.module,
        description=args.description,
    )


if __name__ == "__main__":
    main()
