"""Genre presets and title generation for Suno Mixer."""

import random
from typing import TypedDict


class GenrePreset(TypedDict):
    """Type definition for genre preset."""

    name: str
    style: str
    prompt: str
    bpm: int
    negative_tags: str


GENRE_PRESETS: dict[str, GenrePreset] = {
    "dark_synthwave": {
        "name": "Dreamy Synthwave",
        "style": "80s synthwave, dreamy retrowave, nostalgic outrun, emotional synthwave",
        "prompt": """Dreamy 80s synthwave with nostalgic emotional vibes.
Lush analog synthesizers, warm pads, shimmering arpeggios, gentle pulsing bass.
Nostalgic sunset drives and neon-lit nights. Emotional and cinematic.
Gated reverb drums, chorus-drenched leads, ethereal synth melodies. Bittersweet and hopeful. 92 BPM.""",
        "bpm": 92,
        "negative_tags": "vocals, singing, saxophone, sax, harsh, industrial, aggressive, heavy, distorted",
    },
    "deep_house": {
        "name": "Chill Deep House",
        "style": "Chill deep house, smooth electronic, laid-back grooves",
        "prompt": """Smooth chill deep house perfect for focused work sessions.
Warm rolling basslines, soft Rhodes chords, gentle shuffling percussion.
Mellow filtered pads, subtle grooves, relaxed atmosphere.
Coffee shop meets late-night lounge. Unobtrusive yet engaging. 110 BPM.""",
        "bpm": 110,
        "negative_tags": "vocals, drops, aggressive, intense, buildup, mainstream edm, harsh",
    },
    "ambient_electronic": {
        "name": "Ambient Focus",
        "style": "Ambient electronic, peaceful soundscape, atmospheric focus music",
        "prompt": """Peaceful ambient electronic soundscape for deep concentration.
Slowly evolving pads, gentle textures, spacious atmospheres.
Soft drones, subtle melodic fragments, calming washes of sound.
Like floating through clouds. Meditative and serene. Perfect for deep work. 70 BPM.""",
        "bpm": 70,
        "negative_tags": "vocals, drums, percussion, harsh, intense, fast, aggressive",
    },
    "lofi_beats": {
        "name": "Lo-Fi Chill",
        "style": "Lo-fi hip hop, chill beats, jazzy lo-fi, study music",
        "prompt": """Warm lo-fi hip hop beats perfect for studying and coding.
Mellow jazzy samples, soft dusty drums, gentle vinyl crackle.
Smooth Rhodes chords, laid-back grooves, cozy late-night vibes.
Like a rainy afternoon with coffee. Nostalgic and comforting. 85 BPM.""",
        "bpm": 85,
        "negative_tags": "vocals, singing, intense, fast, aggressive, harsh, loud",
    },
    "minimal_techno": {
        "name": "Minimal Electronic",
        "style": "Minimal electronic, downtempo, hypnotic grooves, subtle techno",
        "prompt": """Minimal electronic with hypnotic subtle grooves for focused work.
Soft clicks and gentle percussion, warm filtered basslines.
Slowly evolving patterns, understated melodies, spacious mix.
Repetitive but not intrusive. Background texture for concentration. 100 BPM.""",
        "bpm": 100,
        "negative_tags": "vocals, aggressive, pounding, harsh, loud, intense, drops",
    },
    "neo_classical": {
        "name": "Neo Classical",
        "style": "Neo classical, modern classical, cinematic piano, orchestral ambient",
        "prompt": """Gentle neo-classical music blending piano with soft electronic textures.
Delicate piano melodies, subtle string arrangements, ambient pads.
Emotional and introspective modern classical with minimalist sensibility.
Warm and contemplative. Beautiful background for creative work. 75 BPM.""",
        "bpm": 75,
        "negative_tags": "vocals, drums, harsh, loud, fast, aggressive, intense",
    },
}


# Title word combinations for each genre (3-4 words per title)
TITLE_WORDS: dict[str, list[list[str]]] = {
    "dark_synthwave": [
        ["Neon", "Golden", "Velvet", "Distant", "Fading", "Electric", "Violet", "Amber", "Midnight", "Sunset"],
        ["Highway", "Dreams", "Horizon", "Memories", "Skyline", "Coast", "Summer", "Escape", "Paradise", "Waves"],
        ["Drive", "Drift", "Echoes", "Glow", "Reflections", "Reverie", "Promise", "Return", "Embrace", "Journey"],
    ],
    "deep_house": [
        ["Hollow", "Submerged", "Distant", "Veiled", "Shadowed", "Buried", "Midnight", "Sunken", "Lost", "Frozen"],
        ["Warehouse", "Bunker", "Tunnel", "Depths", "Basement", "Underground", "Sector", "Chamber", "Void", "Cavern"],
        ["Pulse", "Echo", "Drift", "Descent", "Current", "Signal", "Motion", "Ritual", "Passage", "Transmission"],
    ],
    "ambient_electronic": [
        ["Distant", "Hollow", "Fading", "Cold", "Empty", "Lost", "Frozen", "Buried", "Silent", "Void"],
        ["Horizon", "Wasteland", "Grid", "Expanse", "Threshold", "Boundary", "Abyss", "Sector", "Zone", "Edge"],
        ["Signals", "Echoes", "Remnants", "Ghosts", "Traces", "Fragments", "Memories", "Transmissions", "Static", "Drift"],
    ],
    "lofi_beats": [
        ["Dark", "Broken", "Hollow", "Static", "Glitch", "Distant", "Faded", "Void", "Grey", "Shadowed"],
        ["Circuit", "Terminal", "Basement", "Underground", "Concrete", "Midnight", "Urban", "Digital", "Neon", "Analog"],
        ["Signals", "Fragments", "Noise", "Decay", "Static", "Dreams", "Echoes", "Transmissions", "Loops", "Sessions"],
    ],
    "minimal_techno": [
        ["Stark", "Cold", "Raw", "Mono", "Void", "Grid", "Black", "Steel", "Iron", "Null"],
        ["Sector", "Node", "Block", "Cell", "Unit", "Phase", "Vector", "Zone", "Terminal", "Core"],
        ["Machine", "System", "Pattern", "Sequence", "Matrix", "Code", "Process", "Function", "Protocol", "Loop"],
    ],
    "neo_classical": [
        ["Fallen", "Distant", "Fading", "Silent", "Cold", "Hollow", "Dark", "Lost", "Buried", "Frozen"],
        ["Empire", "Kingdom", "Throne", "Skyline", "Horizon", "Monument", "Cathedral", "Tower", "Citadel", "Ruins"],
        ["Descent", "Requiem", "Elegy", "Collapse", "Awakening", "Departure", "Ending", "Reckoning", "Echo", "Legacy"],
    ],
}


MOOD_WORDS = [
    "FLOW",
    "FOCUS",
    "CLARITY",
    "PROGRESS",
    "DISCIPLINE",
    "DRIVE",
    "VISION",
    "MOMENTUM",
    "AMBITION",
    "THRIVE",
    "GRIND",
    "RISE",
    "FORGE",
    "PEAK",
    "DEPTH",
    "CALM",
    "EXECUTE",
    "CREATE",
    "BUILD",
    "MASTERY",
]


# System prompt for generating unique track titles
TITLE_SYSTEM_PROMPT = """You are naming tracks for a dark, electronic focus music mix.

Genre: {genre_name}
Style: {style}
Number of titles needed: {count}

Aesthetic inspiration: Tron Legacy, Blade Runner, cyberpunk, dystopian futures,
neon-noir, late-night coding sessions, dark warehouses, digital grids.

Generate {count} unique, evocative track titles. Each title should:
- Be 2-4 words long
- Feel dark, moody, and electronic
- Evoke digital/technological imagery (grids, circuits, signals, voids)
- Be poetic and memorable, not generic
- Avoid happy, warm, or bright imagery
- Sound like they belong on a Tron or Blade Runner soundtrack

Output ONLY the titles, one per line. No numbering, no explanations."""


# System prompt for generating unique thumbnail prompts
THUMBNAIL_SYSTEM_PROMPT = """You are a creative director for a coding/focus music YouTube channel.
Generate a unique, detailed image prompt for a YouTube thumbnail.

Theme: Dark, moody, atmospheric scenes with soft diffuse lighting.

Vary between these scene types:
- Silhouette of person at monitors during blue hour, soft city lights in background
- Minimalist workspace at golden hour, warm light diffusing through windows
- Back view of developer in glass-walled space at dusk, muted city skyline
- Cozy cabin workspace at dawn, soft morning mist outside
- Rooftop setup during early evening, subtle warm and cool tones mixing
- Dark office at night with soft ambient screen glow, city out of focus below

Time of day (vary between):
- Early morning / dawn with soft diffuse light
- Golden hour / early evening with warm muted tones
- Nighttime with subtle ambient lighting

Style requirements:
- MUST be landscape/widescreen (16:9 aspect ratio)
- Dark and moody overall tone
- Soft, diffuse lighting - no harsh light sources
- Cinematic contrast with deep shadows
- Muted, desaturated color palette - NO oversaturated colors
- Cool blues and teals with occasional subtle warm accents
- Film grain, photorealistic, ultra-wide angle
- Can include silhouette/back of person (adds scale and relatability)
- No faces visible, no text, no watermarks

Output ONLY the image prompt. Be specific and vivid. Emphasize soft lighting and muted colors."""


def generate_title(genre: str, index: int) -> str:
    """Generate a track title for a genre (deprecated, use generate_titles for uniqueness).

    Args:
        genre: The genre key from GENRE_PRESETS
        index: Track index (used for seeding randomness)

    Returns:
        A three-word evocative title
    """
    words = TITLE_WORDS.get(genre, TITLE_WORDS["dark_synthwave"])

    random.seed(index * 31 + hash(genre) % 1000)
    first = random.choice(words[0])
    second = random.choice(words[1])
    third = random.choice(words[2])
    random.seed()  # Reset to true randomness

    return f"{first} {second} {third}"


def generate_titles(genre: str, count: int) -> list[str]:
    """Generate unique track titles for a genre.

    Args:
        genre: The genre key from GENRE_PRESETS
        count: Number of unique titles to generate

    Returns:
        List of unique three-word evocative titles
    """
    words = TITLE_WORDS.get(genre, TITLE_WORDS["dark_synthwave"])
    titles: set[str] = set()
    max_attempts = count * 10  # Prevent infinite loop
    attempts = 0

    while len(titles) < count and attempts < max_attempts:
        first = random.choice(words[0])
        second = random.choice(words[1])
        third = random.choice(words[2])
        title = f"{first} {second} {third}"
        titles.add(title)
        attempts += 1

    return list(titles)[:count]


def get_preset(genre: str) -> GenrePreset:
    """Get a genre preset by key.

    Args:
        genre: The genre key

    Returns:
        The genre preset dict

    Raises:
        KeyError: If genre not found
    """
    if genre not in GENRE_PRESETS:
        available = ", ".join(GENRE_PRESETS.keys())
        raise KeyError(f"Unknown genre '{genre}'. Available: {available}")
    return GENRE_PRESETS[genre]


def get_thumbnail_prompt(style: str) -> str:
    """Get a thumbnail prompt by style.

    Args:
        style: The style key

    Returns:
        The DALL-E prompt string

    Raises:
        KeyError: If style not found
    """
    if style not in THUMBNAIL_STYLES:
        available = ", ".join(THUMBNAIL_STYLES.keys())
        raise KeyError(f"Unknown thumbnail style '{style}'. Available: {available}")
    return THUMBNAIL_STYLES[style]
