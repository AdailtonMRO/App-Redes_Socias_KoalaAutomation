# 🤖 Integração com Google Gemini AI (Geração de Roteiros)

> **Documento Técnico:** `docs/08_GEMINI.md`  
> **Versão:** 1.0.0

---

## 1. Visão Geral
O Google Gemini é responsável por atuar como o estrategista criativo da automação. Ele recebe o perfil da marca, o nicho, o tom de voz e as regras de restrição ("avoid"), devolvendo uma estrutura **JSON estritamente validada**.

---

## 2. Modelos Homologados
- **`gemini-3.6-flash`** *(Padrão Recomendado)*: Altíssima velocidade de inferência (1 a 3 segundos), total aderência a JSON estruturado tipado.
- **`gemini-3.1-flash-lite`**: Modelo ultra econômico para otimização de prompts e tarefas de alta escala.
- **`gemini-3.1-flash-lite-image`**: Geração de imagens fotográficas 1K com suporte a `responseModalities: ["IMAGE"]`.
- **`veo-3.1-lite-generate-preview`**: Geração de vídeos cinematográficos 9:16 nativos (4 a 8 segundos).

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

---

## 5. Esteira Multimodal de Menor Custo Operacional (Cost-Effective Pipeline)
Implementada em `app/ai/multimodal_pipeline.py` com o script executável `scripts/run_multimodal_pipeline.py`:
- **Etapa 1 (Otimização de Prompt):** `gemini-3.1-flash-lite` (US$ 0,0001 / execução) gera prompts estáticos e dinâmicos de física de movimento.
- **Etapa 2 (Imagem Base 1K):** `gemini-3.1-flash-lite-image` / `imagen-3.0` (US$ 0,0336 / geração) cria o frame âncora em 1024x1024 ou 9:16.
- **Etapa 3 (Vídeo Image-to-Video):** `veo-3.1-lite-generate-preview` / `veo-2.0` (US$ 0,05 / segundo = US$ 0,20 para 4 segundos) anima o frame base prevenindo distorções.
- **Custo Total Estimado por Reel:** **~US$ 0,2337 (~R$ 1,36)** por publicação de vídeo vertical completa.
