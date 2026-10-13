#!/usr/bin/env python3
"""Build a portable media bundle, NOT a native OpenCut project."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent
IMAGES = [
    ("vice-city.jpg", "https://www.rockstargames.com/VI/_next/static/media/Vice_City_01.135x56yoeu.6t.jpg"),
    ("jason.jpg", "https://www.rockstargames.com/VI/_next/static/media/Jason_Duval_01.07m377xeb6jhq.jpg"),
    ("lucia.jpg", "https://www.rockstargames.com/VI/_next/static/media/Lucia_Caminos_01.0a7yqvewctkfp.jpg"),
]


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)], check=True, capture_output=True, text=True,
        timeout=30,
    )
    return json.loads(result.stdout)


def narration_duration(info: dict) -> float:
    streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if len(streams) != 1:
        raise ValueError("Expected exactly one audio stream.")
    duration = float(info["format"]["duration"])
    if not math.isfinite(duration) or not 0.1 <= duration <= 300:
        raise ValueError("Narration duration must be between 0.1 and 300 seconds.")
    return duration


def plan_images(duration: float, names: list[str]) -> list[dict]:
    if not names or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Positive duration and images are required.")
    boundaries = [round(duration * i / len(names), 6) for i in range(len(names) + 1)]
    return [
        {"file": "images/" + name, "start_seconds": boundaries[i],
         "end_seconds": boundaries[i + 1]}
        for i, name in enumerate(names)
    ]


def download_image(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "ViceScope/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if not response.headers.get_content_type().startswith("image/"):
            raise ValueError("Official image URL did not return an image.")
        data = response.read(20 * 1024 * 1024 + 1)
    if not data or len(data) > 20 * 1024 * 1024:
        raise ValueError("Image is empty or exceeds 20 MiB.")
    destination.write_bytes(data)
    info = probe(destination)
    stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if not stream or stream.get("width", 0) <= 0 or stream.get("height", 0) <= 0:
        raise ValueError("Downloaded image cannot be decoded.")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(destination), "-frames:v", "1",
         "-f", "null", "-"], check=True, timeout=30,
    )


def build() -> Path:
    narration = os.environ.get("NARRATION_TEXT", "").strip()
    title = os.environ.get("VIDEO_TITLE", "").strip()
    subtitle = os.environ.get("VIDEO_SUBTITLE", "").strip()
    if not narration or len(narration) > 1200 or not title or len(title) > 50 or len(subtitle) > 70:
        raise ValueError("Missing or oversized editorial text.")
    audio = ROOT / "assets/narration.wav"
    narration_duration(probe(audio))
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    target = output / "ViceScope-OpenCut-Media.zip"
    with tempfile.TemporaryDirectory(prefix="vicescope-opencut-") as directory:
        folder = Path(directory)
        (folder / "images").mkdir()
        normalized = folder / "narration.wav"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(audio),
             "-map", "0:a:0", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
             "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(normalized)],
            check=True, timeout=120,
        )
        info = probe(normalized)
        duration = narration_duration(info)
        stream = next(s for s in info["streams"] if s["codec_type"] == "audio")
        if stream["sample_rate"] != "48000" or stream["channels"] != 2:
            raise ValueError("Audio format validation failed.")
        for name, url in IMAGES:
            download_image(url, folder / "images" / name)
        (folder / "script.txt").write_text(narration + "\n", encoding="utf-8")
        files = sorted(p for p in folder.rglob("*") if p.is_file())
        manifest = {
            "schema": "vicescope.media-bundle.v1",
            "native_opencut_project": False,
            "title": title, "subtitle": subtitle,
            "canvas": {"width": 1080, "height": 1920, "fps": 30},
            "duration_seconds": duration,
            "narration": {"file": "narration.wav", "script": "script.txt",
                          "language": "en-US", "start_seconds": 0},
            "images": plan_images(duration, [name for name, _ in IMAGES]),
            "sources": [{"file": "images/" + name, "url": url} for name, url in IMAGES],
            "captions": {"method": "OpenCut transcription", "generated": False},
            "review": {"human_approved": False, "publication_allowed": False},
            "files": [
                {"path": p.relative_to(folder).as_posix(), "bytes": p.stat().st_size,
                 "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in files
            ],
        }
        (folder / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (folder / "LEIA-ME.txt").write_text(
            "ViceScope — pacote de mídias para edição\n\n"
            "Este ZIP não é um projeto nativo do OpenCut. Extraia antes de importar.\n"
            "1. Importe narration.wav e as três imagens da pasta images.\n"
            "2. Coloque a voz desde o início na faixa de áudio.\n"
            "3. Organize as imagens na faixa visual conforme manifest.json.\n"
            "4. Use a transcrição do OpenCut para gerar legendas e revise contra script.txt.\n"
            "5. Use formato vertical 1080x1920 e exporte com áudio incluído.\n\n"
            "O manifest descreve o plano de montagem para uma futura integração.\n"
            "Não cole o JSON como projeto no site público.\n"
            "As imagens são oficiais do GTA VI; não confirmam a notícia narrada.\n"
            "O roteiro padrão é um teste de formato, não uma notícia.\n"
            "Publicação continua dependendo de revisão factual e aprovação humana.\n",
            encoding="utf-8",
        )
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(folder).as_posix())
        with zipfile.ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity validation failed.")
            saved = json.loads(archive.read("manifest.json"))
            for entry in saved["files"]:
                data = archive.read(entry["path"])
                if len(data) != entry["bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
                    raise ValueError("Bundle file integrity validation failed.")
    print(json.dumps({"bundle": str(target), "duration_seconds": duration,
                      "images": len(IMAGES), "native_opencut_project": False}))
    return target


if __name__ == "__main__":
    build()
