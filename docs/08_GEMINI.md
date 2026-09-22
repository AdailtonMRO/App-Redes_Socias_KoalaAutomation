# 🤖 Integração com Google Gemini AI (Geração de Roteiros)

> **Documento Técnico:** `docs/08_GEMINI.md`  
> **Versão:** 1.0.0

---

## 1. Visão Geral
O Google Gemini é responsável por atuar como o estrategista criativo da automação. Ele recebe o perfil da marca, o nicho, o tom de voz e as regras de restrição ("avoid"), devolvendo uma estrutura **JSON estritamente validada**.

---

## 2. Modelos Homologados
- **`gemini-2.5-flash`** *(Padrão Recomendado)*: Altíssima velocidade de inferência (2 a 4 segundos), excelente aderência a JSON estruturado e custo mínimo.
- **`gemini-2.5-pro`**: Modelo com maior capacidade de raciocínio, indicado para campanhas mais complexas.

---

## 3. Estrutura do Schema de Saída (Pydantic)
```json
{
  "title": "3 Segredos do Saque Perfeito",
  "hook": "Você ainda perde pontos de graça no saque? Pare agora!",
  "objective": "engajamento",
  "script": "Texto corrido da narrativa...",
  "scenes": [
    {
      "scene_number": 1,
      "duration": 4,
      "description": "Close dinâmico do movimento de preparação",
      "visual_prompt": "Cinematic vertical 9:16 shot of athlete preparing tennis serve...",
      "narration": "Você ainda comete esse erro clássico?"
    }
  ],
  "caption": "Legenda formatada com emojis e parágrafos curtos...",
  "hashtags": ["#tenis", "#tennis", "#dicas"],
  "cta": "Siga para mais dicas no link da bio!"
}
```

---

## 4. Fallback e Mock Generator
Para garantir que o fluxo de ponta a ponta e a esteira de CI/CD possam ser testados a qualquer momento sem consumo de cotas de API, o módulo `app/ai/gemini.py` possui um gerador sintético de alta fidelidade que entra em ação automaticamente caso a chave não esteja configurada ou ocorra instabilidade temporária na rede.
