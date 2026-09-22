# 📡 Content Radar — Motor Proativo de Inteligência de Conteúdo

> **Documento Técnico:** `docs/18_CONTENT_RADAR.md`  
> **Versão:** 1.4.0  
> **Status:** Ativo / Homologado

---

## 1. Visão Geral e Objetivo de Negócio

O **Content Radar** é o motor de inteligência e curadoria jornalística automatizada do ecossistema Koala Automation. Ele monitora em tempo real portais dedicados de tênis, grandes canais de esportes e fontes oficiais do esporte para alimentar a esteira de criação:

1. **Monitora 7 provedores de dados independentes** (TenisBrasil, Tenis News, Diário do Tênis, ge.globo, ESPN Brasil, UOL, WTA, CBT, ATP, ITF e Google Trends).
2. **Normaliza os achados** em um contrato padrão de dados (`ResearchItem`).
3. **Aplica memória dinâmica anti-repetição** para que atualizações e requisições consecutivas (`/radar`) sempre tragam conteúdos frescos e variados.
4. **Filtra e estrutura através do Gemini** extraindo a manchete magnética, resumo informativo e pontos-chave esportivos.
5. **Gera Stories Verticais Estáticos (9:16):** As matérias selecionadas são convertidas diretamente em imagens de Story de alto impacto visual (1080x1920) com card central de resumo e a **logomarca oficial do perfil posicionada no canto inferior direito**.
6. **Notifica o operador via Telegram** com briefing matinal e botões interativos de ação direta (`[NOTÍCIA 1..4]`, `[🔄 Atualizar Notícias]`).


---

## 2. Arquitetura de Adapters Desacoplados

Nenhuma fonte externa fica acoplada ao núcleo do sistema. Todas as fontes herdam da interface abstrata `SourceAdapter` e produzem objetos normalizados `ResearchItem`.

```text
                            CONTENT RADAR (radar.py)
                                        │
      ┌─────────────────────────────────┼─────────────────────────────────┐
      ↓                                 ↓                                 ↓
BrazilianTennisAdapter          SportsPortalsAdapter               WTAAndCBTAdapter
(TenisBrasil, TenisNews,         (ge.globo, ESPN Brasil,           (WTA, Bia Haddad,
 Diário do Tênis - Feeds)         UOL Esporte - RSS)                CBT, Juvenis)
      │                                 │                                 │
      ├─────────────────────────────────┼─────────────────────────────────┤
      ↓                                 ↓                                 ↓
 NewsAdapter                       ATPAdapter / ITFAdapter          GoogleTrendsAdapter
(Google News Aberto)              (ATP Tour / ITF Tennis)          (pytrends + RSS)
      │                                 │                                 │
      └─────────────────────────────────┼─────────────────────────────────┘
                                        ↓
                       NORMALIZAÇÃO & ANTI-SPAM (ResearchItem)
                                        ↓
                      MEMÓRIA ANTI-REPETIÇÃO DINÂMICA
                                        ↓
                         OPPORTUNITY SCORER (Gemini)
                        (Ângulo Tênis -> Máquina DIY)
                                        ↓
                         TELEGRAM BRIEFING INTERATIVO
```

---

## 3. Contrato de Dados Normalizado (`ResearchItem`)

Independentemente de a notícia vir do Google Trends, do TenisBrasil, do ge.globo ou da ATP, ela é convertida neste schema unificado:

```json
{
  "id": "uuid4",
  "source_name": "TenisBrasil (UOL)",
  "source_type": "specialized_news",
  "title": "João Fonseca supera rodada e acelera forehand a 160km/h",
  "url": "https://tenisbrasil.uol.com.br/...",
  "summary": "Resumo do acontecimento ou métrica de tendência...",
  "published_at": "2026-09-22T10:00:00Z",
  "collected_at": "2026-09-22T11:00:00Z",
  "language": "pt",
  "country": "BR",
  "topics": ["tennis", "joao_fonseca", "treinamento"],
  "raw_metrics": {
    "source_weight": 1.2,
    "outlet": "TenisBrasil (UOL)"
  }
}
```

---

## 4. Fontes Verificadas e Política Anti-Alucinação

Seguindo a regra de **não inventar endpoints fictícios**, todas as fontes foram testadas e validadas:

| Fonte | Provedor | Método de Acesso | Cobertura |
| :--- | :--- | :--- | :--- |
| **Portais Especializados BR** | `BrazilianTennisAdapter` | Feeds RSS nativos (TenisBrasil UOL, Tenis News, Diário do Tênis) | Circuito nacional, ATP/WTA, ranking de brasileiros e bastidores |
| **Grandes Portais de Esportes** | `SportsPortalsAdapter` | Google News RSS direcionado (`site:ge.globo.com`, `site:espn.com.br`, `site:uol.com.br/esporte`) | Repercussão em massa, transmissões e grandes reportagens |
| **WTA & CBT** | `WTAAndCBTAdapter` | Google News RSS segmentado | Tênis feminino (Bia Haddad, Stefani), base juvenil e Copa Davis |
| **Notícias Amplas** | `NewsAdapter` | Google News RSS dinâmico | Biomecânica, tecnologia de raquetes e treinamento esportivo |
| **Google Trends** | `GoogleTrendsAdapter` | `pytrends` + RSS oficial de tendências | Buscas em alta no Brasil e termos em ascensão |
| **ATP Tour** | `ATPAdapter` | Feed RSS de circuito | Resultados e estatísticas da ATP |
| **ITF Tennis** | `ITFAdapter` | Feed RSS de regulamentos e torneios | Circuito de transição e juvenil mundial |
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
