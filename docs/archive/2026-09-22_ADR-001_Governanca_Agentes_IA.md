# [ADR-001] Adoção do padrão de governança de documentação e deploy automático para agentes de IA

> **Data:** 2026-09-22
> **Versão afetada:** 1.1.0 em diante
> **Autor:** Engenharia Koala Automation (via Agente IA)
> **Status:** Aceita

---

## Contexto

O projeto Social Media Automation (Koala Automation) utiliza agentes de IA para desenvolvimento
e manutenção do código. Identificou-se que, sem regras explícitas e vinculantes, os agentes
tendiam a:

1. Implementar funcionalidades sem atualizar a documentação correspondente
2. Não registrar mudanças no CHANGELOG de forma consistente
3. Não preparar instruções de deploy para o servidor HomeLab (10.0.0.119)
4. Deixar o arquivo VERSION desatualizado após mudanças

Isso criava divergência entre o código real e a documentação, além de dificultar o rastreamento
de versões no ambiente de produção.

---

## Decisão

Criar um sistema formal de governança para agentes de IA composto de:

1. **Arquivo de regras** em `.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md`
   → Carregado automaticamente por agentes compatíveis (Antigravity IDE, etc.)
   → Define 8 regras inegociáveis para toda e qualquer alteração

2. **Guia de deploy** em `docs/19_DEPLOY_HOMELAB.md`
   → Manual completo com instruções automáticas (CI/CD) e manuais (fallback)
   → Inclui troubleshooting, rollback e checklist PRD

3. **Scripts de automação** em `scripts/`
   → `changelog_update.py`: atualização padronizada do CHANGELOG via CLI
   → `pre_deploy_check.py`: validação automática antes de qualquer deploy

4. **Diretório de arquivo arquitetural** em `docs/archive/`
   → Registro imutável de decisões técnicas relevantes (ADRs)
   → Template padronizado em `docs/archive/TEMPLATE_ADR.md`

---

## Alternativas Consideradas

| Alternativa | Por que foi descartada |
|-------------|------------------------|
| Documentação apenas no README | Não específico o suficiente para agentes de IA; não é carregado automaticamente |
| Regras dentro do 00_REGRAS_E_DIRETRIZES.md existente | O arquivo já é extenso; misturar regras de negócio com regras de agentes reduziria clareza |
| Usar hooks de git (pre-commit) | Requer setup no ambiente do desenvolvedor; agentes de IA não sempre executam hooks locais |

---

## Impacto

### Módulos afetados
- `.agents/rules/` — Diretório criado com arquivo de regras para agentes
- `docs/19_DEPLOY_HOMELAB.md` — Novo documento de guia de deploy
- `docs/archive/` — Novo diretório de ADRs
- `scripts/changelog_update.py` — Novo script de automação
- `scripts/pre_deploy_check.py` — Novo script de validação
- `docs/00_INDEX.md` — Atualizado para referenciar novos documentos
- `docs/00_REGRAS_E_DIRETRIZES.md` — Seção 8 expandida

### Riscos identificados
- Agentes de IA que não suportam leitura automática de `.agents/rules/` podem não seguir
  as regras — Probabilidade: Média; Mitigação: O operador deve incluir referência às regras
  no início de cada sessão

### Plano de mitigação
- O operador deve verificar periodicamente (a cada 2 semanas) se os agentes estão seguindo
  as regras através do script `pre_deploy_check.py`
- O CHANGELOG é a fonte de verdade para auditoria de conformidade

---

## Referências

- `docs/00_REGRAS_E_DIRETRIZES.md` — Regras de engenharia do projeto
- `.agents/rules/AI_AGENTS_DOCUMENTATION_AND_DEPLOY.md` — Regras para agentes de IA
- `docs/19_DEPLOY_HOMELAB.md` — Guia de deploy
- Keep a Changelog: https://keepachangelog.com/
- Conventional Commits: https://www.conventionalcommits.org/
- ADR (Architecture Decision Records): https://adr.github.io/

---

> **NOTA:** Este arquivo é imutável após criação. Para rever esta decisão,
> criar um novo arquivo de ADR referenciando este como "Substituído por".
