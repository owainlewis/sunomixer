# Suno Mixer: Fully Automated YouTube Mix Generation

## The Problem

"Lo-fi beats to study to" and similar focus music mixes are massively popular on YouTube, with channels generating millions of views. Creating these mixes traditionally requires:

- Sourcing or producing hours of music
- Audio engineering (mixing, normalization, transitions)
- Thumbnail design
- Video production
- SEO-optimized titles, descriptions, and tags
- Manual upload and scheduling

This is time-intensive and doesn't scale.

## The Solution

**Suno Mixer** is a fully automated pipeline that generates complete, YouTube-ready focus music videos from a single command. It orchestrates multiple AI services to handle every step of the content creation process.

```
suno-mixer generate --mood FOCUS --genre dark_synthwave --tracks 10
```

One command. One hour of original music. Ready for YouTube.

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT                                    │
│              Mood: "FOCUS"  +  Genre: "dark_synthwave"          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI GENERATION LAYER                          │
│                                                                 │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Gemini    │    │  Suno API   │    │   Gemini    │        │
│   │             │    │             │    │             │        │
│   │ Track Titles│    │ 10 Tracks   │    │  Thumbnail  │        │
│   │ "Neon       │    │ (parallel)  │    │  (or asset) │        │
│   │  Highway    │    │             │    │             │        │
│   │  Dreams"    │    │ ~3 min each │    │  1280x720   │        │
│   └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MEDIA PROCESSING LAYER                        │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                     FFmpeg Pipeline                      │  │
│   │                                                          │  │
│   │  Audio:  Normalize → Transition → Mix → Export MP3      │  │
│   │  Video:  Static Image + Audio → H.264 MP4               │  │
│   │  Image:  Add text overlay with glow/shadow effects      │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    METADATA GENERATION                          │
│                                                                 │
│   Title:       "FOCUS Flow: Deep Work Music for Intense..."    │
│   Description: Track listing with timestamps, CTAs, hashtags   │
│   Tags:        16+ SEO-optimized tags                          │
│   Thumbnail:   Text overlay auto-sized to fit                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUT                                  │
│                                                                 │
│   📁 output/FOCUS_dark_synthwave_20241202/                      │
│      ├── mix.mp4           (1hr video, ready for upload)       │
│      ├── mix.mp3           (audio only)                        │
│      ├── thumbnail.png     (YouTube thumbnail with text)       │
│      └── metadata.json     (title, description, tags)          │
│                                                                 │
│   Optional: Auto-upload to YouTube via OAuth                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## AI Services Used

| Service | Role | Why |
|---------|------|-----|
| **Suno API** | Music generation | Generates original instrumental tracks from text prompts. No licensing issues. |
| **Google Gemini** | Title & thumbnail generation | Creates unique, evocative track names and thumbnail images matching the aesthetic. |
| **YouTube Data API** | Publishing | Automated upload with metadata, thumbnail, and scheduling. |

## Key Technical Decisions

**Async-First Architecture**
- 10 tracks generate in parallel (not sequentially)
- Downloads happen concurrently
- Total generation time: ~10-15 minutes for 1 hour of content

**Graceful Fallbacks**
- Pre-generated thumbnail assets as primary (faster, consistent quality)
- AI generation as fallback
- Word-bank title generation if Gemini unavailable

**Audio Engineering**
- Loudness normalization to -14 dBFS (YouTube/Spotify standard)
- Clean cuts between tracks (crossfades often sound worse with AI music)
- 320kbps MP3 output

**Video Production**
- H.264 encoding for universal compatibility
- 2-second fade-in from black
- Text overlay with auto-resize to prevent edge overflow

## Daily Automation

The system is designed to run as a scheduled job:

```bash
# Cron job: Generate a new mix every day at 2 AM
0 2 * * * cd /path/to/suno-mixer && ./run-daily.sh
```

Each run produces unique content:
- Random mood selection from curated list
- AI-generated titles ensure no duplicates
- Thumbnail variation through asset rotation or AI generation

## Output Example

**Generated Title:**
> FOCUS Flow: Deep Work Music for Intense Programming Sessions | 1 Hour Synthwave Mix

**Generated Description:**
```
Deep work music engineered for flow states and intense focus.

Tracks:
00:00 - Neon Highway Dreams
03:24 - Digital Horizon Pulse
06:48 - Velvet Midnight Echo
...

#deepwork #focusmusic #synthwave #programming #studymusic
```

## Tech Stack

```
Python 3.11+
├── aiohttp / aiofiles    (async I/O)
├── pydub                 (audio processing)
├── Pillow                (image manipulation)
├── google-genai          (Gemini API)
├── google-api-client     (YouTube API)
├── click + rich          (CLI)
└── pydantic              (configuration)

External:
└── FFmpeg                (video/audio encoding)
```

## Why This Matters

1. **Zero marginal cost** - Each video costs only API calls (~$0.50-1.00)
2. **Infinite variety** - AI ensures every mix is unique
3. **No licensing** - Suno-generated music is commercially usable
4. **SEO-optimized** - Metadata generation follows YouTube best practices
5. **Fully hands-off** - Schedule it and forget it

---

*Built as an experiment in end-to-end AI content automation.*
