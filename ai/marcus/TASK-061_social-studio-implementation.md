# TASK-061 — Social Studio Pipeline: Full Implementation Spec
**Assigned to:** Marcus
**Status:** done
**Completed:** 2026-06-01
**Priority:** critical — highest effort task
**Depends on:** TASK-060 (architecture research)
**Context:** This is the build document. TASK-060 answered what to build and why. This document answers exactly how to build it — every module, every function signature, every API call, every edge case. Claude reads this and writes code from it directly. No interpretation required.

---

## Table of Contents
1. [Project Structure and File Layout](#1-project-structure-and-file-layout)
2. [Module: `djinn.brands` — Config and DB Layer](#2-module-djinnbrands--config-and-db-layer)
3. [Module: `djinn.media.ingest` — iCloud → Salomon Intake](#3-module-djinnmediaingest--icloud--salomon-intake)
4. [Module: `djinn.media.reel` — Video Processing Pipeline](#4-module-djinnmediareel--video-processing-pipeline)
5. [Module: `djinn.media.transcribe` — faster-whisper Integration](#5-module-djinnmediatranscribe--faster-whisper-integration)
6. [Module: `djinn.media.caption` — Ollama Caption Generation](#6-module-djinnmediacaption--ollama-caption-generation)
7. [Module: `djinn.publish.meta` — Instagram + Facebook Graph API](#7-module-djinnpublishmeta--instagram--facebook-graph-api)
8. [Module: `djinn.publish.youtube` — YouTube Data API v3](#8-module-djinnpublishyoutube--youtube-data-api-v3)
9. [Module: `djinn.publish.x` — X/Twitter v2 + v1.1 Media](#9-module-djinnpublishx--xtwitter-v2--v11-media)
10. [Module: `djinn.scheduler` — Publish Queue and systemd Timer](#10-module-djinnscheduler--publish-queue-and-systemd-timer)
11. [Module: `djinn.tokens` — Token Lifecycle and Auto-Refresh](#11-module-djinntokens--token-lifecycle-and-auto-refresh)
12. [CLI Entry Points — `djinn` Command Group](#12-cli-entry-points--djinn-command-group)
13. [Hosting: Publicly Accessible Video URL for Meta](#13-hosting-publicly-accessible-video-url-for-meta)
14. [Environment Files and Secrets Layout](#14-environment-files-and-secrets-layout)
15. [Error Handling Patterns and Retry Logic](#15-error-handling-patterns-and-retry-logic)
16. [Full End-to-End Run Sequence](#16-full-end-to-end-run-sequence)
17. [Installation and First-Run Checklist](#17-installation-and-first-run-checklist)
18. [Open Items and Known Gotchas](#18-open-items-and-known-gotchas)

---

## 1. Project Structure and File Layout

### Python Package Layout
```
~/projects/djinn-social/
├── pyproject.toml
├── README.md
├── djinn/
│   ├── __init__.py
│   ├── brands.py           # BrandConfig, DB helpers, season/week/episode math
│   ├── media/
│   │   ├── __init__.py
│   │   ├── ingest.py       # HEIC/HEVC conversion, manifest creation
│   │   ├── reel.py         # ffmpeg 9:16 pipeline, cover extraction
│   │   ├── transcribe.py   # faster-whisper wrapper
│   │   └── caption.py      # Ollama caption generation, JSON parsing
│   ├── publish/
│   │   ├── __init__.py
│   │   ├── meta.py         # Instagram + Facebook Graph API
│   │   ├── youtube.py      # YouTube Data API v3
│   │   └── x.py            # X/Twitter
│   ├── scheduler.py        # Publish queue runner
│   ├── tokens.py           # Token refresh daemon/checker
│   └── cli.py              # Click command group
├── configs/
│   └── brands/
│       ├── terp-tribe.json
│       └── typhon-forge.json
├── scripts/
│   ├── djinn-publish-scheduler.service
│   └── djinn-publish-scheduler.timer
└── tests/
    └── ...
```

### `pyproject.toml` (relevant excerpt)
```toml
[project]
name = "djinn-social"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "requests>=2.31",
    "faster-whisper>=1.0",
    "google-api-python-client>=2.100",
    "google-auth-oauthlib>=1.1",
    "tweepy>=4.14",
    "openai>=1.0",       # used for Ollama OpenAI-compatible endpoint
    "python-dotenv>=1.0",
    "rich>=13.0",         # colored terminal output
    "apscheduler>=3.10",
]

[project.scripts]
djinn = "djinn.cli:cli"
djinn-content-day-init = "djinn.cli:content_day_init"
djinn-media-ingest = "djinn.cli:media_ingest"
djinn-media-reel = "djinn.cli:media_reel"
djinn-media-caption = "djinn.cli:media_caption"
djinn-media-publish = "djinn.cli:media_publish"
djinn-content-find = "djinn.cli:content_find"
djinn-token-refresh = "djinn.cli:token_refresh"
```

### Config and Data Paths (XDG-compliant)
```python
# djinn/__init__.py
from pathlib import Path

DJINN_CONFIG_DIR = Path.home() / ".config" / "djinn"
DJINN_DATA_DIR = Path.home() / ".local" / "share" / "djinn"
DJINN_BRANDS_CONFIG_DIR = DJINN_CONFIG_DIR / "brands"
DJINN_BRANDS_DATA_DIR = DJINN_DATA_DIR / "brands"

# Created on first run
DJINN_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DJINN_DATA_DIR.mkdir(parents=True, exist_ok=True)
DJINN_BRANDS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
DJINN_BRANDS_DATA_DIR.mkdir(parents=True, exist_ok=True)
```

---

## 2. Module: `djinn.brands` — Config and DB Layer

### `brands.py` — Full Implementation

```python
# djinn/brands.py
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from djinn import DJINN_BRANDS_CONFIG_DIR, DJINN_BRANDS_DATA_DIR


@dataclass
class DayConfig:
    theme: str
    tone: str
    opening_pattern: str = ""


@dataclass
class BrandConfig:
    brand_name: str
    brand_slug: str
    season: int
    season_start_date: date
    base_folder: Path
    telegram_bot: str
    content_schedule: dict[str, DayConfig]
    platform_credentials: Path
    caption_persona: str
    db_path: Path

    @classmethod
    def load(cls, brand_slug: str) -> "BrandConfig":
        config_path = DJINN_BRANDS_CONFIG_DIR / f"{brand_slug}.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Brand config not found: {config_path}")
        with open(config_path) as f:
            data = json.load(f)
        schedule = {
            day: DayConfig(**cfg)
            for day, cfg in data["content_schedule"].items()
        }
        return cls(
            brand_name=data["brand_name"],
            brand_slug=data["brand_slug"],
            season=data["season"],
            season_start_date=date.fromisoformat(data["season_start_date"]),
            base_folder=Path(data["base_folder"]).expanduser(),
            telegram_bot=data["telegram_bot"],
            content_schedule=schedule,
            platform_credentials=Path(data["platform_credentials"]).expanduser(),
            caption_persona=data["caption_persona"],
            db_path=Path(data.get("db_path",
                str(DJINN_BRANDS_DATA_DIR / f"{brand_slug}.db"))).expanduser(),
        )

    def week_in_season(self, target_date: date) -> int:
        """1-indexed week number within the current season."""
        delta = (target_date - self.season_start_date).days
        return (delta // 7) + 1

    def next_episode(self, db_conn: sqlite3.Connection) -> int:
        """Auto-increments episode counter per brand per season."""
        row = db_conn.execute(
            "SELECT MAX(episode) FROM content_days WHERE brand=? AND season=?",
            (self.brand_slug, self.season),
        ).fetchone()
        current_max = row[0] if row[0] is not None else 0
        return current_max + 1

    def folder_slug(self, target_date: date) -> str:
        """Generates e.g. S6_E14_W2_Wax-Wednesday"""
        week = self.week_in_season(target_date)
        day_name = target_date.strftime("%A").lower()
        day_cfg = self.content_schedule.get(day_name)
        if day_cfg is None:
            raise ValueError(f"No content schedule for {day_name} in brand {self.brand_slug}")
        theme_slug = day_cfg.theme.replace(" ", "-")
        # Episode gets set when row is inserted; use placeholder for preview
        return f"S{self.season}_E{{episode}}_W{week}_{theme_slug}"


def get_db(brand_slug: str) -> sqlite3.Connection:
    db_path = DJINN_BRANDS_DATA_DIR / f"{brand_slug}.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS content_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            season INTEGER NOT NULL,
            week_in_season INTEGER NOT NULL,
            episode INTEGER NOT NULL,
            content_day TEXT NOT NULL,
            theme_name TEXT NOT NULL,
            folder_slug TEXT NOT NULL,
            project_path TEXT,
            status TEXT DEFAULT 'pending',
            published_ig INTEGER DEFAULT 0,
            published_fb INTEGER DEFAULT 0,
            published_yt INTEGER DEFAULT 0,
            published_x INTEGER DEFAULT 0,
            ig_media_id TEXT,
            fb_media_id TEXT,
            yt_video_id TEXT,
            x_tweet_id TEXT,
            archive_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            published_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_content_days_brand_season
            ON content_days(brand, season);

        CREATE TABLE IF NOT EXISTS token_store (
            id INTEGER PRIMARY KEY,
            brand TEXT NOT NULL,
            platform TEXT NOT NULL,
            token_type TEXT NOT NULL,
            token_value TEXT NOT NULL,
            expires_at TEXT,
            refreshed_at TEXT DEFAULT (datetime('now')),
            UNIQUE(brand, platform, token_type)
        );
    """)
    conn.commit()


def insert_content_day(
    conn: sqlite3.Connection,
    brand: BrandConfig,
    target_date: date,
) -> sqlite3.Row:
    day_name = target_date.strftime("%A").lower()
    day_cfg = brand.content_schedule[day_name]
    week = brand.week_in_season(target_date)
    episode = brand.next_episode(conn)
    slug = (
        f"S{brand.season}_E{episode}_W{week}_{day_cfg.theme.replace(' ', '-')}"
    )
    project_path = str(
        brand.base_folder
        / target_date.strftime("%A").capitalize()
        / slug
    )
    conn.execute(
        """INSERT INTO content_days
           (brand, season, week_in_season, episode, content_day,
            theme_name, folder_slug, project_path, status)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            brand.brand_slug, brand.season, week, episode,
            day_name, day_cfg.theme, slug, project_path, "pending"
        ),
    )
    conn.commit()
    return conn.execute(
        "SELECT * FROM content_days WHERE folder_slug=?", (slug,)
    ).fetchone()
```

### Key Design Decisions
- `week_in_season` is computed from `season_start_date` — no manual tracking needed.
- `episode` is a MAX + 1 query — crash-safe, no race condition for a single-user system.
- `token_store` table lives in the brands DB so tokens travel with the brand data.
- `sqlite3.Row` enables dict-style access: `row["folder_slug"]`.

---

## 3. Module: `djinn.media.ingest` — iCloud → Salomon Intake

### What Ingest Does
1. Scans `~/djinn-media-inbox/` for new files (or a specified path)
2. Detects HEIC, HEVC, MOV, MP4, JPG, PNG
3. Converts HEIC → JPEG using `heif-convert` (subprocess call)
4. Converts HEVC/MOV → H.264 MP4 using ffmpeg (subprocess)
5. Creates a project folder via `insert_content_day`
6. Copies/moves processed files into `project_path/videos/` and `project_path/pics/`
7. Writes `project_path/done/brand_context.json`
8. Updates DB row `status = "ingested"`

### `ingest.py`
```python
# djinn/media/ingest.py
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path

from rich.console import Console
from djinn.brands import BrandConfig, get_db, insert_content_day

console = Console()
INBOX = Path.home() / "djinn-media-inbox"


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def convert_heic(src: Path, dest: Path) -> Path:
    """heif-convert src.heic dest.jpg — falls back to ffmpeg static build."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        run(["heif-convert", str(src), str(dest)])
    except (FileNotFoundError, RuntimeError):
        # ffmpeg 6.1+ static build can handle HEIC
        run(["ffmpeg", "-y", "-i", str(src), str(dest)])
    return dest


def convert_hevc_to_h264(src: Path, dest: Path) -> Path:
    """Transcode HEVC/MOV → H.264 MP4, preserving original resolution."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        str(dest),
    ]
    run(cmd)
    return dest


def ingest_files(
    brand: BrandConfig,
    target_date: date,
    source_dir: Path = INBOX,
    move: bool = False,
) -> dict:
    """
    Scans source_dir, creates project folder for target_date, moves/converts files.
    Returns manifest dict written to done/brand_context.json.
    """
    conn = get_db(brand.brand_slug)
    row = insert_content_day(conn, brand, target_date)
    project_path = Path(row["project_path"])
    videos_dir = project_path / "videos"
    pics_dir = project_path / "pics"
    done_dir = project_path / "done"
    for d in [videos_dir, pics_dir, done_dir]:
        d.mkdir(parents=True, exist_ok=True)

    manifest = {
        "brand": brand.brand_slug,
        "brand_name": brand.brand_name,
        "season": brand.season,
        "episode": row["episode"],
        "week": row["week_in_season"],
        "folder_slug": row["folder_slug"],
        "theme": row["theme_name"],
        "date": target_date.isoformat(),
        "day": target_date.strftime("%A"),
        "tone": brand.content_schedule[target_date.strftime("%A").lower()].tone,
        "caption_persona": brand.caption_persona,
        "opening_pattern": brand.content_schedule[
            target_date.strftime("%A").lower()
        ].opening_pattern,
        "videos": [],
        "pics": [],
    }

    for src in sorted(source_dir.iterdir()):
        if src.name.startswith(".") or not src.is_file():
            continue

        ext = src.suffix.lower()

        # HEIC → JPEG
        if ext in (".heic", ".heif"):
            dest = pics_dir / f"{src.stem}.jpg"
            convert_heic(src, dest)
            manifest["pics"].append(str(dest.relative_to(project_path)))
            console.print(f"[green]✓ HEIC converted:[/green] {dest.name}")

        # MOV/HEVC/MP4 → H.264 MP4
        elif ext in (".mov", ".m4v"):
            dest = videos_dir / f"{src.stem}.mp4"
            convert_hevc_to_h264(src, dest)
            manifest["videos"].append(str(dest.relative_to(project_path)))
            console.print(f"[green]✓ MOV converted:[/green] {dest.name}")

        # Already MP4 — copy directly (may still be HEVC-encoded)
        elif ext == ".mp4":
            dest = videos_dir / src.name
            # Probe codec: if HEVC, transcode; if H.264, copy
            probe = run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_streams", str(src)],
                check=False,
            )
            codec = "h264"  # default
            if probe.returncode == 0:
                import json as _json
                streams = _json.loads(probe.stdout).get("streams", [])
                for s in streams:
                    if s.get("codec_type") == "video":
                        codec = s.get("codec_name", "h264")
                        break
            if codec in ("hevc", "h265"):
                convert_hevc_to_h264(src, dest)
            else:
                shutil.copy2(src, dest)
            manifest["videos"].append(str(dest.relative_to(project_path)))
            console.print(f"[green]✓ MP4 ingested:[/green] {dest.name}")

        # JPEG/PNG → copy to pics
        elif ext in (".jpg", ".jpeg", ".png"):
            dest = pics_dir / src.name
            shutil.copy2(src, dest)
            manifest["pics"].append(str(dest.relative_to(project_path)))

        else:
            console.print(f"[yellow]⚠ Skipped:[/yellow] {src.name} (unsupported format)")
            continue

        if move:
            src.unlink()

    # Write brand_context.json
    ctx_path = done_dir / "brand_context.json"
    with open(ctx_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Update DB
    conn.execute(
        "UPDATE content_days SET status='ingested' WHERE folder_slug=?",
        (row["folder_slug"],),
    )
    conn.commit()
    conn.close()
    console.print(f"\n[bold green]Ingest complete:[/bold green] {row['folder_slug']}")
    return manifest
```

### Critical Edge Cases
- **No files in inbox:** ingest creates the folder structure and writes `brand_context.json` with empty lists. Claude can still run caption from transcript-only mode.
- **Multiple videos:** all get ingested. The reel step uses the first video by default; Javier can override with `--video-file`.
- **ProRes RAW (.mov + .raw pair):** ffmpeg will fail silently. Add check: if `ffprobe` reports `prores_ks` codec AND file size > 2GB, warn and skip. Javier must reshoot as HEVC.
- **Live Photo pairs:** `.heic` + `.mov` with same stem. Both get processed independently (still → pics, motion → videos). This is correct behavior.

---

## 4. Module: `djinn.media.reel` — Video Processing Pipeline

### What the Reel Pipeline Does
1. Takes the primary video from `project_path/videos/` (first `.mp4`, or `--video-file` override)
2. Reads `done/brand_context.json` for metadata
3. Produces `done/reel.mp4` — 1080×1920 H.264, 30fps, AAC, `faststart`
4. Produces `done/cover.jpg` — frame extracted at `--thumb-offset` seconds (default 1.5s)
5. Optionally produces `done/reel_subtitled.mp4` (requires transcription to have run first)
6. Updates DB `status = "reel_ready"`

### `reel.py`
```python
# djinn/media/reel.py
import json
import subprocess
from pathlib import Path

from rich.console import Console
from djinn.brands import get_db

console = Console()

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TARGET_FPS = 30
TARGET_CRF = 20
AUDIO_BITRATE = "192k"


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg error:\n{result.stderr[-2000:]}")


def build_reel(
    project_path: Path,
    video_file: Path | None = None,
    thumb_offset: float = 1.5,
    burn_subtitles: bool = False,
    crf: int = TARGET_CRF,
) -> dict:
    """
    Build reel.mp4 + cover.jpg from the project's video.
    Returns paths dict.
    """
    done_dir = project_path / "done"
    videos_dir = project_path / "videos"
    done_dir.mkdir(parents=True, exist_ok=True)

    # Select source video
    if video_file is None:
        candidates = sorted(videos_dir.glob("*.mp4"))
        if not candidates:
            raise FileNotFoundError(f"No MP4 files in {videos_dir}")
        video_file = candidates[0]

    reel_out = done_dir / "reel.mp4"
    cover_out = done_dir / "cover.jpg"

    # --- Build reel.mp4 ---
    # scale to 9:16, pad with black if needed, add faststart
    vf_scale = (
        f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={TARGET_WIDTH}:{TARGET_HEIGHT}:"
        "(ow-iw)/2:(oh-ih)/2:black,"
        "setsar=1"
    )
    run([
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-vf", vf_scale,
        "-r", str(TARGET_FPS),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", str(crf),
        "-profile:v", "high",
        "-level:v", "4.0",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-ar", "44100",
        "-movflags", "+faststart",
        # Remove edit lists (Instagram rejects videos with edit lists)
        "-use_editlist", "0",
        str(reel_out),
    ])
    console.print(f"[green]✓ reel.mp4[/green] → {reel_out}")

    # --- Extract cover frame ---
    run([
        "ffmpeg", "-y",
        "-ss", str(thumb_offset),
        "-i", str(reel_out),
        "-vframes", "1",
        "-q:v", "2",
        str(cover_out),
    ])
    console.print(f"[green]✓ cover.jpg[/green] → {cover_out}")

    # --- Optional: burn-in subtitles ---
    subtitled_out = None
    if burn_subtitles:
        srt_path = done_dir / "transcription.srt"
        if not srt_path.exists():
            console.print("[yellow]⚠ Subtitle burn-in skipped — transcription.srt not found[/yellow]")
        else:
            subtitled_out = done_dir / "reel_subtitled.mp4"
            subtitle_style = (
                "FontSize=28,"
                "Fontname=Arial,"
                "Bold=1,"
                "PrimaryColour=&H00FFFFFF,"
                "OutlineColour=&H00000000,"
                "Outline=2,"
                "Shadow=1,"
                "Alignment=2,"
                "MarginV=120"
            )
            run([
                "ffmpeg", "-y",
                "-i", str(reel_out),
                "-vf", f"subtitles={str(srt_path)}:force_style='{subtitle_style}'",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", str(crf),
                "-c:a", "copy",
                str(subtitled_out),
            ])
            console.print(f"[green]✓ reel_subtitled.mp4[/green] → {subtitled_out}")

    # Update manifest
    ctx_path = done_dir / "brand_context.json"
    if ctx_path.exists():
        with open(ctx_path) as f:
            ctx = json.load(f)
        ctx["reel_path"] = str(reel_out)
        ctx["cover_path"] = str(cover_out)
        if subtitled_out:
            ctx["subtitled_reel_path"] = str(subtitled_out)
        with open(ctx_path, "w") as f:
            json.dump(ctx, f, indent=2)

    return {
        "reel": reel_out,
        "cover": cover_out,
        "subtitled": subtitled_out,
    }
```

### ffmpeg Flags Explained
| Flag | Why |
|------|-----|
| `-use_editlist 0` | Instagram Graph API rejects MP4 files with edit lists (HEVC container quirk) |
| `-pix_fmt yuv420p` | Instagram, Facebook, YouTube all require 4:2:0. H.264 High profile sometimes produces 4:4:4 on certain encoders |
| `-profile:v high -level:v 4.0` | Maximum compatibility across all platforms |
| `-movflags +faststart` | Moves `moov` atom to file start — Meta requires this for streaming |
| `force_original_aspect_ratio=decrease` + `pad` | Pillarboxes portrait video into 9:16 without cropping content |
| `setsar=1` | Resets Sample Aspect Ratio to 1:1 — prevents distortion from anamorphic sources |

### File Size Check
After encoding, check `reel.mp4` size:
```python
import os
size_mb = os.path.getsize(str(reel_out)) / (1024 * 1024)
if size_mb > 95:  # Instagram Graph API hard limit is 100MB
    console.print(f"[red]⚠ reel.mp4 is {size_mb:.1f}MB — approaching 100MB limit[/red]")
    console.print("Re-encode with higher CRF (e.g. --crf 24) or trim video")
if size_mb > 480:  # X limit is 512MB
    raise RuntimeError(f"reel.mp4 ({size_mb:.1f}MB) exceeds X/Twitter 512MB limit")
```

---

## 5. Module: `djinn.media.transcribe` — faster-whisper Integration

### `transcribe.py`
```python
# djinn/media/transcribe.py
import json
from pathlib import Path

from rich.console import Console

console = Console()


def transcribe_reel(
    project_path: Path,
    model_size: str = "small",
    language: str = "en",
) -> dict:
    """
    Runs faster-whisper on done/reel.mp4.
    Writes done/transcription.txt and done/transcription.srt.
    Returns {"text": str, "srt_path": str}.
    """
    # Lazy import — faster-whisper takes ~2s to load, don't penalize other commands
    from faster_whisper import WhisperModel

    done_dir = project_path / "done"
    reel_path = done_dir / "reel.mp4"
    if not reel_path.exists():
        raise FileNotFoundError(f"reel.mp4 not found at {reel_path}. Run media-reel first.")

    console.print(f"[cyan]Transcribing with faster-whisper ({model_size})...[/cyan]")

    # Load model with int8 quantization for CPU efficiency
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(reel_path),
        beam_size=5,
        language=language,
        vad_filter=True,       # Voice Activity Detection — skips silence
        vad_parameters=dict(
            min_silence_duration_ms=500,
        ),
    )

    # Build plain text and SRT simultaneously
    full_text_lines = []
    srt_blocks = []
    for i, seg in enumerate(segments, start=1):
        text = seg.text.strip()
        if not text:
            continue
        full_text_lines.append(text)

        start = _seconds_to_srt_timestamp(seg.start)
        end = _seconds_to_srt_timestamp(seg.end)
        srt_blocks.append(f"{i}\n{start} --> {end}\n{text}\n")

    full_text = " ".join(full_text_lines)
    srt_content = "\n".join(srt_blocks)

    txt_path = done_dir / "transcription.txt"
    srt_path = done_dir / "transcription.srt"
    txt_path.write_text(full_text, encoding="utf-8")
    srt_path.write_text(srt_content, encoding="utf-8")

    # Update brand_context.json
    ctx_path = done_dir / "brand_context.json"
    if ctx_path.exists():
        with open(ctx_path) as f:
            ctx = json.load(f)
        ctx["transcript_snippet"] = full_text[:500]
        ctx["transcript_language"] = info.language
        with open(ctx_path, "w") as f:
            json.dump(ctx, f, indent=2)

    console.print(f"[green]✓ Transcription complete[/green] ({len(full_text_lines)} segments)")
    return {"text": full_text, "srt_path": str(srt_path)}


def _seconds_to_srt_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
```

### Model Selection Guide
| Use case | Model | Reason |
|----------|-------|--------|
| Standard social clip (<90s) | `small` | Best accuracy/speed tradeoff on CPU |
| Long-form video (>3 min) | `medium` | Better at proper nouns, technical terms |
| Subtitle burn-in (quality matters) | `medium` | Higher accuracy = fewer embarrassing on-screen typos |
| Quick hashtag extraction only | `base` | 2× faster, accuracy sufficient |
| GPU available (VRAM ≥ 6GB) | `large-v3-turbo` | Best accuracy, ~19s for 60s clip |

### `vad_filter=True` Importance
VAD (Voice Activity Detection) pre-filters silence. Without it, whisper hallucinates text in silent gaps — a known issue with all Whisper models. Always enable on social content that has music/ambient sound.

---

## 6. Module: `djinn.media.caption` — Ollama Caption Generation

### `caption.py`
```python
# djinn/media/caption.py
import json
from pathlib import Path
from typing import Optional

from openai import OpenAI
from rich.console import Console

console = Console()

# Ollama OpenAI-compatible endpoint
# The openai library works unchanged with base_url pointing to Ollama
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"  # Required by openai library, value ignored by Ollama


# Cannabis-safe language rules — injected into every Terp Tribe prompt
CANNABIS_SAFE_RULES = """
CRITICAL — Platform Safety Rules:
- NEVER use: #weed, #cannabis, #420, #marijuana, #thc, #cbd, #pot, #smoke, #stoner
- SAFE words: "herb", "flower", "terp", "terpene", "dab", "concentrate", "functional art",
  "botanical", "ritual", "culture", "lifestyle", "community", "accessory", "gear", "glass",
  "torch", "rig", "banger", "terp pearl", "carb cap", "rosin", "live resin"
- On Instagram/Facebook: NO prices, NO "available now", NO "DM to order" — this triggers
  commercial solicitation enforcement. Use "link in bio" or "check website" instead.
- On YouTube: "functional art", "maker", "artisan glass" language preferred. No drug slang.
- On X: X is more permissive than Meta. Standard product language is fine.
"""


def build_caption_prompt(ctx: dict, hashtag_bank: list[str]) -> str:
    is_cannabis_brand = "terp" in ctx.get("brand", "").lower()
    safety_rules = CANNABIS_SAFE_RULES if is_cannabis_brand else ""
    
    trending_topics = ctx.get("trending_topics", [])
    hook_style = ctx.get("recommended_hook_style", "question")
    transcript = ctx.get("transcript_snippet", "")
    
    hashtag_sample = hashtag_bank[-20:] if hashtag_bank else []
    
    return f"""You are the caption writer for {ctx['brand_name']}.

Brand voice: {ctx['caption_persona']}

Content context:
- Theme: {ctx['theme']} (tone: {ctx['tone']})
- Season {ctx['season']}, Episode {ctx['episode']}, Week {ctx['week']}
- Day: {ctx['day']}
- Suggested opening pattern: "{ctx.get('opening_pattern', '')}"
- Transcript snippet: "{transcript}"
- Trending topics: {trending_topics}
- Recommended hook style: {hook_style}
- Available hashtags (use sparingly): {hashtag_sample}

{safety_rules}

Caption requirements:
- Instagram (ig): 150-220 words. 3-5 hashtags from the safe bank above. 
  First sentence is the hook. End with a call-to-action or question.
- Facebook (fb): First 2 sentences of the IG caption only, max 3 hashtags.
  Facebook audience skews older — add slight context for clarity.
- YouTube title (yt_title): Under 70 characters. SEO-optimized with main keyword first.
  Include the theme keyword. NO clickbait. NO all-caps.
- YouTube description (yt_description): First 125 chars must be the hook (visible before "more").
  Then 3-5 sentence body. Then: "🔗 Check bio for links" on its own line.
  Then: "Tags: [comma-separated keyword list]" at the bottom.
- X/Twitter (x): Under 250 characters. Punchy. 1-2 hashtags max. No filler words.
  Mobile-first — imagine it being read on a subway.

RESPOND ONLY with valid JSON, no explanation, no markdown code fences:
{{
  "ig": "...",
  "fb": "...",
  "yt_title": "...",
  "yt_description": "...",
  "yt_tags": ["tag1", "tag2"],
  "x": "..."
}}"""


def generate_captions(
    project_path: Path,
    model: str = "qwen2.5:14b",
    hashtag_bank: Optional[list[str]] = None,
) -> dict:
    """
    Reads done/brand_context.json, generates all 4 platform captions via Ollama.
    Writes individual caption files to done/.
    Returns the parsed caption dict.
    """
    done_dir = project_path / "done"
    ctx_path = done_dir / "brand_context.json"
    if not ctx_path.exists():
        raise FileNotFoundError(f"brand_context.json not found. Run ingest first.")
    
    with open(ctx_path) as f:
        ctx = json.load(f)
    
    # Load hashtag bank if provided
    if hashtag_bank is None:
        hashtag_bank = _load_hashtag_bank(ctx.get("brand", ""))
    
    # Load trend signal if available
    trend_signal_path = Path.home() / "djinn" / "social" / f"TREND-SIGNAL-{ctx['brand']}.md"
    if trend_signal_path.exists():
        trend_text = trend_signal_path.read_text()
        ctx["trending_topics"] = _extract_trending_topics(trend_text)
        ctx["recommended_hook_style"] = _extract_hook_style(trend_text)
    
    prompt = build_caption_prompt(ctx, hashtag_bank)
    
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    
    console.print(f"[cyan]Generating captions with {model}...[/cyan]")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional social media caption writer. "
                    "You ALWAYS respond with valid JSON and nothing else. "
                    "No markdown. No explanation. Pure JSON."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
        # Ollama supports response_format for JSON mode on supported models
        response_format={"type": "json_object"},
    )
    
    raw = response.choices[0].message.content.strip()
    
    # Parse and validate
    try:
        captions = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract JSON from response if model added explanation
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            captions = json.loads(match.group())
        else:
            raise ValueError(f"Model did not return valid JSON:\n{raw[:500]}")
    
    # Validate required keys
    required = ["ig", "fb", "yt_title", "yt_description", "yt_tags", "x"]
    missing = [k for k in required if k not in captions]
    if missing:
        raise ValueError(f"Caption response missing keys: {missing}")
    
    # Write individual files
    (done_dir / "caption_ig.txt").write_text(captions["ig"])
    (done_dir / "caption_fb.txt").write_text(captions["fb"])
    (done_dir / "caption_yt.txt").write_text(
        f"{captions['yt_title']}\n\n{captions['yt_description']}"
    )
    (done_dir / "caption_x.txt").write_text(captions["x"])
    (done_dir / "captions.json").write_text(json.dumps(captions, indent=2))
    
    # Update brand_context.json
    ctx["captions"] = captions
    with open(ctx_path, "w") as f:
        json.dump(ctx, f, indent=2)
    
    console.print("[green]✓ Captions generated and written to done/[/green]")
    _print_caption_preview(captions)
    return captions


def _print_caption_preview(captions: dict) -> None:
    console.print("\n[bold]Caption Preview[/bold]")
    console.print(f"[bold]IG:[/bold] {captions['ig'][:100]}...")
    console.print(f"[bold]YT Title:[/bold] {captions['yt_title']}")
    console.print(f"[bold]X:[/bold] {captions['x']}")


def _load_hashtag_bank(brand_slug: str) -> list[str]:
    bank_path = Path.home() / ".config" / "djinn" / "brands" / f"{brand_slug}-hashtags.txt"
    if not bank_path.exists():
        return []
    return [line.strip() for line in bank_path.read_text().splitlines() if line.strip()]


def _extract_trending_topics(trend_md: str) -> list[str]:
    """Simple extraction — looks for bullet items under '## Trending' header."""
    lines = trend_md.splitlines()
    in_section = False
    topics = []
    for line in lines:
        if "trending" in line.lower() and line.startswith("#"):
            in_section = True
            continue
        if in_section and line.startswith("#"):
            break
        if in_section and line.strip().startswith("-"):
            topics.append(line.strip().lstrip("- "))
    return topics[:5]


def _extract_hook_style(trend_md: str) -> str:
    """Looks for hook style recommendation in trend signal."""
    for line in trend_md.splitlines():
        if "hook" in line.lower() and "style" in line.lower():
            return line.split(":")[-1].strip() if ":" in line else "question"
    return "question"
```

### Model Selection for Caption Generation
| Model | Speed (14B params, CPU) | Quality | Notes |
|-------|------------------------|---------|-------|
| `qwen2.5:14b` | ~45s | Excellent | **Recommended** — best JSON compliance |
| `qwen2.5:7b` | ~20s | Good | Use for quick iterations |
| `phi4:14b` | ~40s | Excellent | Alternative; may need stronger JSON forcing |
| `llama3.2:3b` | ~8s | Acceptable | Only for compression tasks (X captions) |

**JSON mode note:** Ollama's `response_format: {"type": "json_object"}` is only supported on models that were fine-tuned for it (Qwen, Llama 3.x). If using an older model, remove `response_format` and rely on the regex fallback.

---

## 7. Module: `djinn.publish.meta` — Instagram + Facebook Graph API

### API Version and Base URL
```python
# djinn/publish/meta.py
import json
import os
import time
import tempfile
from pathlib import Path
import requests
from rich.console import Console
from djinn.brands import BrandConfig

console = Console()

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}"

# Meta Graph API rate limit: 25 published posts per 24-hour window per IG account
# Content publishing limit check endpoint
LIMIT_ENDPOINT = "/{ig_user_id}/content_publishing_limit"
```

### Token Loading
```python
def load_meta_creds(brand: BrandConfig) -> dict:
    """Load brand-scoped Meta credentials from env file."""
    from dotenv import dotenv_values
    creds = dotenv_values(brand.platform_credentials)
    slug = brand.brand_slug.replace("-", "_").upper()
    return {
        "ig_user_id": creds.get(f"IG_USER_ID_{slug[:2].upper()}"),
        "fb_page_id": creds.get(f"FB_PAGE_ID_{slug[:2].upper()}"),
        "page_token": creds.get(f"META_PAGE_TOKEN_{slug[:2].upper()}"),
    }
```

### Instagram Reels Upload — Full Flow
```python
def upload_instagram_reel(
    brand: BrandConfig,
    video_url: str,
    caption: str,
    cover_url: Optional[str] = None,
    share_to_feed: bool = True,
    dry_run: bool = False,
) -> str:
    """
    Full 3-step Instagram Reels upload.
    video_url must be publicly accessible (see Section 13 for hosting strategy).
    Returns published media ID.
    """
    creds = load_meta_creds(brand)
    ig_user_id = creds["ig_user_id"]
    token = creds["page_token"]
    
    if dry_run:
        console.print(f"[yellow][DRY RUN] Would upload to IG:[/yellow] {video_url[:60]}...")
        return "dry_run_media_id"

    # --- Check rate limit first ---
    limit_resp = requests.get(
        f"{GRAPH_BASE}/{ig_user_id}/content_publishing_limit",
        params={
            "fields": "config,quota_usage",
            "access_token": token,
        },
    ).json()
    quota_used = limit_resp.get("data", [{}])[0].get("quota_usage", 0)
    quota_max = limit_resp.get("data", [{}])[0].get("config", {}).get("quota_total", 25)
    if quota_used >= quota_max:
        raise RuntimeError(
            f"Instagram publishing rate limit reached: {quota_used}/{quota_max} posts "
            "in the last 24 hours. Wait before publishing."
        )
    console.print(f"[cyan]IG quota: {quota_used}/{quota_max}[/cyan]")

    # --- Step 1: Create media container ---
    container_params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": str(share_to_feed).lower(),
        "access_token": token,
    }
    if cover_url:
        container_params["cover_url"] = cover_url

    console.print("[cyan]Step 1/3: Creating IG media container...[/cyan]")
    container_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        params=container_params,
    ).json()

    if "error" in container_resp:
        raise RuntimeError(f"Container creation failed: {container_resp['error']}")

    container_id = container_resp["id"]
    console.print(f"[green]Container created:[/green] {container_id}")

    # --- Step 2: Poll until FINISHED ---
    console.print("[cyan]Step 2/3: Polling container status...[/cyan]")
    max_polls = 30  # 5 min max (30 × 10s)
    for attempt in range(max_polls):
        status_resp = requests.get(
            f"{GRAPH_BASE}/{container_id}",
            params={
                "fields": "status_code,status",
                "access_token": token,
            },
        ).json()

        status_code = status_resp.get("status_code", "IN_PROGRESS")
        console.print(f"  Poll {attempt + 1}/{max_polls}: {status_code}")

        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            raise RuntimeError(
                f"Container processing failed. Error: {status_resp.get('status')}"
            )
        elif status_code == "EXPIRED":
            raise RuntimeError("Container expired (>24h since creation). Create a new container.")

        time.sleep(10)
    else:
        raise TimeoutError("Container did not finish processing within 5 minutes.")

    # --- Step 3: Publish ---
    console.print("[cyan]Step 3/3: Publishing...[/cyan]")
    publish_resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        params={
            "creation_id": container_id,
            "access_token": token,
        },
    ).json()

    if "error" in publish_resp:
        raise RuntimeError(f"Publish failed: {publish_resp['error']}")

    media_id = publish_resp["id"]
    console.print(f"[bold green]✓ Instagram Reel published:[/bold green] {media_id}")
    return media_id
```

### Facebook Reels Upload
```python
def upload_facebook_reel(
    brand: BrandConfig,
    video_url: str,
    caption: str,
    dry_run: bool = False,
) -> str:
    """
    Facebook Reels upload via Page video endpoint.
    As of June 2025, ALL Facebook videos are Reels — use the standard video endpoint.
    Returns video ID.
    """
    creds = load_meta_creds(brand)
    fb_page_id = creds["fb_page_id"]
    token = creds["page_token"]

    if dry_run:
        console.print(f"[yellow][DRY RUN] Would upload to FB:[/yellow] {video_url[:60]}...")
        return "dry_run_video_id"

    console.print("[cyan]Uploading Facebook Reel...[/cyan]")
    # Facebook video upload is a single call (no container polling needed for videos
    # under ~4GB via URL). For large files, use the Resumable Upload API.
    resp = requests.post(
        f"{GRAPH_BASE}/{fb_page_id}/videos",
        params={
            "file_url": video_url,
            "description": caption,
            "published": "true",
            "access_token": token,
        },
    ).json()

    if "error" in resp:
        raise RuntimeError(f"Facebook video upload failed: {resp['error']}")

    video_id = resp.get("id")
    console.print(f"[bold green]✓ Facebook Reel uploaded:[/bold green] {video_id}")
    return video_id
```

### Publishing from Project Folder
```python
def publish_project_to_meta(
    project_path: Path,
    brand: BrandConfig,
    platforms: list[str] = ("ig", "fb"),
    video_server_url: str = None,
    dry_run: bool = False,
) -> dict:
    """
    Main entry point: reads done/ folder, uploads to IG and/or FB.
    video_server_url: Base URL of the temp HTTP server (see Section 13).
    Returns dict of published IDs.
    """
    done_dir = project_path / "done"
    reel_path = done_dir / "reel.mp4"
    cover_path = done_dir / "cover.jpg"

    if not reel_path.exists():
        raise FileNotFoundError("done/reel.mp4 not found. Run media-reel first.")

    with open(done_dir / "brand_context.json") as f:
        ctx = json.load(f)

    captions_path = done_dir / "captions.json"
    if not captions_path.exists():
        raise FileNotFoundError("done/captions.json not found. Run media-caption first.")

    with open(captions_path) as f:
        captions = json.load(f)

    results = {}

    # IG requires publicly accessible URL — see Section 13
    if video_server_url:
        video_url = f"{video_server_url}/{reel_path.name}"
        cover_url = f"{video_server_url}/{cover_path.name}"
    else:
        raise ValueError(
            "video_server_url is required for Meta publishing. "
            "See Section 13 for the local HTTP server approach."
        )

    if "ig" in platforms:
        ig_id = upload_instagram_reel(
            brand=brand,
            video_url=video_url,
            caption=captions["ig"],
            cover_url=cover_url,
            dry_run=dry_run,
        )
        results["ig_media_id"] = ig_id

    if "fb" in platforms:
        fb_id = upload_facebook_reel(
            brand=brand,
            video_url=video_url,
            caption=captions["fb"],
            dry_run=dry_run,
        )
        results["fb_video_id"] = fb_id

    # Update DB
    if not dry_run:
        from djinn.brands import get_db
        conn = get_db(brand.brand_slug)
        conn.execute(
            """UPDATE content_days SET
                published_ig=?, ig_media_id=?,
                published_fb=?, fb_media_id=?,
                status='published', published_at=datetime('now')
               WHERE project_path=?""",
            (
                1 if "ig" in platforms else 0,
                results.get("ig_media_id"),
                1 if "fb" in platforms else 0,
                results.get("fb_video_id"),
                str(project_path),
            ),
        )
        conn.commit()
        conn.close()

    return results
```

### Meta API Critical Notes
- **API version:** Currently `v21.0` (May 2026). Meta versions quarterly. Check `developers.facebook.com` for sunset notices — each version is supported ~2 years.
- **Instagram container model for Reels:** The `video_url` must be publicly accessible. Meta's servers fetch the video directly. You cannot POST binary file data to the standard endpoint — use the Resumable Upload for that.
- **100MB hard cap:** Instagram Graph API enforces 100MB for the standard flow. The Resumable Upload (`rupload.facebook.com`) handles larger files. For Djinn's clips (<90s at CRF 20), size will be 20–80MB — under the limit.
- **`-use_editlist 0` is mandatory:** HEVC `.mov` files from iPhone contain edit lists. Without stripping them, the container step returns `Error 2207001`.
- **Instagram cross-post to Facebook:** There is no official API to cross-post from IG to FB simultaneously. They are separate API calls with separate endpoints. Instagram's in-app share to Facebook is not available via API.
- **Token expiry:** Long-lived User tokens expire in 60 days. Page access tokens (what you're using) can be non-expiring if the user never changes their password. To get a non-expiring Page token: exchange User token → get Page access token (always non-expiring as of Meta's 2021 change). Verify with: `GET /{page-token}/debug_token`.

---

## 8. Module: `djinn.publish.youtube` — YouTube Data API v3

### One-Time OAuth Setup (Browser Required)
Run this once per brand to get the refresh token:
```python
# scripts/youtube_oauth_setup.py
# Run this ONCE in a browser environment: python scripts/youtube_oauth_setup.py --brand terp-tribe

import click
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

@click.command()
@click.option("--brand", required=True)
@click.option("--client-secrets", required=True, help="Path to client_secrets.json from Google Cloud Console")
def setup(brand, client_secrets):
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
    creds = flow.run_local_server(port=8080)
    
    # Save refresh token to brand credential file
    brand_env = Path.home() / ".config" / "djinn" / f"meta-{brand}.env"
    slug = brand.replace("-", "_").upper()[:2]
    
    with open(brand_env, "a") as f:
        f.write(f"\nYT_REFRESH_TOKEN_{slug}={creds.refresh_token}\n")
        f.write(f"YT_CLIENT_ID_{slug}={creds.client_id}\n")
        f.write(f"YT_CLIENT_SECRET_{slug}={creds.client_secret}\n")
    
    print(f"Refresh token written to {brand_env}")
    print("You will NOT need to do this again unless you revoke access.")

if __name__ == "__main__":
    setup()
```

### `youtube.py`
```python
# djinn/publish/youtube.py
import json
import os
import time
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from rich.console import Console

from djinn.brands import BrandConfig

console = Console()

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_CATEGORY_HOWTO = "26"   # How-to & Style
YOUTUBE_CATEGORY_SCIENCE = "28" # Science & Technology (for Typhon's Forge)


def _get_youtube_service(brand: BrandConfig):
    from dotenv import dotenv_values
    creds_raw = dotenv_values(brand.platform_credentials)
    slug = brand.brand_slug.replace("-", "_").upper()[:2]
    
    creds = Credentials(
        token=None,
        refresh_token=creds_raw[f"YT_REFRESH_TOKEN_{slug}"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_raw[f"YT_CLIENT_ID_{slug}"],
        client_secret=creds_raw[f"YT_CLIENT_SECRET_{slug}"],
        scopes=SCOPES,
    )
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload_youtube_short(
    brand: BrandConfig,
    project_path: Path,
    dry_run: bool = False,
) -> str:
    """
    Upload reel.mp4 to YouTube as a Short with thumbnail.
    Returns video ID.
    """
    done_dir = project_path / "done"
    reel_path = done_dir / "reel.mp4"
    cover_path = done_dir / "cover.jpg"
    
    if not reel_path.exists():
        raise FileNotFoundError("done/reel.mp4 not found.")

    with open(done_dir / "captions.json") as f:
        captions = json.load(f)

    with open(done_dir / "brand_context.json") as f:
        ctx = json.load(f)

    title = captions["yt_title"]
    description = captions["yt_description"]
    tags = captions.get("yt_tags", [])
    
    # YouTube Shorts: 9:16 + ≤3min → auto-classified as Short. No special flag needed.
    # Category: How-to for Terp Tribe, Science & Tech for Typhon's Forge
    is_maker = "typhon" in brand.brand_slug.lower()
    category_id = YOUTUBE_CATEGORY_SCIENCE if is_maker else YOUTUBE_CATEGORY_HOWTO
    
    if dry_run:
        console.print(f"[yellow][DRY RUN] Would upload to YouTube:[/yellow] '{title}'")
        return "dry_run_yt_id"

    youtube = _get_youtube_service(brand)

    body = {
        "snippet": {
            "title": title[:100],  # YouTube hard limit: 100 chars
            "description": description,
            "tags": tags[:500],    # YouTube tag list limit
            "categoryId": category_id,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    console.print(f"[cyan]Uploading to YouTube: '{title[:50]}...'[/cyan]")
    media = MediaFileUpload(
        str(reel_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=10 * 1024 * 1024,  # 10MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    # Resumable upload loop
    response = None
    retry_count = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                console.print(f"  YouTube upload: {pct}%", end="\r")
        except Exception as e:
            retry_count += 1
            if retry_count > 5:
                raise RuntimeError(f"YouTube upload failed after 5 retries: {e}")
            console.print(f"[yellow]Upload error (retry {retry_count}/5): {e}[/yellow]")
            time.sleep(5 * retry_count)  # exponential backoff

    video_id = response["id"]
    console.print(f"\n[bold green]✓ YouTube Short uploaded:[/bold green] {video_id}")
    console.print(f"  URL: https://youtube.com/shorts/{video_id}")

    # Upload thumbnail
    if cover_path.exists():
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(cover_path), mimetype="image/jpeg"),
            ).execute()
            console.print("[green]✓ YouTube thumbnail set[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Thumbnail upload failed (non-critical): {e}[/yellow]")

    # Update DB
    from djinn.brands import get_db
    conn = get_db(brand.brand_slug)
    conn.execute(
        "UPDATE content_days SET published_yt=1, yt_video_id=? WHERE project_path=?",
        (video_id, str(project_path)),
    )
    conn.commit()
    conn.close()

    return video_id
```

### YouTube Quota Math
- Default quota: **10,000 units/day per Google Cloud project**
- `videos.insert` costs **1,600 units**
- `thumbnails.set` costs **50 units**
- Total per upload: ~1,650 units
- Max uploads/day: **6 videos** before hitting quota ceiling
- Djinn's usage: 2 brands × 1 video/day = 2 uploads/day = 3,300 units — **well within limits**
- If Javier scales to more brands or frequency: request quota increase via Google Cloud Console → IAM & Admin → Quotas (free, takes 3-5 business days)

### YouTube Cannabis Policy
YouTube does **not** ban uploads for cannabis-adjacent content — only demonetization. Glass accessories and 3D printed functional art will be demonetized but not removed. Use:
- **Category 26 (How-to & Style)** for Terp Tribe — lifestyle content
- **Category 28 (Science & Technology)** for Typhon's Forge — maker content
- Avoid explicit drug consumption in video or title
- `selfDeclaredMadeForKids: false` is required — always set this explicitly

---

## 9. Module: `djinn.publish.x` — X/Twitter v2 + v1.1 Media

### X API Reality in 2026
The X API moved to pay-per-use pricing. The legacy Free tier is **deprecated** — no more "500 posts/month free." As of early 2026:
- Standard text post: **$0.015**
- Post with a URL: **$0.20**
- Posts with media (video): use v1.1 media upload, cost falls under write endpoint pricing
- For 7 posts/week × 2 brands = 60 posts/month: ~$0.90–$12/month depending on mix

For Djinn: **start with minimal posting to X** (1–2 posts/day across both brands) and evaluate cost after the first billing cycle.

### `x.py`
```python
# djinn/publish/x.py
import json
import time
from pathlib import Path

import tweepy
from rich.console import Console

from djinn.brands import BrandConfig

console = Console()


def _get_tweepy_clients(brand: BrandConfig):
    """Returns (api_v1, client_v2) tuple — both needed for media upload + posting."""
    from dotenv import dotenv_values
    creds = dotenv_values(brand.platform_credentials)
    slug = brand.brand_slug.replace("-", "_").upper()[:2]
    
    consumer_key = creds[f"X_CONSUMER_KEY_{slug}"]
    consumer_secret = creds[f"X_CONSUMER_SECRET_{slug}"]
    access_token = creds[f"X_ACCESS_TOKEN_{slug}"]
    access_secret = creds[f"X_ACCESS_SECRET_{slug}"]
    
    # v1.1 API — required for media upload (video)
    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret, access_token, access_secret
    )
    api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
    
    # v2 client — for posting tweets
    client_v2 = tweepy.Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_secret,
        wait_on_rate_limit=True,
    )
    
    return api_v1, client_v2


def post_to_x(
    brand: BrandConfig,
    project_path: Path,
    dry_run: bool = False,
) -> str:
    """
    Upload video and post tweet. Returns tweet ID.
    Uses v1.1 for media upload, v2 for tweet creation.
    """
    done_dir = project_path / "done"
    reel_path = done_dir / "reel.mp4"
    
    if not reel_path.exists():
        raise FileNotFoundError("done/reel.mp4 not found.")

    with open(done_dir / "captions.json") as f:
        captions = json.load(f)

    caption = captions["x"]

    # X hard limit: 280 chars
    if len(caption) > 280:
        caption = caption[:277] + "..."
        console.print("[yellow]⚠ X caption truncated to 280 chars[/yellow]")

    if dry_run:
        console.print(f"[yellow][DRY RUN] Would post to X:[/yellow] '{caption}'")
        return "dry_run_tweet_id"

    api_v1, client_v2 = _get_tweepy_clients(brand)

    # Step 1: Upload video via v1.1 chunked upload
    console.print("[cyan]Uploading video to X...[/cyan]")
    try:
        media = api_v1.media_upload(
            filename=str(reel_path),
            media_category="tweet_video",  # Required for video (non-gif)
            chunked=True,
        )
    except tweepy.TweepyException as e:
        raise RuntimeError(f"X media upload failed: {e}")

    # Step 2: Poll processing status
    media_id = media.media_id
    console.print(f"  Media ID: {media_id}. Waiting for processing...")
    
    for _ in range(60):  # Max 5 min
        try:
            status = api_v1.get_media_upload_status(media_id)
            proc = getattr(status, "processing_info", None)
            if proc is None:
                break  # No processing_info = already done
            state = proc.get("state", "pending")
            if state == "succeeded":
                break
            elif state == "failed":
                raise RuntimeError(f"X video processing failed: {proc}")
            wait = proc.get("check_after_secs", 5)
            console.print(f"  State: {state} — checking in {wait}s...")
            time.sleep(wait)
        except tweepy.TweepyException as e:
            console.print(f"[yellow]Status check error: {e}[/yellow]")
            time.sleep(5)
    else:
        raise TimeoutError("X video processing timed out after 5 minutes.")

    # Step 3: Post tweet with media
    console.print("[cyan]Posting tweet...[/cyan]")
    try:
        response = client_v2.create_tweet(
            text=caption,
            media_ids=[media_id],
        )
        tweet_id = response.data["id"]
    except tweepy.TweepyException as e:
        raise RuntimeError(f"X tweet creation failed: {e}")

    console.print(f"[bold green]✓ X tweet posted:[/bold green] {tweet_id}")
    console.print(f"  URL: https://x.com/i/web/status/{tweet_id}")

    # Update DB
    from djinn.brands import get_db
    conn = get_db(brand.brand_slug)
    conn.execute(
        "UPDATE content_days SET published_x=1, x_tweet_id=? WHERE project_path=?",
        (str(tweet_id), str(project_path)),
    )
    conn.commit()
    conn.close()

    return str(tweet_id)
```

### X Media Upload Notes
- The `media_category="tweet_video"` parameter is **required** for video files — without it, X treats the upload as a GIF and it will fail for MP4.
- `chunked=True` in `media_upload` enables Tweepy's automatic chunked upload — required for files >5MB (all Reels will be >5MB).
- The `get_media_upload_status` polling is not needed if `media.processing_info` is `None` — that means processing is instant (common for images, rare for videos).
- **OAuth 1.0a is required for media uploads.** OAuth 2.0 (Bearer Token) does not support the v1.1 media endpoint.

---

## 10. Module: `djinn.scheduler` — Publish Queue and systemd Timer

### `scheduler.py`
```python
# djinn/scheduler.py
"""
Runs every 15 minutes via systemd timer.
Scans all brand DBs for content with status='kit_ready' and scheduled publish time.
Fires the publish chain if it's time.
"""
import json
import logging
from datetime import datetime, time as dtime
from pathlib import Path

from djinn.brands import BrandConfig, get_db

logger = logging.getLogger("djinn.scheduler")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PUBLISH_SCHEDULE_PATH = Path.home() / ".config" / "djinn" / "publish-schedule.json"


def load_publish_schedule() -> dict:
    if not PUBLISH_SCHEDULE_PATH.exists():
        return {}
    with open(PUBLISH_SCHEDULE_PATH) as f:
        return json.load(f)


def run_scheduler():
    """Main scheduler loop — called by systemd timer every 15 minutes."""
    schedule = load_publish_schedule()
    now = datetime.now()
    current_day = now.strftime("%A").lower()
    current_time = now.strftime("%H:%M")
    
    # Find all brand configs
    config_dir = Path.home() / ".config" / "djinn" / "brands"
    brand_slugs = [
        p.stem for p in config_dir.glob("*.json")
        if not p.stem.endswith("-hashtags")
    ]
    
    for brand_slug in brand_slugs:
        try:
            brand = BrandConfig.load(brand_slug)
            conn = get_db(brand_slug)
            
            # Find content ready to publish today
            rows = conn.execute(
                """SELECT * FROM content_days
                   WHERE brand=? AND content_day=? AND status='kit_ready'
                   AND published_ig=0 AND published_yt=0 AND published_x=0
                   ORDER BY episode DESC LIMIT 1""",
                (brand_slug, current_day),
            ).fetchall()
            
            if not rows:
                continue
            
            # Check if it's scheduled publish time (±7 min window)
            brand_schedule = schedule.get(brand_slug, {})
            scheduled_time_str = brand_schedule.get(current_day)
            if not scheduled_time_str:
                continue
            
            scheduled_h, scheduled_m = map(int, scheduled_time_str.split(":"))
            scheduled_mins = scheduled_h * 60 + scheduled_m
            current_mins = now.hour * 60 + now.minute
            
            if abs(current_mins - scheduled_mins) <= 7:
                for row in rows:
                    project_path = Path(row["project_path"])
                    logger.info(f"Publishing {brand_slug}: {row['folder_slug']}")
                    _publish_project(brand, project_path, conn, row)
            
            conn.close()
        except Exception as e:
            logger.error(f"Scheduler error for {brand_slug}: {e}", exc_info=True)


def _publish_project(brand, project_path, conn, row):
    """Fire the full publish chain for a ready project."""
    from djinn.publish.meta import publish_project_to_meta
    from djinn.publish.youtube import upload_youtube_short
    from djinn.publish.x import post_to_x
    from djinn.media.caption import generate_captions

    # Start the local file server for Meta URL requirement
    from djinn.hosting import start_temp_server, stop_temp_server
    server, base_url = start_temp_server(project_path / "done")

    try:
        results = {}
        
        # Meta (IG + FB)
        results.update(
            publish_project_to_meta(
                project_path=project_path,
                brand=brand,
                platforms=["ig", "fb"],
                video_server_url=base_url,
            )
        )
        
        # YouTube
        yt_id = upload_youtube_short(brand=brand, project_path=project_path)
        results["yt_video_id"] = yt_id
        
        # X
        x_id = post_to_x(brand=brand, project_path=project_path)
        results["x_tweet_id"] = x_id
        
        logger.info(f"Published {row['folder_slug']}: {results}")
        
    finally:
        stop_temp_server(server)
```

### systemd Service and Timer
```ini
# scripts/djinn-publish-scheduler.service
[Unit]
Description=Djinn Social Publish Scheduler
After=network.target

[Service]
Type=oneshot
User=%i
ExecStart=/home/javier/projects/djinn-social/.venv/bin/python -m djinn.scheduler
WorkingDirectory=/home/javier/projects/djinn-social
Environment=PATH=/home/javier/projects/djinn-social/.venv/bin:/usr/local/bin:/usr/bin:/bin
StandardOutput=journal
StandardError=journal
```

```ini
# scripts/djinn-publish-scheduler.timer
[Unit]
Description=Run Djinn Publish Scheduler every 15 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
AccuracySec=30s

[Install]
WantedBy=timers.target
```

Install:
```bash
# Copy to systemd user directory
cp scripts/djinn-publish-scheduler.service ~/.config/systemd/user/
cp scripts/djinn-publish-scheduler.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now djinn-publish-scheduler.timer
# Verify
systemctl --user list-timers djinn*
```

---

## 11. Module: `djinn.tokens` — Token Lifecycle and Auto-Refresh

### Instagram Page Token Refresh
Instagram Page access tokens are non-expiring **if** obtained correctly (User token → Page token via Graph API). The User token expires in 60 days and must be refreshed to keep the Page token valid.

```python
# djinn/tokens.py
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import dotenv_values, set_key
from rich.console import Console

console = Console()

GRAPH_BASE = "https://graph.facebook.com/v21.0"


def refresh_instagram_long_lived_token(brand_slug: str) -> None:
    """
    Refreshes the long-lived User access token before it expires.
    Long-lived tokens expire in 60 days. Refresh before day 50.
    Can be refreshed as long as not expired and ≥24h old.
    """
    env_path = Path.home() / ".config" / "djinn" / f"meta-{brand_slug}.env"
    creds = dotenv_values(env_path)
    slug = brand_slug.replace("-", "_").upper()[:2]
    
    current_token = creds.get(f"META_USER_TOKEN_{slug}")
    if not current_token:
        console.print(f"[red]No user token found for {brand_slug}. Manual re-auth required.[/red]")
        return
    
    # Refresh endpoint — GET, not POST
    resp = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": current_token,
        },
    ).json()
    
    if "error" in resp:
        console.print(f"[red]Token refresh failed for {brand_slug}: {resp['error']}[/red]")
        console.print("Manual re-auth required. Run: djinn token-reauth --brand {brand_slug}")
        return
    
    new_token = resp["access_token"]
    expires_in = resp.get("expires_in", 5183944)  # ~60 days in seconds
    
    set_key(str(env_path), f"META_USER_TOKEN_{slug}", new_token)
    set_key(str(env_path), f"META_TOKEN_REFRESHED", datetime.now().isoformat())
    set_key(
        str(env_path),
        f"META_TOKEN_EXPIRES",
        (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
    )
    
    console.print(f"[green]✓ Instagram token refreshed for {brand_slug}[/green]")
    console.print(f"  New expiry: {(datetime.now() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d')}")


def check_token_health() -> None:
    """
    Checks all brand tokens for impending expiry.
    Called by Marcus in the morning briefing if configured.
    """
    config_dir = Path.home() / ".config" / "djinn" / "brands"
    brand_slugs = [p.stem for p in config_dir.glob("*.json") if not p.stem.endswith("-hashtags")]
    
    for brand_slug in brand_slugs:
        env_path = Path.home() / ".config" / "djinn" / f"meta-{brand_slug}.env"
        if not env_path.exists():
            continue
        creds = dotenv_values(env_path)
        expires_str = creds.get("META_TOKEN_EXPIRES")
        if not expires_str:
            console.print(f"[yellow]⚠ {brand_slug}: No token expiry recorded[/yellow]")
            continue
        expires = datetime.fromisoformat(expires_str)
        days_left = (expires - datetime.now()).days
        if days_left <= 10:
            console.print(f"[red]⚠ {brand_slug}: Token expires in {days_left} days — refresh NOW[/red]")
        elif days_left <= 20:
            console.print(f"[yellow]⚠ {brand_slug}: Token expires in {days_left} days[/yellow]")
        else:
            console.print(f"[green]✓ {brand_slug}: Token healthy ({days_left} days remaining)[/green]")
```

### Token Refresh Schedule
Add to cron / systemd timer to run every 45 days:
```bash
# ~/.config/systemd/user/djinn-token-refresh.service
[Unit]
Description=Djinn Instagram Token Refresh

[Service]
Type=oneshot
ExecStart=/home/javier/projects/djinn-social/.venv/bin/djinn token-refresh
```
```bash
# ~/.config/systemd/user/djinn-token-refresh.timer
[Unit]
Description=Refresh Djinn tokens every 45 days

[Timer]
OnCalendar=*-*-01 06:00:00  # First of every month at 6AM
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 12. CLI Entry Points — `djinn` Command Group

### `cli.py` — Full Click Command Group
```python
# djinn/cli.py
from datetime import date
from pathlib import Path

import click
from rich.console import Console

from djinn.brands import BrandConfig, get_db, insert_content_day

console = Console()


@click.group()
def cli():
    """Djinn Social Studio — multi-brand content pipeline."""
    pass


@cli.command("content-day-init")
@click.option("--brand", required=True, help="Brand slug (e.g. terp-tribe)")
@click.option("--date", "target_date", default=None, 
              help="YYYY-MM-DD (default: today)")
@click.option("--setup", is_flag=True, help="Initialize brand DB and folder structure")
def content_day_init(brand, target_date, setup):
    """Initialize a content day: create folders, DB entry, brand_context.json."""
    from djinn.media.ingest import ingest_files
    from djinn.brands import DJINN_BRANDS_DATA_DIR
    
    brand_config = BrandConfig.load(brand)
    d = date.fromisoformat(target_date) if target_date else date.today()
    
    if setup:
        brand_config.base_folder.mkdir(parents=True, exist_ok=True)
        DJINN_BRANDS_DATA_DIR.mkdir(parents=True, exist_ok=True)
        conn = get_db(brand)
        conn.close()
        console.print(f"[green]✓ Brand {brand} initialized[/green]")
        return
    
    manifest = ingest_files(brand=brand_config, target_date=d)
    console.print(f"\n[bold]Project created:[/bold] {manifest['folder_slug']}")
    console.print(f"  Path: {brand_config.base_folder / d.strftime('%A').capitalize() / manifest['folder_slug']}")


@cli.command("media-ingest")
@click.option("--brand", required=True)
@click.option("--date", "target_date", default=None)
@click.option("--source", default=None, help="Source directory (default: ~/djinn-media-inbox)")
@click.option("--move", is_flag=True, help="Move files (delete from source) instead of copying")
def media_ingest(brand, target_date, source, move):
    """Ingest media files from inbox into project folder."""
    from djinn.media.ingest import ingest_files, INBOX
    brand_config = BrandConfig.load(brand)
    d = date.fromisoformat(target_date) if target_date else date.today()
    source_dir = Path(source) if source else INBOX
    ingest_files(brand=brand_config, target_date=d, source_dir=source_dir, move=move)


@cli.command("media-reel")
@click.argument("project_path")
@click.option("--video-file", default=None, help="Specific video file to use")
@click.option("--thumb-offset", default=1.5, type=float, help="Seconds into video for cover frame")
@click.option("--burn-subs", is_flag=True, help="Burn subtitles from transcription.srt")
@click.option("--crf", default=20, type=int, help="H.264 CRF quality (lower=higher quality)")
def media_reel(project_path, video_file, thumb_offset, burn_subs, crf):
    """Build 9:16 reel.mp4 and cover.jpg from project video."""
    from djinn.media.reel import build_reel
    p = Path(project_path)
    vf = Path(video_file) if video_file else None
    result = build_reel(p, video_file=vf, thumb_offset=thumb_offset,
                        burn_subtitles=burn_subs, crf=crf)
    console.print(f"\n[bold]Reel output:[/bold] {result['reel']}")


@cli.command("media-transcribe")
@click.argument("project_path")
@click.option("--model", default="small", 
              type=click.Choice(["tiny", "base", "small", "medium", "large-v3-turbo"]))
def media_transcribe(project_path, model):
    """Transcribe reel.mp4 with faster-whisper."""
    from djinn.media.transcribe import transcribe_reel
    result = transcribe_reel(Path(project_path), model_size=model)
    console.print(f"\n[bold]Transcript:[/bold] {result['text'][:200]}...")


@cli.command("media-caption")
@click.argument("project_path")
@click.option("--model", default="qwen2.5:14b", help="Ollama model to use")
def media_caption(project_path, model):
    """Generate all platform captions via Ollama."""
    from djinn.media.caption import generate_captions
    generate_captions(Path(project_path), model=model)


@cli.command("media-publish")
@click.argument("project_path")
@click.option("--brand", required=True)
@click.option("--platform", multiple=True, 
              type=click.Choice(["ig", "fb", "yt", "x"]),
              help="Platforms to publish to (can specify multiple)")
@click.option("--dry-run", is_flag=True, help="Print what would be published without doing it")
def media_publish(project_path, brand, platform, dry_run):
    """Publish project to specified platforms."""
    from djinn.publish.meta import publish_project_to_meta
    from djinn.publish.youtube import upload_youtube_short
    from djinn.publish.x import post_to_x
    from djinn.hosting import start_temp_server, stop_temp_server
    
    brand_config = BrandConfig.load(brand)
    p = Path(project_path)
    platforms = list(platform) if platform else ["ig", "fb", "yt", "x"]
    
    # Start local file server for Meta uploads
    server, base_url = None, None
    if "ig" in platforms or "fb" in platforms:
        server, base_url = start_temp_server(p / "done")
    
    try:
        if "ig" in platforms or "fb" in platforms:
            publish_project_to_meta(
                project_path=p,
                brand=brand_config,
                platforms=[pl for pl in platforms if pl in ("ig", "fb")],
                video_server_url=base_url,
                dry_run=dry_run,
            )
        if "yt" in platforms:
            upload_youtube_short(brand=brand_config, project_path=p, dry_run=dry_run)
        if "x" in platforms:
            post_to_x(brand=brand_config, project_path=p, dry_run=dry_run)
    finally:
        if server:
            stop_temp_server(server)


@cli.command("content-find")
@click.option("--brand", required=True)
@click.option("--theme", default=None)
@click.option("--season", default=None, type=int)
@click.option("--status", default=None)
def content_find(brand, theme, season, status):
    """Query content DB for matching projects."""
    conn = get_db(brand)
    query = "SELECT * FROM content_days WHERE brand=?"
    params = [brand]
    if theme:
        query += " AND theme_name LIKE ?"
        params.append(f"%{theme}%")
    if season:
        query += " AND season=?"
        params.append(season)
    if status:
        query += " AND status=?"
        params.append(status)
    query += " ORDER BY episode DESC"
    rows = conn.execute(query, params).fetchall()
    if not rows:
        console.print("[yellow]No results found[/yellow]")
        return
    for row in rows:
        console.print(f"  [{row['status']}] {row['folder_slug']} → {row['project_path']}")
    conn.close()


@cli.command("token-refresh")
@click.option("--brand", default=None, help="Specific brand (default: all brands)")
def token_refresh(brand):
    """Refresh Instagram long-lived tokens."""
    from djinn.tokens import refresh_instagram_long_lived_token, check_token_health
    if brand:
        refresh_instagram_long_lived_token(brand)
    else:
        config_dir = Path.home() / ".config" / "djinn" / "brands"
        for p in config_dir.glob("*.json"):
            if not p.stem.endswith("-hashtags"):
                refresh_instagram_long_lived_token(p.stem)
    check_token_health()
```

---

## 13. Hosting: Publicly Accessible Video URL for Meta

### The Problem
Instagram Graph API cannot accept file uploads directly. The `video_url` parameter in the container creation call must be a **publicly accessible HTTPS URL** that Meta's servers can fetch. Salomon is a home machine — no public IP.

### Solution A: Temporary ngrok Tunnel (Recommended for Dev/Testing)
```python
# djinn/hosting.py
import subprocess
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os


def start_temp_server(
    directory: Path,
    port: int = 8741,
) -> tuple:
    """
    Starts a local HTTP server on the given directory.
    Returns (server_thread, base_url).
    Requires: ngrok authtoken configured (ngrok config add-authtoken <token>)
    """
    os.chdir(directory)
    
    handler = SimpleHTTPRequestHandler
    handler.log_message = lambda *args: None  # Suppress access logs
    httpd = HTTPServer(("", port), handler)
    
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    # Start ngrok tunnel
    ngrok_proc = subprocess.Popen(
        ["ngrok", "http", str(port), "--log=false"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)  # Wait for ngrok to initialize
    
    # Get public URL from ngrok API
    import requests as req
    tunnels = req.get("http://localhost:4040/api/tunnels").json()
    public_url = tunnels["tunnels"][0]["public_url"]
    
    return (httpd, ngrok_proc), public_url


def stop_temp_server(server_tuple) -> None:
    httpd, ngrok_proc = server_tuple
    httpd.shutdown()
    ngrok_proc.terminate()
```

### Solution B: Cloudflare Tunnel (Production — Recommended)
Cloudflare Tunnel (formerly Argo Tunnel) provides a permanent, free, authenticated HTTPS tunnel:
```bash
# One-time setup
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel login
cloudflared tunnel create djinn-media
cloudflared tunnel route dns djinn-media media.djinn-internal.com

# Start tunnel (add to systemd)
cloudflared tunnel --url http://localhost:8741 run djinn-media
```

Then the base URL is always `https://media.djinn-internal.com` — no ngrok startup delay.

```python
# When using Cloudflare Tunnel:
DJINN_MEDIA_BASE_URL = "https://media.djinn-internal.com"
# The local HTTP server serves from done/ directory on port 8741
# Meta fetches from https://media.djinn-internal.com/reel.mp4
```

### Solution C: Upload to R2/S3 Bucket (For Scale)
```python
import boto3
def upload_to_r2(file_path: Path, bucket: str, key: str) -> str:
    """Upload to Cloudflare R2 (S3-compatible), return public URL."""
    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
    )
    s3.upload_file(str(file_path), bucket, key, ExtraArgs={"ACL": "public-read"})
    return f"https://pub-{BUCKET_HASH}.r2.dev/{key}"
```

**Recommendation for Djinn:** Start with ngrok for testing, migrate to Cloudflare Tunnel once the pipeline is stable. The tunnel stays running as a systemd service — no per-publish setup.

---

## 14. Environment Files and Secrets Layout

### Complete File Structure
```
~/.config/djinn/
├── brands/
│   ├── terp-tribe.json        # Brand config (non-secret)
│   ├── typhon-forge.json      # Brand config (non-secret)
│   ├── terp-tribe-hashtags.txt  # One hashtag per line
│   └── typhon-forge-hashtags.txt
├── meta-terp-tribe.env        # chmod 600 — NEVER commit to git
├── meta-typhon-forge.env      # chmod 600 — NEVER commit to git
└── publish-schedule.json      # Non-secret scheduling config
```

### `meta-terp-tribe.env` Template
```env
# Instagram
IG_USER_ID_TT=<instagram_business_account_id>
META_PAGE_TOKEN_TT=<long_lived_page_access_token>
META_USER_TOKEN_TT=<long_lived_user_access_token>
FB_PAGE_ID_TT=<facebook_page_id>
META_TOKEN_REFRESHED=2026-06-01T00:00:00
META_TOKEN_EXPIRES=2026-07-31T00:00:00

# YouTube
YT_CLIENT_ID_TT=<google_oauth_client_id>
YT_CLIENT_SECRET_TT=<google_oauth_client_secret>
YT_REFRESH_TOKEN_TT=<youtube_refresh_token_from_setup_script>

# X/Twitter
X_CONSUMER_KEY_TT=<x_api_consumer_key>
X_CONSUMER_SECRET_TT=<x_api_consumer_secret>
X_ACCESS_TOKEN_TT=<x_oauth1_access_token>
X_ACCESS_SECRET_TT=<x_oauth1_access_token_secret>
```

```bash
# Lock down permissions immediately after creation
chmod 600 ~/.config/djinn/meta-*.env
```

### `publish-schedule.json`
```json
{
  "terp-tribe": {
    "monday":    "10:30",
    "tuesday":   "11:00",
    "wednesday": "11:00",
    "thursday":  "10:30",
    "friday":    "10:00",
    "saturday":  "11:30",
    "sunday":    "12:00"
  },
  "typhon-forge": {
    "monday":    "11:00",
    "tuesday":   "11:30",
    "wednesday": "12:00",
    "thursday":  "12:00",
    "friday":    "11:00",
    "saturday":  "13:00",
    "sunday":    "14:00"
  }
}
```

---

## 15. Error Handling Patterns and Retry Logic

### Meta API Error Code Reference
| Error Code | Subcode | Meaning | Action |
|------------|---------|---------|--------|
| 400 | — | Container not FINISHED when publishing | Add polling loop; wait |
| 2207001 | — | Server-side upload failure | Retry 1–2× with new container |
| 9 | 2207042 | Publishing rate limit exceeded | Check `content_publishing_limit`; wait |
| 190 | — | Token expired or invalid | Trigger token refresh flow |
| 100 | — | Invalid parameter | Check video_url accessibility, codec |
| 4 | — | App-level rate limit | Exponential backoff |

### Universal Retry Decorator
```python
# djinn/utils.py
import time
import functools
import logging

logger = logging.getLogger("djinn")


def retry_on_error(max_attempts=3, delay_seconds=5, backoff=2.0, 
                   retry_on=(Exception,), log_prefix=""):
    """Decorator for exponential backoff retry."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exc = e
                    wait = delay_seconds * (backoff ** attempt)
                    logger.warning(
                        f"{log_prefix}{func.__name__} failed "
                        f"(attempt {attempt+1}/{max_attempts}): {e}. "
                        f"Retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)
            raise last_exc
        return wrapper
    return decorator


# Usage:
# @retry_on_error(max_attempts=3, delay_seconds=10, log_prefix="[Meta] ")
# def upload_instagram_reel(...):
```

### Error Recovery Patterns
```python
# Common error patterns and recovery strategy

# Meta 190 (token expired)
if resp.get("error", {}).get("code") == 190:
    from djinn.tokens import refresh_instagram_long_lived_token
    refresh_instagram_long_lived_token(brand.brand_slug)
    # Reload token and retry once
    raise TokenExpiredError("Token expired — refreshed, retry once")

# Container stuck in IN_PROGRESS > 5 min
# → Create a new container (do NOT retry the same one)
# → Log: "Container {id} timed out. Creating new container."

# YouTube quota exceeded
# → Log error with quota reset time (midnight Pacific)
# → Set status = "yt_quota_exceeded" in DB
# → Retry next day automatically via scheduler

# X media upload fails on first attempt
# → Check file size (< 512MB for X)
# → Check codec (must be H.264, not HEVC)
# → If both OK, wait 30s and retry with new upload session
```

---

## 16. Full End-to-End Run Sequence

### Manual Run (Today's Content)
```bash
# 1. Javier drops files into ~/djinn-media-inbox/
#    (iPhone Shortcut does this automatically via iCloud → rclone sync)

# 2. Initialize content day and ingest files
djinn-media-ingest --brand terp-tribe --move

# 3. Build 9:16 reel
# (project_path printed by step 2)
djinn-media-reel ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday

# 4. Transcribe (optional but recommended for caption quality)
djinn-media-transcribe ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday

# 5. Generate captions
djinn-media-caption ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday

# 6. Review captions in done/ folder
cat ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday/done/caption_ig.txt
# Edit if needed

# 7. Mark as kit_ready (enables scheduler auto-publish)
djinn content-day-set-status ~/Terp\ Tribe/Wednesday/... kit_ready

# OR: Publish immediately
djinn-media-publish ~/Terp\ Tribe/Wednesday/S6_E14_W2_Wax-Wednesday \
  --brand terp-tribe \
  --platform ig --platform fb --platform yt --platform x

# 8. Verify
djinn content-find --brand terp-tribe --status published
```

### Marcus-Triggered Run via Telegram
When Marcus detects new files in inbox and it's a content day:
```
Marcus → Javier (Telegram):
"📦 4 files in your inbox (2 videos, 2 photos). 
Today is Wax Wednesday — S6_E14. 
Start ingest? Reply YES to auto-run the full pipeline."

Javier → "YES"

Marcus:
- Runs: djinn-media-ingest → djinn-media-reel → djinn-media-transcribe → djinn-media-caption
- Sends preview: "Reel built. Caption preview:
  IG: When the dab hits just right... [click to see full]
  X: The terp stack speaks for itself 🔥
  Accept captions? Reply YES to schedule, EDIT to revise."

Javier → "YES"
Marcus → Sets status=kit_ready → scheduler fires at 11:00
```

The Telegram integration hooks into `djinn.cli` commands via `subprocess.run` or direct function calls.

---

## 17. Installation and First-Run Checklist

### System Dependencies (Ubuntu/Fedora)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
  ffmpeg \
  libheif-examples \
  python3.11 \
  python3.11-venv \
  libffi-dev

# Verify
ffmpeg -version | head -1
heif-convert --version
```

### Python Environment
```bash
cd ~/projects/djinn-social
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"  # Installs in editable mode with dev extras

# Verify CLI
djinn --help
djinn-media-ingest --help
```

### One-Time Setup Per Brand
```bash
# 1. Create brand config
cp configs/brands/terp-tribe.json.example ~/.config/djinn/brands/terp-tribe.json
# Edit: season_start_date, base_folder, telegram_bot

# 2. Create credential file
cp configs/meta.env.example ~/.config/djinn/meta-terp-tribe.env
chmod 600 ~/.config/djinn/meta-terp-tribe.env
# Fill in: IG_USER_ID_TT, META_PAGE_TOKEN_TT, FB_PAGE_ID_TT, etc.

# 3. Initialize brand DB and folder structure
djinn-content-day-init --brand terp-tribe --setup

# 4. YouTube OAuth (browser required, one-time)
python scripts/youtube_oauth_setup.py \
  --brand terp-tribe \
  --client-secrets ~/google-client-secrets.json

# 5. Test with dry run
djinn-media-publish <project_path> --brand terp-tribe --dry-run

# 6. Install systemd timer
cp scripts/djinn-publish-scheduler.service ~/.config/systemd/user/
cp scripts/djinn-publish-scheduler.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now djinn-publish-scheduler.timer
```

### Meta App Review Requirements
Before the Instagram and Facebook API will work for accounts Javier doesn't own:
1. Meta Developer Account: `developers.facebook.com`
2. Create App → Business use case
3. Add Instagram product
4. Request permissions: `instagram_business_basic`, `instagram_business_content_publish`
5. Record screencasts of the upload flow (use test account during dev)
6. Submit for app review — expect 2–4 weeks
7. **For Javier's own accounts:** Dev mode is sufficient — no app review needed

---

## 18. Open Items and Known Gotchas

### Blockers Before Build
1. **Meta App Review:** Required to publish to non-test IG accounts. Start the submission immediately — it takes 2–4 weeks. Use test/dev accounts until approved.
2. **YouTube One-Time OAuth:** Must be done in a browser environment with the `youtube_oauth_setup.py` script. Cannot be automated headlessly the first time.
3. **X API Billing:** X's new pay-per-use model requires a credit card on file at `developer.x.com`. Add $5–10 to start.
4. **Cloudflare Tunnel vs ngrok:** Decide which hosting approach before build. Cloudflare Tunnel is free and permanent; ngrok free tier has random URLs and session limits.
5. **Brand configs confirmation:** Typhon's Forge day themes are placeholders. Javier must confirm the actual weekly schedule before `djinn-content-day-init` is built.
6. **Season 6 start date:** Used for all week_in_season calculations. Confirm exact date.

### Known API Gotchas
| Platform | Gotcha | Notes |
|----------|--------|-------|
| Instagram | `video_url` must be HTTPS, not HTTP | ngrok provides HTTPS; local HTTP server won't work |
| Instagram | `-use_editlist 0` required in ffmpeg | iPhone HEVC containers have edit lists |
| Instagram | Creator accounts blocked from API publishing | Account must be set to Business type |
| Instagram | 100MB file size limit for standard flow | Resumable upload needed for larger files |
| Facebook | FB API returns 200 for video upload but async processes | Check video status via `/{video_id}?fields=status` |
| YouTube | `videos.insert` requires OAuth, not Service Account | No workaround — must do browser OAuth once |
| YouTube | New projects require audit for public uploads | New Google Cloud project videos default to private |
| X | OAuth 1.0a required for v1.1 media endpoint | OAuth 2.0 Bearer Token does not work for video upload |
| X | `media_category="tweet_video"` required | Without it: upload succeeds but playback fails |
| Ollama | JSON mode not available on all models | Test `response_format` before relying on it |
| faster-whisper | `vad_filter=True` prevents hallucination in silence | Always enable for social content with ambient audio |

### Cannabis Brand IG/FB Safety Rules (Critical)
- Words that trigger enforcement (never use in captions): `weed`, `cannabis`, `420`, `marijuana`, `thc`, `cbd`, `buy`, `sale`, `order`, `delivery`, `menu`, `price`
- Instagram uses automated enforcement with no warning — shadowban can persist 90–120 days
- Safe framing: education, lifestyle, culture, community — NOT sales, promotions, menus
- No prices in any content. No "DM for info" (implies sales). No "Available now"
- The caption agent has these rules hardcoded — but manually review before publishing

### File Size Budget
| File | Typical Size | Platform Limit |
|------|-------------|----------------|
| reel.mp4 (CRF 20, 60s) | 30–80 MB | IG: 100MB, X: 512MB |
| reel.mp4 (CRF 24, 60s) | 15–40 MB | All platforms: ✓ |
| cover.jpg | 200–500 KB | All platforms: ✓ |
| transcription.srt | <50 KB | N/A |
| brand_context.json | <10 KB | N/A |

If `reel.mp4` exceeds 95MB: re-run `djinn-media-reel` with `--crf 24` (minor quality reduction, dramatic size reduction).

---

*Researched and written by Marcus | 2026-06-01 | Task: TASK-061*
*This is the build document. Claude implements directly from this specification.*
*TASK-060 is the research foundation. Read TASK-060 first if context is needed.*
