# Suno Mixer - YouTube Mix Automation System

## Product Requirements Document (PRD)

### Overview

Suno Mixer is a Python automation system that generates complete YouTube-ready music mixes on demand. The system creates long-form deep work/focus music videos by:

1. **Generating N tracks in parallel** using the Suno API
2. **Mixing tracks** into seamless long-form audio with crossfades
3. **Generating AI thumbnails** using OpenAI DALL-E or Google Gemini
4. **Composing final video** with thumbnail + audio + stylized text overlay

The output style is inspired by channels like "sout" - featuring minimalist, moody thumbnails with single-word motivational overlays (e.g., "AMBITION", "FLOW", "FOCUS", "GRIND", "OUTLIER", "HYPERFOCUS").

---

## Goals

1. **Parallel track generation** - Generate N tracks simultaneously via Suno API (critical for speed)
2. **Seamless mixing** - Join tracks with professional crossfade transitions
3. **AI-powered thumbnails** - Generate cinematic, mood-appropriate thumbnails
4. **Professional video output** - Combine audio + thumbnail with stylized text overlay
5. **On-demand generation** - Simple CLI to generate complete mixes
6. **Local-first** - Save all outputs locally (no cloud dependencies)

---

## Key Technical Considerations

### Parallel Track Generation (Critical)

Track generation via Suno API takes **2-5 minutes per track**. For a 10-track mix, sequential generation would take 20-50 minutes. **Parallel generation reduces this to ~5 minutes**.

```
Sequential (BAD):  Track1 -> Track2 -> Track3 -> ... -> Track10 = 30+ minutes

Parallel (GOOD):   Track1 \
                   Track2  |
                   Track3  +--> All complete in ~5 minutes
                   ...     |
                   Track10/
```

### Suno API Integration

**Base URL**: `https://api.sunoapi.org`

**Endpoints**:
- **Generate**: `POST /api/v1/generate`
- **Status Check**: `GET /api/v1/generate/record-info?taskId={id}`

**Available Models**:
| Model | Max Duration | Notes |
|-------|-------------|-------|
| `V5` | 8 min | Superior musical expression, fastest |
| `V4_5PLUS` | 8 min | Richer sound, new creative options |
| `V4_5ALL` | 8 min | Better song structure |
| `V4_5` | 8 min | Superior genre blending |
| `V4` | 4 min | Best audio quality, refined structure |

**Task Status Values**:
- `PENDING` - Queued for processing
- `TEXT_SUCCESS` - Lyrics/text generated
- `FIRST_SUCCESS` - First variant ready
- `SUCCESS` - Complete
- `CREATE_TASK_FAILED` / `GENERATE_AUDIO_FAILED` - Failed
- `SENSITIVE_WORD_ERROR` - Content policy violation

**Output**: MP3 URL from `response.sunoData[0].audioUrl`

**Important**: Generated files are stored for **15 days** before deletion

---

## System Architecture

```
+------------------------------------------------------------------------------+
|                           SUNO MIXER PIPELINE                                |
+------------------------------------------------------------------------------+
|                                                                              |
|  PHASE 1: PARALLEL GENERATION (~5 min)                                       |
|  +----------------------------------+  +---------------------------+         |
|  |   Track Generator (Suno API)    |  |  Thumbnail Generator      |         |
|  |   +-------+ +-------+ +-------+ |  |  (OpenAI DALL-E/Gemini)   |         |
|  |   |Track 1| |Track 2| |Track N| |  |                           |         |
|  |   +---+---+ +---+---+ +---+---+ |  +-------------+-------------+         |
|  |       |         |         |     |                |                        |
|  |       +----+----+----+----+     |                |                        |
|  |            |                    |                |                        |
|  |            v                    |                |                        |
|  |   [Parallel async polling]      |                |                        |
|  +------------+--------------------+                |                        |
|               |                                     |                        |
|  PHASE 2:     v                                     |                        |
|  +----------------------------------+               |                        |
|  |       Audio Mixer Engine         |               |                        |
|  |   - Download MP3s from Suno      |               |                        |
|  |   - Crossfade transitions        |               |                        |
|  |   - Volume normalization         |               |                        |
|  |   - Output: mixed_audio.mp3      |               |                        |
|  +------------+---------------------+               |                        |
|               |                                     |                        |
|  PHASE 3:     v                                     v                        |
|  +---------------------------------------------------------------+          |
|  |                   Video Composer (FFmpeg)                     |          |
|  |   - Static thumbnail as video background                      |          |
|  |   - Text overlay: "AMBITION" / "FLOW" / "FOCUS" etc.          |          |
|  |   - Audio track attached                                      |          |
|  |   - Output: final_video.mp4 (YouTube-ready)                   |          |
|  +-----------------------------+---------------------------------+          |
|                                |                                             |
|                                v                                             |
|                    +-----------------------+                                 |
|                    |     Local Output      |                                 |
|                    |     ./output/         |                                 |
|                    |     +-- video.mp4     |                                 |
|                    |     +-- thumbnail.png |                                 |
|                    |     +-- audio.mp3     |                                 |
|                    |     +-- metadata.json |                                 |
|                    +-----------------------+                                 |
|                                                                              |
+------------------------------------------------------------------------------+
```

---

## Core Components

### 1. Track Generator (Suno API Client)

**Purpose**: Generate tracks via Suno API with parallel execution

**API Details** (from official documentation):

#### Generate Request
```http
POST https://api.sunoapi.org/api/v1/generate
Authorization: Bearer {SUNO_API_KEY}
Content-Type: application/json

{
  "model": "V4_5ALL",           # V4, V4_5, V4_5PLUS, V4_5ALL, V5
  "customMode": true,            # true = use style/title, false = auto-generate
  "instrumental": true,          # true = no vocals
  "prompt": "Dark synthwave...", # Required. Max 3000 (V4) or 5000 (V4.5+) chars
  "style": "Synthwave, chillwave", # Required if customMode=true. Max 200 (V4) or 1000 (V4.5+)
  "title": "Track Title",        # Required if customMode=true. Max 80-100 chars
  "negativeTags": "Heavy Metal", # Optional: styles to exclude
  "callBackUrl": "https://..."   # Optional: webhook for completion
}

Response: { "code": 200, "data": { "taskId": "5c79****be8e" } }
```

#### Poll Status
```http
GET https://api.sunoapi.org/api/v1/generate/record-info?taskId={taskId}
Authorization: Bearer {SUNO_API_KEY}

Response: {
  "code": 200,
  "data": {
    "taskId": "5c79****be8e",
    "status": "SUCCESS",  # PENDING | TEXT_SUCCESS | FIRST_SUCCESS | SUCCESS | *_FAILED
    "response": {
      "sunoData": [{
        "id": "8551****662c",
        "audioUrl": "https://example.cn/****.mp3",
        "streamAudioUrl": "https://example.cn/****",
        "imageUrl": "https://example.cn/****.jpeg",
        "title": "Track Title",
        "tags": "synthwave, electronic",
        "duration": 198.44,
        "createTime": "2025-01-01 00:00:00"
      }]
    },
    "errorCode": null,
    "errorMessage": null
  }
}
```

**Implementation**:
```python
class SunoClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sunoapi.org/api/v1"

    async def generate_track(self, prompt: str, title: str, style: str) -> str:
        """Submit generation request, returns task_id"""
        pass

    async def poll_status(self, task_id: str, timeout: int = 300) -> TrackResult:
        """Poll until SUCCESS, returns MP3 URL"""
        pass

    async def generate_tracks_parallel(
        self,
        prompts: List[TrackPrompt],
        max_concurrent: int = 10
    ) -> List[TrackResult]:
        """Generate multiple tracks in parallel using asyncio.gather"""
        pass
```

**Configuration**:
```yaml
suno:
  api_key: "${SUNO_API_KEY}"
  base_url: "https://api.sunoapi.org/api/v1"
  model: "V4_5ALL"              # V4, V4_5, V4_5PLUS, V4_5ALL, V5
  custom_mode: true
  instrumental: true
  default_style: "Dark synthwave, chillwave, electronic"
  negative_tags: "vocals, singing, heavy metal"
  poll_interval_seconds: 30
  timeout_seconds: 600          # 10 min max wait per track
  max_concurrent: 10            # Parallel track generation limit
  retry_attempts: 3
```

**Error Handling**:
| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 400 | Invalid params | Check request body |
| 401 | Unauthorized | Check API key |
| 429 | Insufficient credits | Check balance |
| 430 | Rate limited | Backoff and retry |
| 455 | Maintenance | Wait and retry |
| 500 | Server error | Retry with backoff |

---

### 2. Genre Presets

**Purpose**: Hardcoded, high-quality prompts that ensure consistent genre and BPM across all tracks in a mix.

**Why hardcoded presets:**
- **Consistency** - All tracks flow together with matching genre/BPM
- **Simplicity** - No LLM dependency for prompts
- **Speed** - No API latency for prompt generation
- **Cost** - No per-prompt API costs
- **Reliability** - One less external service

**Genre Presets**:
```python
GENRE_PRESETS = {
    "dark_synthwave": {
        "name": "Dark Synthwave",
        "style": "Dark synthwave, chillwave, retrowave, electronic",
        "prompt": """Dark synthwave with atmospheric pads and driving arpeggios.
Inspired by Timecop 1983 and The Midnight. Night drive aesthetic with
neon-lit highways. Featuring deep bass, lush synth layers, crisp drums,
and reverb-drenched melodies. Moody and cinematic. 95 BPM.""",
        "bpm": 95,
        "negative_tags": "vocals, singing, acoustic, jazz, happy",
        "thumbnail_style": "night_drive"
    },

    "deep_house": {
        "name": "Deep House",
        "style": "Deep house, progressive house, melodic house",
        "prompt": """Deep house with warm rolling basslines and hypnotic grooves.
Smooth chord progressions, subtle percussion, atmospheric textures.
Minimalist and elegant production. Perfect for focus and flow. 122 BPM.""",
        "bpm": 122,
        "negative_tags": "vocals, drops, aggressive, dubstep, buildup",
        "thumbnail_style": "modern_workspace"
    },

    "ambient_electronic": {
        "name": "Ambient Electronic",
        "style": "Ambient electronic, downtempo, atmospheric",
        "prompt": """Ambient electronic soundscape with evolving textures and
gentle rhythms. Ethereal pads, soft arpeggios, subtle organic beats.
Calming and meditative atmosphere. Warm analog synthesizers. 78 BPM.""",
        "bpm": 78,
        "negative_tags": "vocals, loud, aggressive, rock, fast",
        "thumbnail_style": "ocean_view"
    },

    "lofi_beats": {
        "name": "Lo-Fi Beats",
        "style": "Lo-fi hip hop, chillhop, jazzy beats, instrumental hip hop",
        "prompt": """Lo-fi hip hop beats with warm vinyl crackle and mellow vibes.
Jazzy piano chords, dusty drums, smooth basslines, tape saturation.
Nostalgic and relaxing study music atmosphere. 85 BPM.""",
        "bpm": 85,
        "negative_tags": "vocals, singing, aggressive, electronic, loud",
        "thumbnail_style": "modern_workspace"
    },

    "minimal_techno": {
        "name": "Minimal Techno",
        "style": "Minimal techno, tech house, deep techno",
        "prompt": """Minimal techno with hypnotic repetitive patterns and
subtle evolution. Deep kick drums, crisp hi-hats, filtered synth stabs.
Driving but understated energy. Industrial undertones. 126 BPM.""",
        "bpm": 126,
        "negative_tags": "vocals, melodic, happy, acoustic, breakdown",
        "thumbnail_style": "penthouse"
    },

    "neo_classical": {
        "name": "Neo Classical",
        "style": "Neo classical, modern classical, cinematic piano",
        "prompt": """Neo classical composition with emotional piano melodies and
subtle string arrangements. Cinematic and introspective atmosphere.
Minimal electronic textures supporting organic instruments. 70 BPM.""",
        "bpm": 70,
        "negative_tags": "drums, beats, electronic, synth, fast",
        "thumbnail_style": "ocean_view"
    }
}
```

**Track Title Generation**:
```python
# Simple title generator - evocative 1-3 word combinations
TITLE_WORDS = {
    "dark_synthwave": [
        ["Neon", "Chrome", "Voltage", "Digital", "Midnight", "Shadow"],
        ["Abyss", "Horizon", "Dreams", "Descent", "Protocol", "Signal"]
    ],
    "deep_house": [
        ["Deep", "Warm", "Liquid", "Velvet", "Infinite", "Golden"],
        ["Currents", "Motion", "Waves", "Pulse", "Flow", "Drift"]
    ],
    # ... etc
}

def generate_title(genre: str, index: int) -> str:
    """Generate unique track title from word combinations"""
    words = TITLE_WORDS.get(genre, TITLE_WORDS["dark_synthwave"])
    return f"{random.choice(words[0])} {random.choice(words[1])}"
```

**Configuration**:
```yaml
presets:
  default_genre: "dark_synthwave"
  available_genres:
    - dark_synthwave
    - deep_house
    - ambient_electronic
    - lofi_beats
    - minimal_techno
    - neo_classical
```

---

### 3. Audio Mixer Engine

**Purpose**: Combine downloaded tracks into a seamless mix

**Features**:
- Download MP3s from Suno URLs
- Crossfade transitions (10-15 seconds)
- Volume normalization
- Output as high-quality MP3

**Implementation**:
```python
class AudioMixer:
    def __init__(self, crossfade_ms: int = 10000):
        self.crossfade_ms = crossfade_ms

    async def download_tracks(self, urls: List[str], output_dir: str) -> List[str]:
        """Download MP3s from Suno URLs in parallel"""
        pass

    def create_mix(self, track_paths: List[str], output_path: str) -> str:
        """Mix tracks with crossfades, returns output path"""
        # Use pydub for audio processing
        pass

    def normalize_volume(self, audio: AudioSegment, target_dbfs: float = -14.0):
        """Normalize audio to target loudness"""
        pass
```

**Configuration**:
```yaml
mixer:
  crossfade_duration_ms: 10000
  target_loudness_dbfs: -14.0
  output_format: "mp3"
  output_bitrate: "320k"
```

---

### 4. Thumbnail Generator

**Purpose**: Generate cinematic thumbnails using AI

**Style Guidelines** (matching "sout" channel):
- Modern minimalist workspace interiors
- Large windows with city/ocean views
- Night/dusk atmospheric lighting
- Deep blues, warm ambers, soft whites
- Clean, professional aesthetic

**Implementation**:
```python
class ThumbnailGenerator:
    def __init__(self, provider: str = "openai"):
        self.provider = provider

    async def generate(self, mood: str, style: str = "modern_workspace") -> str:
        """Generate thumbnail, returns local file path"""
        pass

STYLE_PROMPTS = {
    "modern_workspace": """
        Minimalist modern office interior at night,
        large floor-to-ceiling windows overlooking city skyline,
        single desk with computer monitor glowing softly,
        moody ambient lighting with blue and amber tones,
        cinematic composition, photorealistic, 4K, no text
    """,
    "ocean_view": """
        Modern minimalist room with large windows overlooking calm ocean at dusk,
        single desk setup with warm lamp,
        atmospheric blue hour lighting,
        cinematic, photorealistic, 4K, no text
    """,
    "penthouse": """
        Luxury penthouse interior at night,
        panoramic city views through floor-to-ceiling windows,
        minimalist furniture, warm ambient lighting,
        cinematic mood, photorealistic, 4K, no text
    """,
    "night_drive": """
        View from inside a car driving through neon-lit city at night,
        rain on windshield, blurred city lights,
        synthwave aesthetic, cinematic, 4K, no text
    """
}
```

**Configuration**:
```yaml
thumbnail:
  provider: "openai"  # openai | gemini
  model: "dall-e-3"
  size: "1792x1024"
  quality: "hd"
  default_style: "modern_workspace"
```

---

### 5. Video Composer

**Purpose**: Combine thumbnail + audio + text overlay into final video

**Text Overlay Specs** (matching "sout" style):
- Font: Montserrat Black (or similar clean sans-serif)
- Color: White with subtle drop shadow
- Position: Center of frame
- Letter spacing: Wide (tracked out)
- ALL CAPS

**Mood Words**:
```python
MOOD_WORDS = [
    "AMBITION", "FLOW", "FOCUS", "GRIND", "OUTLIER",
    "MASTERMIND", "HYPERFOCUS", "CLARITY", "MOMENTUM",
    "DISCIPLINE", "VISION", "DRIVE", "EXECUTE", "PEAK",
    "LIMITLESS", "ASCEND", "CONQUER", "RISE", "FORGE",
    "PRECISION", "RELENTLESS", "UNSTOPPABLE", "ARCHITECT"
]
```

**Implementation** (FFmpeg):
```python
class VideoComposer:
    def compose(
        self,
        thumbnail_path: str,
        audio_path: str,
        overlay_text: str,
        output_path: str
    ) -> str:
        """Create video with static image, audio, and text overlay"""
        # FFmpeg command structure:
        # 1. Load image as video stream
        # 2. Add text overlay with drawtext filter
        # 3. Add audio stream
        # 4. Encode with YouTube-optimal settings
        pass
```

**FFmpeg Command**:
```bash
ffmpeg -loop 1 -i thumbnail.png -i audio.mp3 \
    -vf "drawtext=text='AMBITION':fontfile=Montserrat-Black.ttf:fontsize=120:\
         fontcolor=white:shadowcolor=black:shadowx=2:shadowy=2:\
         x=(w-text_w)/2:y=(h-text_h)/2" \
    -c:v libx264 -preset slow -crf 18 \
    -c:a aac -b:a 320k \
    -shortest -pix_fmt yuv420p \
    output.mp4
```

**Configuration**:
```yaml
video:
  resolution: "1920x1080"
  fps: 30
  codec: "libx264"
  preset: "slow"
  crf: 18
  audio_codec: "aac"
  audio_bitrate: "320k"

overlay:
  font: "Montserrat-Black"
  font_size: 120
  font_color: "white"
  position: "center"
  shadow: true
  shadow_color: "black"
  shadow_offset: 2
```

---

### 6. Pipeline Orchestrator

**Purpose**: Coordinate the entire workflow with parallel execution

**Simplified Flow** (no LLM dependency for prompts):
```
1. Load genre preset (hardcoded)
2. PARALLEL: Generate N tracks via Suno + Generate thumbnail
3. Download tracks and mix audio
4. Compose final video with text overlay
5. Save outputs locally
```

**Implementation**:
```python
class MixPipeline:
    def __init__(self, config: Config):
        self.suno = SunoClient(config.suno.api_key)
        self.mixer = AudioMixer(config.mixer)
        self.thumbnail = ThumbnailGenerator(config.thumbnail)
        self.composer = VideoComposer(config.video)

    async def generate(
        self,
        mood: str,
        genre: str = "dark_synthwave",
        track_count: int = 10
    ) -> MixOutput:
        """
        Generate complete mix:
        1. Load genre preset
        2. PARALLEL: Generate tracks via Suno + Generate thumbnail
        3. Download and mix audio
        4. Compose final video with overlay
        """
        # Phase 1: Load preset and prepare track requests
        preset = GENRE_PRESETS[genre]
        track_requests = [
            TrackRequest(
                prompt=preset["prompt"],
                style=preset["style"],
                title=generate_title(genre, i),
                negative_tags=preset["negative_tags"]
            )
            for i in range(track_count)
        ]

        # Phase 2: Parallel generation (tracks + thumbnail run simultaneously)
        tracks_task = self.suno.generate_tracks_parallel(track_requests)
        thumbnail_task = self.thumbnail.generate(
            mood=mood,
            style=preset.get("thumbnail_style", "modern_workspace")
        )

        tracks, thumbnail_path = await asyncio.gather(tracks_task, thumbnail_task)

        # Phase 3: Download and mix audio
        audio_files = await self.mixer.download_tracks([t.audio_url for t in tracks])
        mixed_audio = self.mixer.create_mix(audio_files)

        # Phase 4: Compose video with text overlay
        output_name = f"{mood.lower()}_{genre}"
        video_path = self.composer.compose(
            thumbnail_path=thumbnail_path,
            audio_path=mixed_audio,
            overlay_text=mood.upper(),
            output_path=f"./output/{output_name}.mp4"
        )

        # Phase 5: Generate metadata
        metadata = self._generate_metadata(mood, genre, preset, tracks, mixed_audio)

        return MixOutput(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            audio_path=mixed_audio,
            metadata=metadata
        )

    def _generate_metadata(self, mood, genre, preset, tracks, audio_path) -> dict:
        return {
            "title": f"Deep Work Music for {mood} | {preset['name']} Mix for Focus & Productivity",
            "mood": mood,
            "genre": genre,
            "bpm": preset["bpm"],
            "track_count": len(tracks),
            "tracks": [{"title": t.title, "duration": t.duration} for t in tracks],
            "generated_at": datetime.utcnow().isoformat()
        }
```

---

## CLI Interface

```bash
# Generate a complete mix (default: dark_synthwave, 10 tracks)
suno-mixer generate --mood "FOCUS"

# Generate with specific genre
suno-mixer generate --mood "AMBITION" --genre dark_synthwave --tracks 12

# Generate deep house mix
suno-mixer generate --mood "FLOW" --genre deep_house --tracks 10

# Generate lo-fi beats mix
suno-mixer generate --mood "GRIND" --genre lofi_beats

# Specify output directory
suno-mixer generate --mood "FOCUS" --genre ambient_electronic --output "./output/"

# List available genres
suno-mixer list genres

# List available mood words
suno-mixer list moods

# Generate only tracks (no mixing/video) - useful for testing
suno-mixer tracks --genre dark_synthwave --count 3 --output "./tracks/"

# Generate only thumbnail
suno-mixer thumbnail --mood "HYPERFOCUS" --style night_drive

# Mix existing local tracks (no Suno API needed)
suno-mixer mix --input "./tracks/" --output "./mix.mp3" --crossfade 10
```

**Available Genres**:
| Genre | BPM | Vibe |
|-------|-----|------|
| `dark_synthwave` | 95 | Night drive, neon, retro |
| `deep_house` | 122 | Warm, hypnotic, flowing |
| `ambient_electronic` | 78 | Calm, meditative, ethereal |
| `lofi_beats` | 85 | Nostalgic, jazzy, relaxed |
| `minimal_techno` | 126 | Hypnotic, driving, industrial |
| `neo_classical` | 70 | Cinematic, emotional, piano |

---

## Directory Structure

```
suno-mixer/
├── docs/
│   └── PRD.md
├── src/
│   └── suno_mixer/
│       ├── __init__.py
│       ├── __main__.py             # Entry point
│       ├── cli.py                  # Click CLI
│       ├── config.py               # Pydantic settings
│       ├── models.py               # Data models
│       ├── presets.py              # Genre presets + title generator
│       ├── suno/
│       │   ├── __init__.py
│       │   └── client.py           # Suno API client (async)
│       ├── audio/
│       │   ├── __init__.py
│       │   ├── downloader.py       # Parallel MP3 download
│       │   └── mixer.py            # Crossfade + normalize
│       ├── thumbnail/
│       │   ├── __init__.py
│       │   ├── generator.py        # Abstract interface
│       │   └── openai_provider.py  # DALL-E 3 implementation
│       ├── video/
│       │   ├── __init__.py
│       │   └── composer.py         # FFmpeg composition + overlay
│       └── pipeline/
│           ├── __init__.py
│           └── orchestrator.py     # Main workflow
├── config/
│   └── default.yaml
├── assets/
│   └── fonts/
│       └── Montserrat-Black.ttf
├── output/                         # Generated videos (gitignored)
├── temp/                           # Temporary files (gitignored)
├── tests/
│   ├── __init__.py
│   ├── test_suno_client.py
│   ├── test_mixer.py
│   └── test_composer.py
├── .env.example
├── .gitignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Dependencies

```txt
# Core
python>=3.11
asyncio
aiohttp>=3.9.0
aiofiles>=23.0.0

# Audio Processing
pydub>=0.25.1
ffmpeg-python>=0.2.0

# AI/API Clients
openai>=1.0.0
google-generativeai>=0.3.0

# Image Processing
Pillow>=10.0.0

# CLI
click>=8.0.0
rich>=13.0.0

# Configuration
pyyaml>=6.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
```

---

## Environment Variables

```bash
# Required
SUNO_API_KEY=xxx                  # Suno API key (from api.sunoapi.org)
OPENAI_API_KEY=sk-xxx             # For prompts + DALL-E thumbnails

# Optional
GEMINI_API_KEY=xxx                # Alternative thumbnail provider
LOG_LEVEL=INFO
```

---

## Output Specifications

### Video File
- **Format**: MP4 (H.264 + AAC)
- **Resolution**: 1920x1080
- **Frame Rate**: 30 fps
- **Video Quality**: CRF 18 (~8 Mbps)
- **Audio**: AAC 320kbps stereo

### Generated Metadata (JSON)
```json
{
  "title": "Deep Work Music for AMBITION | Limitless Productivity Playlist",
  "mood": "AMBITION",
  "duration_seconds": 5400,
  "track_count": 12,
  "tracks": [
    {
      "title": "Neon Abyss",
      "prompt": "Dark synthwave dreamwave...",
      "duration_seconds": 240,
      "suno_task_id": "xxx"
    }
  ],
  "thumbnail_style": "modern_workspace",
  "generated_at": "2025-12-01T12:00:00Z"
}
```

---

## Timing Estimates

| Phase | Duration | Notes |
|-------|----------|-------|
| Load Genre Preset | instant | Hardcoded, no API call |
| Track Generation (parallel) | ~5 min | All N tracks generate simultaneously |
| Thumbnail Generation | ~15 sec | DALL-E 3 HD (runs in parallel with tracks) |
| Audio Download | ~30 sec | Parallel downloads from Suno |
| Audio Mixing | ~60 sec | Crossfade and normalize |
| Video Encoding | ~3 min | FFmpeg, depends on duration |
| **Total** | **~8-10 min** | For complete 90-min mix with 10 tracks |

---

## Development Phases

### Phase 1: Foundation
- [x] PRD and architecture design
- [ ] Project scaffolding (pyproject.toml, directory structure)
- [ ] Configuration management (pydantic-settings)
- [ ] Data models (Pydantic)
- [ ] Genre presets module

### Phase 2: Suno Integration
- [ ] Suno API client (async with aiohttp)
- [ ] Parallel track generation (asyncio.gather)
- [ ] Polling with exponential backoff
- [ ] Error handling and retries

### Phase 3: Audio Pipeline
- [ ] Parallel MP3 download from Suno URLs
- [ ] Audio mixing with pydub (crossfades)
- [ ] Volume normalization (-14 LUFS)

### Phase 4: Visual Pipeline
- [ ] Thumbnail generation (OpenAI DALL-E 3)
- [ ] FFmpeg video composition
- [ ] Text overlay with Montserrat font

### Phase 5: Integration
- [ ] Pipeline orchestrator (async)
- [ ] CLI with Click + Rich progress
- [ ] Metadata generation (JSON)

### Phase 6: Polish
- [ ] Live progress display (rich)
- [ ] Comprehensive error handling
- [ ] README and usage docs

---

## Example Session

```bash
$ suno-mixer generate --mood "HYPERFOCUS" --genre dark_synthwave --tracks 10

🎵 Suno Mixer v1.0

  Mood:   HYPERFOCUS
  Genre:  Dark Synthwave (95 BPM)
  Tracks: 10

[1/4] Generating tracks + thumbnail (parallel)...
      ├─ Thumbnail: night_drive style       ✓ (12s)
      ├─ Track 1:  Neon Protocol            ⠋ polling...
      ├─ Track 2:  Chrome Abyss             ⠋ polling...
      ├─ Track 3:  Voltage Dreams           ⠋ polling...
      ├─ Track 4:  Digital Horizon          ⠋ polling...
      ├─ Track 5:  Midnight Signal          ✓ complete
      ├─ Track 6:  Shadow Descent           ⠋ polling...
      ├─ Track 7:  Circuit Echo             ✓ complete
      ├─ Track 8:  Pulse Matrix             ⠋ polling...
      ├─ Track 9:  Binary Drift             ✓ complete
      └─ Track 10: Synth Horizon            ⠋ polling...
      ✓ All tracks complete (4m 38s)

[2/4] Downloading audio files...
      ✓ Downloaded 10 tracks (847 MB)

[3/4] Mixing audio...
      ✓ Applied 10s crossfades
      ✓ Normalized to -14 LUFS
      ✓ Total duration: 1:28:42

[4/4] Composing video...
      ✓ Added "HYPERFOCUS" text overlay
      ✓ Encoded to H.264/AAC
      ✓ Video ready: ./output/hyperfocus_dark_synthwave.mp4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Complete!

   Video:     ./output/hyperfocus_dark_synthwave.mp4 (1.6 GB)
   Thumbnail: ./output/hyperfocus_dark_synthwave_thumb.png
   Audio:     ./output/hyperfocus_dark_synthwave.mp3
   Metadata:  ./output/hyperfocus_dark_synthwave.json

   Total time: 8m 23s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

*Last Updated: December 2025*
