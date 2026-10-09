#!/usr/bin/env python3
"""Render a vertical ViceScope video from dynamic narration and metadata."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
AUDIO = ROOT / "assets" / "narration.wav"
TEXT_DIR = ROOT / ".render_text"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

OUT.mkdir(exist_ok=True)
TEXT_DIR.mkdir(exist_ok=True)

if not AUDIO.exists():
    raise SystemExit("Missing assets/narration.wav")


def run(*args: object) -> None:
    command = [str(arg) for arg in args]
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    value = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(value)


def clean_text(value: str, fallback: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return (value or fallback)[:limit]


def caption_chunks(text: str, words_per_chunk: int = 6) -> list[str]:
    words = re.sub(r"\s+", " ", text).strip().split()
    if not words:
        return ["FOLLOW VICESCOPE FOR MORE"]

    chunks = [
        " ".join(words[index : index + words_per_chunk])
        for index in range(0, len(words), words_per_chunk)
    ]
    return chunks[:12]


def write_text_file(name: str, value: str) -> Path:
    path = TEXT_DIR / name
    path.write_text(value, encoding="utf-8")
    return path


def ffmpeg_path(path: Path) -> str:
    return str(path).replace("\\", "/").replace(":", "\\:")


duration = probe_duration(AUDIO)
narration = clean_text(
    os.environ.get("NARRATION_TEXT", ""),
    "Rockstar Games just revealed another detail that could change GTA Six.",
    1200,
)
title = clean_text(os.environ.get("VIDEO_TITLE", ""), "GTA VI NEWS", 50).upper()
subtitle = clean_text(
    os.environ.get("VIDEO_SUBTITLE", ""),
    "THE DETAIL EVERYONE MISSED",
    70,
).upper()
captions = caption_chunks(narration)

title_file = write_text_file("title.txt", title)
subtitle_file = write_text_file("subtitle.txt", subtitle)

filters = [
    "drawbox=x=70:y=210:w=940:h=8:color=0xFFCC00:t=fill",
    (
        f"drawtext=fontfile={FONT_BOLD}:textfile='{ffmpeg_path(title_file)}':"
        "fontcolor=white:fontsize=92:x=(w-text_w)/2:y=290"
    ),
    (
        f"drawtext=fontfile={FONT_BOLD}:textfile='{ffmpeg_path(subtitle_file)}':"
        "fontcolor=0xFFCC00:fontsize=46:x=(w-text_w)/2:y=430"
    ),
    "drawbox=x=70:y=560:w=940:h=530:color=0x16213E@0.92:t=fill",
    "drawbox=x=90:y=580:w=900:h=490:color=0x0F3460@0.55:t=fill",
    (
        f"drawtext=fontfile={FONT_BOLD}:text='VICESCOPE':fontcolor=white@0.16:"
        "fontsize=125:x=(w-text_w)/2:y=760"
    ),
]

segment = duration / len(captions)
for index, caption in enumerate(captions):
    start = index * segment
    end = duration if index == len(captions) - 1 else (index + 1) * segment
    caption_file = write_text_file(f"caption_{index:02d}.txt", caption.upper())
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:textfile='{ffmpeg_path(caption_file)}':"
        "fontcolor=white:fontsize=58:x=(w-text_w)/2:y=1280:"
        "box=1:boxcolor=black@0.72:boxborderw=28:"
        f"enable='between(t,{start:.3f},{end:.3f})'"
    )

filters.extend(
    [
        (
            f"drawtext=fontfile={FONT_REGULAR}:text='@VICESCOPE':"
            "fontcolor=white@0.85:fontsize=34:x=70:y=1775"
        ),
        (
            f"drawtext=fontfile={FONT_REGULAR}:text='EDITORIAL NEWS':"
            "fontcolor=white@0.65:fontsize=30:x=w-text_w-70:y=1778"
        ),
        (
            f"drawbox=x=70:y=1840:w='(w-140)*t/{duration:.6f}':"
            "h=10:color=0xFFCC00:t=fill"
        ),
        "format=yuv420p",
    ]
)

video_filter = ",".join(filters)
output = OUT / "vicescope-video.mp4"

run(
    "ffmpeg",
    "-hide_banner",
    "-loglevel",
    "error",
    "-y",
    "-f",
    "lavfi",
    "-i",
    f"color=c=0x0B1020:s=1080x1920:r=30:d={duration:.3f}",
    "-i",
    AUDIO,
    "-filter_complex",
    f"[0:v]{video_filter}[v]",
    "-map",
    "[v]",
    "-map",
    "1:a",
    "-c:v",
    "libx264",
    "-preset",
    "veryfast",
    "-crf",
    "25",
    "-c:a",
    "aac",
    "-b:a",
    "128k",
    "-t",
    str(duration),
    "-movflags",
    "+faststart",
    output,
)

print(
    json.dumps(
        {
            "output": str(output),
            "duration": round(duration, 3),
            "title": title,
            "subtitle": subtitle,
            "caption_count": len(captions),
        }
    )
)
