# Suno Mixer

AI-powered YouTube mix automation using Suno API. Generate complete, YouTube-ready deep work/focus music videos with a single command.

## Features

- **Parallel track generation** via Suno API (~5 min for 10 tracks)
- **AI thumbnails** using OpenAI DALL-E 3
- **Automatic mixing** with crossfades and volume normalization
- **Video composition** with stylized text overlay
- **Multiple genre presets** (synthwave, deep house, lo-fi, ambient, etc.)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/suno-mixer.git
cd suno-mixer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Requirements

- Python 3.11+
- FFmpeg (for video composition)
- Suno API key (from [sunoapi.org](https://sunoapi.org))
- OpenAI API key (for thumbnails)

## Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SUNO_API_KEY=your_suno_api_key_here
OPENAI_API_KEY=sk-your_openai_api_key_here
```

## Usage

### Generate a Complete Mix

```bash
# Default: dark synthwave, 10 tracks
suno-mixer generate --mood "FOCUS"

# Specify genre and track count
suno-mixer generate --mood "AMBITION" --genre deep_house --tracks 12

# All options
suno-mixer generate \
    --mood "HYPERFOCUS" \
    --genre dark_synthwave \
    --tracks 10 \
    --output ./output
```

### Available Genres

| Genre | BPM | Style |
|-------|-----|-------|
| `dark_synthwave` | 95 | Night drive, neon, retro |
| `deep_house` | 122 | Warm, hypnotic, flowing |
| `ambient_electronic` | 78 | Calm, meditative, ethereal |
| `lofi_beats` | 85 | Nostalgic, jazzy, relaxed |
| `minimal_techno` | 126 | Hypnotic, driving, industrial |
| `neo_classical` | 70 | Cinematic, emotional, piano |

### List Options

```bash
# List available genres
suno-mixer list genres

# List available mood words
suno-mixer list moods
```

### Generate Only Thumbnail

```bash
suno-mixer thumbnail --mood "FOCUS" --style night_drive --output thumb.png
```

### Mix Local Tracks

```bash
suno-mixer mix --input ./tracks --output mix.mp3 --crossfade 10
```

## Output

Each generation creates:

```
output/
└── focus_dark_synthwave/
    ├── focus_dark_synthwave.mp4      # Final video
    ├── focus_dark_synthwave.mp3      # Audio mix
    ├── focus_dark_synthwave_thumb.png # Thumbnail
    └── focus_dark_synthwave.json     # Metadata
```

## Example Output

```bash
$ suno-mixer generate --mood "HYPERFOCUS" --genre dark_synthwave --tracks 10

Suno Mixer v0.1.0

  Mood:   HYPERFOCUS
  Genre:  Dark Synthwave (95 BPM)
  Tracks: 10

⠋ Generating tracks and thumbnail in parallel... 4:38

Complete!

Video      ./output/hyperfocus_dark_synthwave/hyperfocus_dark_synthwave.mp4
Thumbnail  ./output/hyperfocus_dark_synthwave/hyperfocus_dark_synthwave_thumb.png
Audio      ./output/hyperfocus_dark_synthwave/hyperfocus_dark_synthwave.mp3
Metadata   ./output/hyperfocus_dark_synthwave/hyperfocus_dark_synthwave.json
Duration   1:28:42
Tracks     10
```

## Timing

| Phase | Duration |
|-------|----------|
| Track Generation (parallel) | ~5 min |
| Thumbnail Generation | ~15 sec |
| Audio Download | ~30 sec |
| Audio Mixing | ~60 sec |
| Video Encoding | ~3 min |
| **Total** | **~8-10 min** |

## License

MIT
