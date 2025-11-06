import os
import sys
import subprocess
import torch
import torchaudio
from pathlib import Path

# Проверка аргумента
if len(sys.argv) < 2:
    print("Usage: python3 analyze_audio.py <input_audio.wav>")
    sys.exit(1)

input_file = Path(sys.argv[1])
if not input_file.exists():
    print(f"❌ Файл {input_file} не найден")
    sys.exit(1)

output_dir = Path("output_audio")
output_dir.mkdir(exist_ok=True)
enhanced_file = output_dir / "enhanced_output.wav"

# ---------- Downloading packages ----------
def install(package):
    subprocess.run([sys.executable, "-m", "pip", "install", package, "-q", "--disable-pip-version-check"])

required_packages = ["torch", "torchaudio", "git+https://github.com/facebookresearch/denoiser.git", "openai-whisper", "ffmpeg-python"]
for pkg in required_packages:
    try:
        __import__(pkg.split('[')[0].split('=')[0].split('+')[-1])
    except ImportError:
        print(f"Installing packages {pkg} ...")
        install(pkg)

import denoiser
import whisper
import ffmpeg

print("\nОбработка аудио моделью Denoiser...")
model = denoiser.pretrained.dns64().cuda() if torch.cuda.is_available() else denoiser.pretrained.dns64()
wav, sr = torchaudio.load(str(input_file))
wav = wav.mean(0, keepdim=True)  # моно
wav = wav.to(model.device)
enhanced = model.enhance(wav, sr)[0].cpu()
torchaudio.save(str(enhanced_file), enhanced, sr)
print(f"Очищенный файл сохранён: {enhanced_file}")

print("\n Распознаём речь через Whisper...")
model_w = whisper.load_model("small")
result = model_w.transcribe(str(enhanced_file), language="ru")

text = result.get("text", "").strip()
if text:
    print(f"\nРаспознанная речь:\n{text}")
else:
    print("\nРечь не обнаружена возможно сигнал слабый.")

print("\nSaved to:  ./output_audio/")
