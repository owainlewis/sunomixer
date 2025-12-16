# Sunomix: Automated AI Music Mix Pipeline

> A fully automated system that generates long-form YouTube music mixes using AI-generated tracks, from generation to upload—requiring zero human intervention.

## Overview

Sunomix is a automation pipeline that generates complete YouTube-ready music videos with a single command. The system orchestrates multiple AI services, audio processing, and video composition to produce 90+ minute deep work/focus music mixes that are automatically uploaded to YouTube.

**Benefit:** What would take a human producer many hours of work is fully automated into a ~10 minute pipeline that can run daily without intervention.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SUNOMIX PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                │
│   │   Suno API   │     │  Audio Mix   │     │   FFmpeg     │                │
│   │   (Tracks)   │────▶│  (pydub)     │────▶│   (Video)    │────▶ YouTube   │
│   └──────────────┘     └──────────────┘     └──────────────┘                │
│          │                                         ▲                         │
│          │              ┌──────────────┐           │                         │
│          └──────────────│   Gemini     │───────────┘                         │
│                         │  (Thumbnail) │                                     │
│                         └──────────────┘                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## System Architecture

### High-Level Design

The system follows a 5-phase pipeline architecture optimized for parallel execution:

| Phase | Description | Duration |
|-------|-------------|----------|
| **1. Initialization** | Load genre preset, generate track titles | ~5 sec |
| **2. Parallel Generation** | Generate N tracks via Suno + thumbnail via Gemini | ~5 min |
| **3. Download & Mix** | Fetch audio files, normalize, crossfade | ~90 sec |
| **4. Video Composition** | Combine thumbnail + audio into MP4 | ~3 min |
| **5. Upload** | Push to YouTube with SEO metadata | ~2 min |

**Total time for a 90-minute, 10-track mix: ~10 minutes**

### Why Parallel Execution Matters

The critical insight driving the architecture is that Suno track generation is the bottleneck:

- **Sequential:** 10 tracks × 3 min/track = 30+ minutes
- **Parallel:** 10 tracks simultaneously = ~5 minutes (limited by slowest track)

This 6x speedup is achieved using `asyncio.gather()` with semaphore-based rate limiting:

```python
async def generate_tracks_parallel(self, requests: list[TrackRequest]) -> list[TrackResult]:
    semaphore = asyncio.Semaphore(self.config.max_concurrent)  # 10 concurrent

    async def limited_task(request):
        async with semaphore:
            return await self.generate_track_and_wait(request)

    tasks = [limited_task(req) for req in requests]
    return await asyncio.gather(*tasks)
```

## Component Deep Dive

### 1. Suno API Integration (`suno/client.py`)

The Suno client handles all interactions with the Suno music generation API:

```
POST /api/v1/generate     → Submit generation task
GET  /api/v1/record-info  → Poll for completion
```

**Key Features:**
- Async HTTP client with connection pooling
- Automatic status polling with configurable intervals (30s default)
- 10-minute timeout per track with graceful error handling
- Support for instrumental mode with negative tags (no vocals)

**Generation Request:**
```python
TrackRequest(
    prompt="Dreamy 80s synthwave with nostalgic emotional vibes...",
    style="80s synthwave, dreamy retrowave, nostalgic outrun",
    title="Neon Highway Dreams",
    negative_tags="vocals, singing, harsh, aggressive"
)
```

### 2. Audio Processing (`audio/`)

**Downloader:** Parallel MP3 fetching with semaphore limiting (5 concurrent)
```python
await download_tracks(
    urls=[track.audio_url for track in tracks],
    output_dir=temp_dir,
    max_concurrent=5
)
```

**Mixer:** Professional audio chain using pydub
- Volume normalization to -14 LUFS (broadcast standard)
- Configurable crossfade transitions (3s default)
- 320kbps MP3 output

```python
# Crossfade mixing
for track in tracks[1:]:
    normalized = normalize(load_track(track), target_dbfs=-14)
    mixed = mixed.append(normalized, crossfade=3000)
```

### 3. Thumbnail Generation (`thumbnail/generator.py`)

Two-tier approach for reliability and cost optimization:

1. **Asset-based (preferred):** Random selection from pre-generated images
2. **AI-generated (fallback):** Gemini 2.0 Flash for prompt → image generation

The AI thumbnails follow a specific aesthetic: cinematic dark workspaces, soft ambient lighting, no text, no faces—optimized for the deep work/focus music niche.

### 4. Video Composition (`video/composer.py`)

FFmpeg-based video creation with professional text overlays:

```bash
ffmpeg -loop 1 -i thumbnail.png -i audio.mp3 \
    -vf "fade=t=in:st=0:d=2" \
    -c:v libx264 -preset medium -crf 18 \
    -c:a aac -b:a 320k \
    -pix_fmt yuv420p -shortest -r 30 \
    output.mp4
```

**Text Overlay Features:**
- Custom letter spacing for premium "tracked out" look
- Gaussian blur glow effect
- Drop shadow with configurable offset
- Adaptive font sizing to fit within margins
- Font fallback chain: Montserrat-Black → Arial Black → system

### 5. YouTube Integration (`youtube/client.py`)

OAuth2-authenticated upload with resumable chunked transfers:

```python
# Metadata generation
metadata = {
    "title": "Peak Performance: Deep Work Music for Coding | Dreamy Synthwave",
    "description": generate_youtube_description(mood, genre, tracks),
    "tags": ["deep work", "coding music", "focus", "synthwave", ...],
    "categoryId": "10"  # Music
}

# Resumable upload (1MB chunks)
media = MediaFileUpload(video_path, mimetype="video/mp4",
                         resumable=True, chunksize=1024*1024)
```

## Genre Presets

Six carefully tuned presets optimized for deep work/focus content:

| Genre | BPM | Character |
|-------|-----|-----------|
| **Dark Synthwave** | 92 | 80s nostalgia, neon-lit drives |
| **Deep House** | 110 | Warm, hypnotic grooves |
| **Ambient Electronic** | 70 | Peaceful, meditative |
| **Lo-Fi Beats** | 85 | Dusty, jazzy, nostalgic |
| **Minimal Techno** | 100 | Repetitive, hypnotic |
| **Neo Classical** | 75 | Cinematic piano, strings |

Each preset includes:
- Optimized prompt text (5000 char limit)
- Style tags for consistent output
- Negative tags to exclude vocals
- BPM for energy consistency

## Project Structure

```
suno-mixer/
├── src/suno_mixer/
│   ├── pipeline/
│   │   └── orchestrator.py    # MixPipeline - main coordinator
│   ├── suno/
│   │   └── client.py          # Async Suno API client
│   ├── audio/
│   │   ├── downloader.py      # Parallel MP3 fetching
│   │   └── mixer.py           # Crossfade mixing + normalization
│   ├── thumbnail/
│   │   └── generator.py       # Gemini-based image generation
│   ├── video/
│   │   └── composer.py        # FFmpeg video composition
│   ├── youtube/
│   │   └── client.py          # OAuth2 upload client
│   ├── metadata/
│   │   └── youtube.py         # SEO title/description generation
│   ├── titles/
│   │   └── generator.py       # AI track title generation
│   ├── models.py              # 21 Pydantic data models
│   ├── config.py              # Pydantic settings (6 configs)
│   ├── presets.py             # Genre presets + mood words
│   └── cli.py                 # Click CLI interface
├── assets/thumbnails/         # Pre-generated images
├── output/                    # Generated videos
└── temp/                      # Working directory
```

## Data Flow

```
Input: mood="FOCUS", genre="dark_synthwave", tracks=10

    ┌─────────────────────────────────────────────────────────────┐
    │                    PHASE 1: INIT                             │
    │  Load preset → Generate 10 unique track titles via Gemini   │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │               PHASE 2: PARALLEL GENERATION                   │
    │                                                              │
    │   ┌──────────┐  ┌──────────┐       ┌──────────┐             │
    │   │ Track 1  │  │ Track 2  │  ...  │ Track 10 │   (parallel)│
    │   └──────────┘  └──────────┘       └──────────┘             │
    │                       │                                      │
    │              ┌────────┴────────┐                            │
    │              │   Thumbnail     │              (parallel)    │
    │              └─────────────────┘                            │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                  PHASE 3: DOWNLOAD & MIX                     │
    │  Fetch 10 MP3s (parallel) → Normalize → Crossfade → Export  │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                  PHASE 4: VIDEO COMPOSE                      │
    │  Add text overlay to thumbnail → FFmpeg encode → MP4        │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                  PHASE 5: UPLOAD                             │
    │  Generate SEO metadata → OAuth2 auth → Resumable upload     │
    └─────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
Output: YouTube video URL + local artifacts
```

## Output Artifacts

Each run produces a timestamped directory:

```
output/focus_dark_synthwave_20251202_162747/
├── focus_dark_synthwave_20251202_162747.mp4       # Final video (H.264/AAC)
├── focus_dark_synthwave_20251202_162747.mp3       # Mixed audio (320kbps)
├── focus_dark_synthwave_20251202_162747_thumb.png # Original thumbnail
├── focus_dark_synthwave_20251202_162747_yt_thumb.png # With text overlay
└── focus_dark_synthwave_20251202_162747.json      # Full metadata
```

**Metadata JSON:**
```json
{
  "title": "Peak Performance: Deep Work Music for Coding | Dreamy Synthwave",
  "description": "90 minutes of Dreamy Synthwave...",
  "tags": ["deep work", "coding music", "focus", ...],
  "hashtags": ["#DeepWork", "#CodingMusic", ...],
  "mood": "FOCUS",
  "genre": "dark_synthwave",
  "bpm": 92,
  "track_count": 10,
  "total_duration_seconds": 5432.5,
  "tracks": [
    {"title": "Neon Highway Dreams", "duration": 198.44},
    {"title": "Distant Memories Glow", "duration": 210.12},
    ...
  ],
  "generated_at": "2025-12-02T16:27:47Z"
}
```

## Usage

### Single Command Generation
```bash
suno-mixer generate --mood "FOCUS" --genre dark_synthwave --tracks 10
```

### Upload to YouTube
```bash
suno-mixer publish output/focus_dark_synthwave_20251202 --privacy public
```

### List Available Options
```bash
suno-mixer list genres  # Show 6 presets with BPM
suno-mixer list moods   # Show 20 mood words (FOCUS, FLOW, GRIND, etc.)
```

## Configuration

Environment-based configuration via `.env`:

```bash
SUNO_API_KEY=sk-...           # Suno API key
GEMINI_API_KEY=AIza...        # Google Gemini key
YOUTUBE_CLIENT_SECRETS_PATH=./credentials.json
```

All settings are type-safe via Pydantic:

```python
class SunoConfig(BaseSettings):
    api_key: str
    base_url: str = "https://api.sunoapi.org/api/v1"
    model: str = "V5"
    poll_interval_seconds: int = 30
    timeout_seconds: int = 600
    max_concurrent: int = 10
```

## Key Design Decisions

### 1. Async-First Architecture
Every I/O operation is async, enabling true parallelism without threading complexity.

### 2. Hardcoded Presets Over Dynamic Prompts
Presets ensure consistent quality and avoid per-track API costs for prompt generation.

### 3. Two-Tier Thumbnail Strategy
Pre-generated assets eliminate API latency/cost; Gemini fallback ensures reliability.

### 4. Pydantic Throughout
Type-safe data models with validation catch errors early and provide clear API contracts.

### 5. Resumable YouTube Uploads
Chunked upload protocol handles large files and network interruptions gracefully.

## Dependencies

| Package | Purpose |
|---------|---------|
| `aiohttp` | Async HTTP for Suno API |
| `pydub` | Audio processing |
| `Pillow` | Image manipulation |
| `click` + `rich` | CLI interface |
| `google-genai` | Gemini API |
| `google-api-python-client` | YouTube API |
| `pydantic` | Data validation |

**System Requirements:**
- Python 3.11+
- FFmpeg (for video composition)

## Performance Characteristics

| Metric | Value |
|--------|-------|
| 10-track mix generation | ~5 minutes |
| Full pipeline (generate → upload) | ~10 minutes |
| Output video quality | 1080p, CRF 18 (~8 Mbps) |
| Audio quality | 320kbps MP3 |
| Concurrent Suno requests | 10 (configurable) |
| Concurrent downloads | 5 (configurable) |

## Future Considerations

- **Scheduling:** Cron/Airflow integration for daily automated runs
- **Multi-channel:** Support for multiple YouTube channels
- **Analytics:** Track video performance for optimization
- **A/B Testing:** Compare thumbnail/title effectiveness
- **Web Dashboard:** Visual interface for non-technical users

---

*Built for 100% automated daily operation with zero human intervention.*
