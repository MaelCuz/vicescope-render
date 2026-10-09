#!/usr/bin/env python3
"""Generate ViceScope narration with Kokoro on the GitHub Actions runner."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "assets" / "narration.wav"

text = os.environ.get("NARRATION_TEXT", "").strip()
voice = os.environ.get("KOKORO_VOICE", "am_adam").strip() or "am_adam"
speed = float(os.environ.get("KOKORO_SPEED", "1.08"))

if not text:
    raise SystemExit("NARRATION_TEXT is empty.")

if not 0.75 <= speed <= 1.35:
    raise SystemExit("KOKORO_SPEED must be between 0.75 and 1.35.")

print(f"Generating narration: voice={voice}, speed={speed}, characters={len(text)}")

pipeline = KPipeline(lang_code="a")
chunks = []

for _, _, audio in pipeline(text, voice=voice, speed=speed):
    if audio is not None and len(audio):
        chunks.append(np.asarray(audio, dtype=np.float32))

if not chunks:
    raise SystemExit("Kokoro did not generate any audio.")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
waveform = np.concatenate(chunks)
sf.write(OUTPUT, waveform, 24000, subtype="PCM_16")

duration = len(waveform) / 24000
print(f"Narration saved to {OUTPUT} ({duration:.2f}s)")
