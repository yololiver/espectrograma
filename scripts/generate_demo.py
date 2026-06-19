"""
Corre este script uma vez localmente para gerar o ficheiro de dados pré-computados
usado pela rota /demo.

Uso:
    python scripts/generate_demo.py <caminho_para_audio>

Exemplo:
    python scripts/generate_demo.py src/uploads/soundreality-intro-noise-131718.mp3

Gera:
    src/backend/static/demo/demo_result.json
"""
import sys
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from backend.services import process_audio_file, build_analysis_summary

def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/generate_demo.py <caminho_para_audio>")
        sys.exit(1)

    audio_path = sys.argv[1]
    if not os.path.exists(audio_path):
        print(f"Ficheiro não encontrado: {audio_path}")
        sys.exit(1)

    print(f"A processar: {audio_path}")
    spec_data = process_audio_file(audio_path)
    if not spec_data:
        print("Erro ao processar o ficheiro de áudio.")
        sys.exit(1)

    out_path = os.path.join(ROOT, "src", "backend", "static", "demo", "demo_result.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(spec_data, f, ensure_ascii=False)

    size_kb = os.path.getsize(out_path) / 1024
    print(f"Gravado em: {out_path} ({size_kb:.0f} KB)")
    print(f"Duração: {spec_data['duration']:.1f}s | Sample rate: {spec_data['sample_rate']} Hz")
    print(f"Ruído de fundo: {spec_data['background_noise']}")
    print(f"Eventos: {len(spec_data.get('events', []))}")

if __name__ == "__main__":
    main()
