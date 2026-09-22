# 📡 Content Radar — Motor Proativo de Inteligência de Conteúdo

> **Documento Técnico:** `docs/18_CONTENT_RADAR.md`  
> **Versão:** 1.0.0  
> **Status:** Ativo / Homologado

---

## 1. Visão Geral e Objetivo de Negócio

O **Content Radar** é o módulo de inteligência proativa do sistema. Em vez de depender apenas de temas inseridos manualmente pelo operador, o Radar atua como um jornalista esportivo e diretor de arte automatizado:

1. **Monitora fontes externas** (Trends, Circuito Profissional ATP/ITF e Notícias técnicas).
2. **Normaliza os achados** em um contrato padrão de dados (`ResearchItem`).
3. **Filtra e pontua através do Gemini** cruzando as notícias com o DNA do perfil.
4. **Cria a ponte de conversão DIY:** O foco central do perfil `@koalatenis_` é **fazer com que o praticante monte sua própria máquina lançadora de bolas**. Assim, as notícias e dados de performance funcionam como atrativo de topo de funil para educar e incentivar a construção da máquina.
5. **Notifica o operador via Telegram** com briefing matinal e botões interativos de ação direta (`[CRIAR REEL]`).

---

## 2. Arquitetura de Adapters Desacoplados

Nenhuma fonte externa fica acoplada ao núcleo do sistema. Todas as fontes herdam da interface abstrata `SourceAdapter` e produzem objetos normalizados `ResearchItem`.

```text
                    CONTENT RADAR (radar.py)
                               │
             ┌─────────────────┼─────────────────┐
             ↓                 ↓                 ↓
     GoogleTrendsAdapter   ATPAdapter        ITFAdapter / NewsAdapter
      (pytrends + RSS)     (Feed RSS)        (Feed RSS / Google News)
             │                 │                 │
             └─────────────────┼─────────────────┘
                               ↓
                   NORMALIZAÇÃO (ResearchItem)
                               ↓
                  OPPORTUNITY SCORER (Gemini)
                 (Ângulo Tênis -> Máquina DIY)
                               ↓
                    TELEGRAM BRIEFING MATINAL
```

---

## 3. Contrato de Dados Normalizado (`ResearchItem`)

Independentemente de a notícia vir do Google Trends, de um feed RSS da ATP ou do Google News, ela é convertida neste schema unificado:

```json
{
  "id": "uuid4",
  "source_name": "ATP",
  "source_type": "official",
  "title": "Lehecka upsets Shelton; Rune wins return in Davis Cup",
  "url": "https://www.atptour.com/en/news/...",
  "summary": "Resumo do acontecimento ou métrica de tendência...",
  "published_at": "2026-09-22T10:00:00Z",
  "collected_at": "2026-09-22T11:00:00Z",
  "language": "en",
  "country": "US",
  "topics": ["tennis", "davis-cup", "atp"],
  "raw_metrics": {
    "trend_value": 100,
    "growth_rate": "+150%"
  }
}
```

---

## 4. Fontes Verificadas e Política Anti-Alucinação

Seguindo a regra de **não inventar endpoints fictícios**, todas as fontes foram testadas e validadas:

| Fonte | Provedor Principal | Método de Acesso | Fallback Resiliente |
| :--- | :--- | :--- | :--- |
| **Google Trends** | `GoogleTrendsAdapter` | `pytrends` (queries em alta, volume temporal, termos relacionados) | RSS oficial de tendências (`https://trends.google.com/trending/rss?geo=BR`) |
| **ATP Tour** | `ATPAdapter` | Feed RSS oficial indexado via Google News (`site:atptour.com`) | Cache local de últimas notícias |
| **ITF Tennis** | `ITFAdapter` | Feed RSS de regulamentos e torneios (`site:itftennis.com`) | Cache local |
| **News / Tech / DIY** | `NewsAdapter` | RSS estruturado segmentado em: *tennis ball machine*, *tennis training*, *tennis robotics* | RSS esportivo geral |

---

## 5. Os 6 Pilares de Conteúdo do Koala Tênis

O filtro de inteligência avalia cada informação sob 6 lentes temáticas:

1. 🎾 **Tênis Profissional:** Grandes torneios, ATP/WTA, jogos históricos, estatísticas de atletas.
2. 🧠 **Aprendizado e Biomecânica:** Saque, forehand, backhand, postura, tempo de bola e repetição.
3. ⚙️ **Tecnologia Esportiva:** Velocidade de bola, sensores, cordas, raquetes e máquinas de bolas.
4. 🔧 **DIY & Engenharia (Pilar Central):** Como funciona o motor de duas rodas, controle de RPM, ângulos de propulsão, impressão 3D e eletrônica da máquina de bolas.
5. 🔥 **Tendências (Trends):** O que tenistas amadores estão buscando no Google no momento.
6. 😂 **Conteúdo Leve / Entretenimento:** Situações que todo tenista vive, frustrações comuns na quadra, humor inteligente.

---

## 6. Cronograma Diário Automatizado (Cron Schedule)

O ciclo de vida diário do Radar opera nos seguintes marcos temporais:

```text
[06:00] ───> Coleta Assíncrona dos Adapters (Trends, ATP, ITF, News)
                │
[06:15] ───> Filtragem & Pontuação pelo Gemini (Conexão com Máquina DIY)
                │
[07:30] ───> Notificação no Telegram do Briefing Matinal ("RADAR KOALA")
                │
[Sob Demanda] ───> Clique em [CRIAR REEL] gera publicação completa
```

---

## 7. Formato da Notificação no Telegram

Exemplo da mensagem entregue às 07:30 no Telegram:

```text
🎾 RADAR KOALA — 22/09/2026
Encontrei 8 oportunidades relevantes nas últimas 24h:

🔥 3 Assuntos em alta no Google Trends
📚 3 Conteúdos educativos / técnicos
⚙️ 2 Oportunidades diretas para o Projeto Máquina DIY

💡 DESTAQUE DO DIA:
🎬 "Por que os profissionais treinam devolução de saque com repetição milimétrica?"
• Fonte: ATP Tour & Google Trends
• Ângulo Koala: Demonstrar como a máquina lançadora DIY permite simular exatamente a mesma velocidade e efeito dos tenistas profissionais.
• Formato Sugerido: Reel de 30s

[ 🚀 CRIAR REEL DESTE TEMA ]
[ 📋 VER DEMAIS OPORTUNIDADES ]
```
