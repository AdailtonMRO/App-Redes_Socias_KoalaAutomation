#!/usr/bin/env python3
"""
Script de Exemplo da Esteira Multimodal de Menor Custo (Google AI Studio).
Executa as 3 etapas (Prompt -> Imagem 1K -> Vídeo 720p 4s) e calcula os custos.

Uso:
  python scripts/run_multimodal_pipeline.py --topic "Como treinar saque com máquina de bolas DIY"
"""
import argparse
import asyncio
import sys
from pathlib import Path

# Fix Windows console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Adiciona raiz do projeto ao path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.ai.multimodal_pipeline import MultimodalCostEffectivePipeline, calculate_pipeline_cost


async def main():
    parser = argparse.ArgumentParser(description="Executa esteira multimodal de menor custo.")
    parser.add_argument(
        "--topic",
        default="Treinamento de saque no tênis com máquina de bolas de alta rotação",
        help="Ideia ou tema do conteúdo",
    )
    parser.add_argument(
        "--project",
        default="demo_koala_pipeline",
        help="Nome da pasta de saída do projeto",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=4,
        help="Duração do vídeo em segundos (padrão 4s = US$ 0,20)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("🎬 KOALA AUTOMATION — ESTEIRA MULTIMODAL DE MENOR CUSTO")
    print("=" * 60)
    print(f"📌 Tema de Entrada: {args.topic}")
    print(f"⏱️ Duração do Vídeo: {args.duration}s")
    print("-" * 60)

    pipeline = MultimodalCostEffectivePipeline()
    result = await pipeline.run_full_pipeline(
        user_input=args.topic,
        project_name=args.project,
        aspect_ratio="9:16",
        video_duration_seconds=args.duration,
    )

    print("\n" + "=" * 60)
    print("📦 RESULTADOS DA EXECUÇÃO")
    print("=" * 60)
    if result.prompts:
        print(f"🪝 Gancho Social Media: {result.prompts.headline_hook}")
        print(f"🖼️ Prompt Imagem 1K:   {result.prompts.image_prompt[:90]}...")
        print(f"🎥 Prompt Movimento:    {result.prompts.video_motion_prompt[:90]}...")
    print(f"\n📁 Arquivo de Imagem:   {result.image_path}")
    print(f"📁 Arquivo de Vídeo MP4: {result.video_path}")
    print("-" * 60)
    print(f"💵 Custo Total Estimado: US$ {result.estimated_cost_usd:.4f}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
