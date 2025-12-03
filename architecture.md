# Suno Mixer Architecture

## Overview

Suno Mixer is an AI-powered pipeline that generates YouTube-ready focus music videos from a simple mood + genre input. It orchestrates multiple AI services and processing stages into a fully automated workflow.

**Core Purpose**: Convert a user request (mood + genre) into a complete YouTube video with:
- AI-generated music tracks from Suno API
- AI-generated or curated thumbnail images
- Mixed audio with configurable transitions
- Video composition with text overlay
- YouTube-optimized metadata

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INPUT                                     │
│                      CLI: suno-mixer generate                               │
│                   --mood FOCUS --genre dark_synthwave                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PIPELINE ORCHESTRATOR                               │
│                    (pipeline/orchestrator.py)                               │
│                                                                             │
│  Coordinates 6 phases, manages temp/output dirs, progress callbacks         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
┌───────────────┐           ┌─────────────────┐           ┌─────────────────┐
│   PHASE 1     │           │    PHASE 2a     │           │    PHASE 2b     │
│               │           │   (parallel)    │           │   (parallel)    │
│ Title Gen     │           │  Track Gen      │           │  Thumbnail Gen  │
│               │           │                 │           │                 │
│ ┌───────────┐ │           │ ┌─────────────┐ │           │ ┌─────────────┐ │
│ │  Gemini   │ │           │ │  Suno API   │ │           │ │Pre-generated│ │
│ │   API     │ │           │ │  (V5 Model) │ │           │ │   Assets    │ │
│ └───────────┘ │           │ └─────────────┘ │           │ └──────┬──────┘ │
│       │       │           │       │         │           │        │        │
│       ▼       │           │       ▼         │           │   OR   ▼        │
│  [10 Titles]  │           │ Poll until done │           │ ┌─────────────┐ │
│               │           │ (30s interval)  │           │ │   Gemini    │ │
└───────────────┘           │       │         │           │ │  Image Gen  │ │
                            │       ▼         │           │ └─────────────┘ │
                            │ [10 Audio URLs] │           └─────────────────┘
                            └─────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 3                                        │
│                         Audio Downloader                                    │
│                      (audio/downloader.py)                                  │
│                                                                             │
│              Async parallel download (5 concurrent) → 10 MP3s               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 4                                        │
│                           Audio Mixer                                       │
│                        (audio/mixer.py)                                     │
│                                                                             │
│     Load tracks → Normalize (-14 dBFS) → Cut/Crossfade → Export MP3        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 5                                        │
│                         Video Composer                                      │
│                       (video/composer.py)                                   │
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │  Text Overlay    │    │   FFmpeg Encode  │    │      Outputs         │  │
│  │  (PIL/Pillow)    │───▶│   (H.264/AAC)    │───▶│  • video.mp4         │  │
│  │  • Auto-resize   │    │   • 1080p/30fps  │    │  • yt_thumb.png      │  │
│  │  • Glow/Shadow   │    │   • 2s fade-in   │    │                      │  │
│  └──────────────────┘    └──────────────────┘    └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PHASE 6                                        │
│                        Metadata Generator                                   │
│                       (metadata/youtube.py)                                 │
│                                                                             │
│           Title + Description (w/ timestamps) + Tags + Hashtags            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT DIRECTORY                                    │
│                   output/{mood}_{genre}_{timestamp}/                        │
│                                                                             │
│    ├── mix.mp4              (Final video - clean image)                    │
│    ├── mix.mp3              (Mixed audio)                                  │
│    ├── thumb.png            (Plain thumbnail)                              │
│    ├── yt_thumb.png         (Thumbnail with text overlay)                  │
│    └── metadata.json        (YouTube metadata)                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼ (optional)
┌─────────────────────────────────────────────────────────────────────────────┐
│                          YouTube Client                                     │
│                        (youtube/client.py)                                  │
│                                                                             │
│              OAuth 2.0 → Chunked Upload → Set Thumbnail                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Entry Points

| File | Purpose |
|------|---------|
| `__main__.py` | Module entry point, delegates to CLI |
| `cli.py` | Rich CLI framework (Click + Rich) with commands: `generate`, `mix`, `thumbnail`, `publish`, `list` |

### Core Components

| Component | File | Responsibility |
|-----------|------|----------------|
| **Orchestrator** | `pipeline/orchestrator.py` | 6-phase workflow coordination, directory management, progress callbacks |
| **Suno Client** | `suno/client.py` | Async music generation with parallel track generation (10 concurrent) |
| **Title Generator** | `titles/generator.py` | AI-powered track naming via Gemini with fallback word generation |
| **Thumbnail Generator** | `thumbnail/generator.py` | Dual strategy: pre-generated assets or Gemini image generation |
| **Downloader** | `audio/downloader.py` | Parallel async downloads (5 concurrent) via aiohttp |
| **Mixer** | `audio/mixer.py` | Audio normalization (-14 dBFS) and transitions (cut/crossfade) |
| **Composer** | `video/composer.py` | FFmpeg video encoding + PIL text overlay with auto-resize |
| **Metadata** | `metadata/youtube.py` | SEO-optimized titles, descriptions, tags, and hashtags |
| **YouTube Client** | `youtube/client.py` | OAuth 2.0 authentication, chunked upload, thumbnail setting |

## External Services

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│   Suno API     │  │ Google Gemini  │  │  YouTube API   │  │    FFmpeg      │
│                │  │                │  │                │  │                │
│ • Music gen    │  │ • Title gen    │  │ • OAuth 2.0    │  │ • H.264 encode │
│ • V5 model     │  │ • Image gen    │  │ • Video upload │  │ • Audio mux    │
│ • Polling      │  │ • 2.0-flash    │  │ • Thumbnails   │  │ • Fade effects │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

### API Details

| Service | Endpoint | Authentication | Purpose |
|---------|----------|----------------|---------|
| Suno API | `api.sunoapi.org/api/v1` | Bearer token | Music generation (V5 model) |
| Google Gemini | Google AI SDK | API key | Title generation, image generation |
| YouTube Data API v3 | Google APIs | OAuth 2.0 | Video upload, thumbnail setting |

## Data Flow

```
User Input (mood, genre, track_count)
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 1: Title Generation               │
│   Gemini AI → 10 unique track titles    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 2: Parallel Generation            │
│   ├─ Suno API → 10 tracks (concurrent)  │
│   └─ Thumbnail → image asset/generation │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 3: Download                       │
│   Audio URLs → 10 MP3 files (parallel)  │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 4: Mix                            │
│   MP3s → Normalize → Transition → Mix   │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 5: Compose                        │
│   Image + Audio → MP4 + YT Thumbnail    │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│ Phase 6: Metadata                       │
│   Generate title, description, tags     │
└─────────────────────────────────────────┘
    │
    ▼
MixOutput (video, audio, thumbnails, metadata)
```

## Configuration

Configuration is managed via Pydantic Settings with environment variable support.

```
Config (root)
├── SunoConfig
│   ├── api_key (env: SUNO_API_KEY)
│   ├── base_url, model (V5)
│   ├── poll_interval_seconds (30)
│   ├── timeout_seconds (600)
│   └── max_concurrent (10)
│
├── MixerConfig
│   ├── transition_type ("cut" | "crossfade")
│   ├── crossfade_duration_ms (3000)
│   ├── target_loudness_dbfs (-14.0)
│   └── output_format (mp3), bitrate (320k)
│
├── ThumbnailConfig
│   ├── api_key (env: GEMINI_API_KEY)
│   ├── model (gemini-3-pro-image-preview)
│   └── assets_directory (./assets/thumbnails)
│
├── VideoConfig
│   ├── resolution (1920x1080), fps (30)
│   ├── codec (libx264), preset (medium), crf (18)
│   └── audio_codec (aac), audio_bitrate (320k)
│
├── OverlayConfig
│   ├── font (Montserrat-Black), font_size (140)
│   ├── letter_spacing (25)
│   ├── shadow (enabled), glow (enabled)
│   └── glow_radius (15), glow_opacity (180)
│
└── PipelineConfig
    ├── output_directory (./output)
    ├── temp_directory (./temp)
    └── cleanup_temp (true)
```

## Directory Structure

```
src/suno_mixer/
├── __init__.py              # Package exports
├── __main__.py              # Module entry point
├── cli.py                   # CLI commands
├── config.py                # Pydantic configuration
├── models.py                # Data models
├── presets.py               # Genre presets and prompts
│
├── pipeline/
│   └── orchestrator.py      # 6-phase pipeline
│
├── suno/
│   └── client.py            # Suno API client
│
├── audio/
│   ├── downloader.py        # Async downloads
│   └── mixer.py             # Audio mixing
│
├── titles/
│   └── generator.py         # AI title generation
│
├── thumbnail/
│   └── generator.py         # Thumbnail generation
│
├── video/
│   └── composer.py          # Video composition
│
├── youtube/
│   └── client.py            # YouTube upload
│
└── metadata/
    └── youtube.py           # Metadata generation
```

## Genre Presets

| Genre | BPM | Style |
|-------|-----|-------|
| `dark_synthwave` | 92 | 80s synthwave, dreamy retrowave, nostalgic outrun |
| `deep_house` | 110 | Chill deep house, smooth electronic, laid-back grooves |
| `ambient_electronic` | 70 | Ambient electronic, peaceful soundscape, atmospheric |
| `lofi_beats` | 85 | Lo-fi hip hop, chill beats, jazzy lo-fi, study music |
| `minimal_techno` | 100 | Minimal electronic, downtempo, hypnotic grooves |
| `neo_classical` | 75 | Neo classical, modern classical, cinematic piano |

## Error Handling

| Error Class | Source | Description |
|-------------|--------|-------------|
| `PipelineError` | orchestrator.py | Workflow failures |
| `SunoAPIError` | suno/client.py | API communication issues |
| `DownloadError` | audio/downloader.py | Network failures |
| `MixerError` | audio/mixer.py | Audio processing failures |
| `ComposerError` | video/composer.py | Video composition failures |
| `ThumbnailError` | thumbnail/generator.py | Image generation failures |
| `YouTubeError` | youtube/client.py | Publishing failures |

### Resilience Patterns

1. **Graceful Degradation**: Title generator falls back to word-based generation if Gemini unavailable
2. **Fallback Strategy**: Thumbnail uses pre-generated assets as primary, Gemini as secondary
3. **Error Aggregation**: Parallel operations collect all errors before failing
4. **Timeout Protection**: Suno polling has configurable timeout (default 600s)
5. **Rate Limiting**: Semaphore-based concurrency control

## Key Design Decisions

1. **Async-First**: All I/O operations use async/await for maximum parallelism
2. **Lazy Initialization**: Gemini and YouTube clients only initialize when needed
3. **Dual-Strategy Fallbacks**: Thumbnail and title generation have graceful degradation paths
4. **Modular Components**: Each responsibility is isolated in its own module
5. **Pydantic Validation**: Type-safe configuration from environment variables
6. **Progress Callbacks**: CLI receives real-time updates for long operations
7. **Clean Cuts Default**: Audio transitions use clean cuts instead of crossfades for better quality
8. **Auto-Resize Text**: Thumbnail text automatically scales to fit within margins

## Dependencies

### Python Libraries

| Library | Purpose |
|---------|---------|
| `aiohttp` | Async HTTP requests |
| `aiofiles` | Async file I/O |
| `pydub` | Audio manipulation |
| `Pillow` | Image processing |
| `google-genai` | Gemini API client |
| `google-auth-oauthlib` | OAuth for YouTube |
| `google-api-python-client` | YouTube API |
| `click` | CLI framework |
| `rich` | Terminal UI |
| `pydantic` | Data validation |
| `pydantic-settings` | Configuration management |

### External Tools

| Tool | Purpose |
|------|---------|
| FFmpeg | Video encoding and audio processing |
