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
    "synthwave": {
        "name": "Synthwave",
        "style": "80s synthwave, dreamy retrowave, nostalgic outrun, emotional synthwave",
        "prompt": """Dreamy 80s synthwave with nostalgic emotional vibes.
Lush analog synthesizers, warm pads, shimmering arpeggios, gentle pulsing bass.
Nostalgic sunset drives and neon-lit nights. Emotional and cinematic.
Influenced by The Midnight, FM-84, Timecop1983, and Gunship's softer moments.
Gated reverb drums, chorus-drenched leads, ethereal synth melodies.
Warm tape saturation, subtle sidechain pump, VHS aesthetic.
Bittersweet and hopeful. Perfect background for focused creative work. 92 BPM.""",
        "bpm": 92,
        "negative_tags": "vocals, singing, saxophone, sax, harsh, industrial, aggressive, heavy, distorted, busy, chaotic",
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
    "glitch_chill": {
        "name": "Dark Glitch",
        "style": "Dark Boards of Canada, melancholic analog electronic, somber IDM, haunting ambient electronica",
        "prompt": """Dark melancholic electronica with cold analog textures and deep emotional weight.
Sorrowful floating synthesizers with tape degradation and fading memories.
Lonely melodic fragments drifting through minor key pads and hollow washes.
Subtle glitch textures, broken and hypnotic, slowly decaying like old photographs.
Tape wobble, dusty vinyl crackle, lo-fi sadness and loss.
Somber chord progressions, mournful arpeggios, introspective and heavy-hearted. Dark, sad, deeply melancholic. 72 BPM.""",
        "bpm": 72,
        "negative_tags": "vocals, singing, harsh, industrial, aggressive, heavy, distorted, intense, pounding, loud, upbeat, happy, bright",
    },
    "dark_electronic": {
        "name": "Dark Electronic Focus",
        "style": "Dark atmospheric electronic, moody downtempo, cinematic chill, late-night coding music",
        "prompt": """Dark atmospheric electronic music perfect for late-night coding sessions.
Moody downtempo beats with deep sub-bass and crisp minimal percussion.
Spacious reverb-drenched synths, dark ambient pads, subtle melodic motifs.
Cinematic tension without resolution, like a noir film soundtrack.
Influenced by Tycho, Kiasmos, Moderat, and Carbon Based Lifeforms.
Clean production with warm analog character and digital precision.
Hypnotic and immersive, creating a focused tunnel of concentration.
Dark but not oppressive, atmospheric but not distracting. 95 BPM.""",
        "bpm": 95,
        "negative_tags": "vocals, singing, drops, buildup, harsh, aggressive, loud, upbeat, happy, bright, EDM, dubstep, trap",
    },
    "zen_electronic": {
        "name": "Zen Electronic",
        "style": "Peaceful ambient electronic, zen downtempo, meditative chill, calm study music",
        "prompt": """Peaceful zen electronic music for calm focused study sessions.
Gentle floating pads, soft evolving textures, warm embracing atmospheres.
Delicate melodic phrases that drift like clouds, unhurried and serene.
Subtle organic percussion, soft clicks and whispers of rhythm.
Influenced by Helios, Hammock, Emancipator, and Bonobo's quieter moments.
Warm analog synthesis with airy digital shimmer and natural field recordings.
Like morning light through window blinds, gentle rain on leaves.
Meditative and grounding, creating a peaceful sanctuary for deep work.
Calm without being sleepy, present without demanding attention. 72 BPM.""",
        "bpm": 72,
        "negative_tags": "vocals, singing, drops, buildup, harsh, aggressive, loud, fast, intense, dark, heavy, bass drops, EDM, dubstep, trap",
    },
    "chillstep": {
        "name": "Chillstep",
        "style": "Chillstep, melodic dubstep, atmospheric bass, emotional electronic, calm study music",
        "prompt": """Calm melodic chillstep perfect for focused study sessions.
Soft sub-bass swells, gentle wobbles, lush ethereal pads washing over everything.
Emotional piano melodies layered with shimmering synths and airy textures.
Slow halftime drums with soft snares and delicate hi-hats, never overpowering.
Influenced by Blackmill, CMA, Killigrew, and Seven Lions' softer work.
Dreamy reverb-soaked atmospheres, warm analog warmth meets digital clarity.
Like stargazing on a quiet night, peaceful and introspective.
Melodic and emotional without being intense, perfect background for deep focus.
Calming bass presence that grounds without distracting. 140 BPM halftime feel.""",
        "bpm": 140,
        "negative_tags": "vocals, singing, heavy drops, aggressive, loud, intense, harsh, brostep, riddim, heavy bass, screaming synths",
    },
    "winter_focus": {
        "name": "Winter Focus",
        "style": "Dark minimal electronic, calm chill electronica, winter ambient, deep focus coding music",
        "prompt": """Calm, steady dark electronica perfect for deep focus and late-night coding.
Slow tempo with gentle low-end pulse providing sustained concentration foundation.
Crisp minimal hi-hats and soft percussion, never intrusive or busy.
Cold, spacious atmospheres with winter night clarity and stillness.
Calm minimal melodies drifting through dark ambient pads.
Clean production with deep sub-bass warmth and icy high-end shimmer.
Influenced by Burial, Boards of Canada, and Tycho's darker moments.
Seamless instrumental flow, hypnotic and meditative without being sleepy.
Like coding alone at 3am with snow falling outside, focused and calm.
Dark but not oppressive, minimal but not empty. 68 BPM.""",
        "bpm": 68,
        "negative_tags": "vocals, singing, drops, buildup, harsh, aggressive, loud, fast, intense, upbeat, happy, bright, EDM, dubstep, trap, busy drums, complex rhythms",
    },
    "true_devotion": {
        "name": "True Devotion",
        "style": "Future garage, chillstep, downtempo house, ambient bass, minimal electronic, deep focus work music",
        "prompt": """Minimal future garage and chillstep built for true devotion to the craft.
Deep sub-bass providing clear momentum and grounded foundation.
Calm intensity with future rhythm patterns, never rushed but always moving forward.
Sparse melodic fragments floating over warm low-end, clean and intentional.
Influenced by Burial, Mount Kimbie, Four Tet, and James Blake's instrumental work.
Soft shuffling percussion with crisp hi-hats and muted kicks.
Spacious mix with room to breathe, every element purposeful.
Like locking in for serious work, one step further than yesterday.
Ambient house warmth meets future garage precision.
Consistent progress without distraction, calm without being sleepy.
Perfect for long coding sessions, deep design work, and focused productivity. 128 BPM.""",
        "bpm": 128,
        "negative_tags": "vocals, singing, drops, buildup, harsh, aggressive, loud, intense, happy, bright, EDM, dubstep, trap, busy, chaotic, overwhelming",
    },
}


# Title word combinations for each genre (3-4 words per title)
TITLE_WORDS: dict[str, list[list[str]]] = {
    "synthwave": [
        [
            "Neon",
            "Golden",
            "Velvet",
            "Distant",
            "Fading",
            "Electric",
            "Violet",
            "Amber",
            "Midnight",
            "Sunset",
        ],
        [
            "Highway",
            "Dreams",
            "Horizon",
            "Memories",
            "Skyline",
            "Coast",
            "Summer",
            "Escape",
            "Paradise",
            "Waves",
        ],
        [
            "Drive",
            "Drift",
            "Echoes",
            "Glow",
            "Reflections",
            "Reverie",
            "Promise",
            "Return",
            "Embrace",
            "Journey",
        ],
    ],
    "deep_house": [
        [
            "Hollow",
            "Submerged",
            "Distant",
            "Veiled",
            "Shadowed",
            "Buried",
            "Midnight",
            "Sunken",
            "Lost",
            "Frozen",
        ],
        [
            "Warehouse",
            "Bunker",
            "Tunnel",
            "Depths",
            "Basement",
            "Underground",
            "Sector",
            "Chamber",
            "Void",
            "Cavern",
        ],
        [
            "Pulse",
            "Echo",
            "Drift",
            "Descent",
            "Current",
            "Signal",
            "Motion",
            "Ritual",
            "Passage",
            "Transmission",
        ],
    ],
    "ambient_electronic": [
        [
            "Distant",
            "Hollow",
            "Fading",
            "Cold",
            "Empty",
            "Lost",
            "Frozen",
            "Buried",
            "Silent",
            "Void",
        ],
        [
            "Horizon",
            "Wasteland",
            "Grid",
            "Expanse",
            "Threshold",
            "Boundary",
            "Abyss",
            "Sector",
            "Zone",
            "Edge",
        ],
        [
            "Signals",
            "Echoes",
            "Remnants",
            "Ghosts",
            "Traces",
            "Fragments",
            "Memories",
            "Transmissions",
            "Static",
            "Drift",
        ],
    ],
    "lofi_beats": [
        [
            "Dark",
            "Broken",
            "Hollow",
            "Static",
            "Glitch",
            "Distant",
            "Faded",
            "Void",
            "Grey",
            "Shadowed",
        ],
        [
            "Circuit",
            "Terminal",
            "Basement",
            "Underground",
            "Concrete",
            "Midnight",
            "Urban",
            "Digital",
            "Neon",
            "Analog",
        ],
        [
            "Signals",
            "Fragments",
            "Noise",
            "Decay",
            "Static",
            "Dreams",
            "Echoes",
            "Transmissions",
            "Loops",
            "Sessions",
        ],
    ],
    "minimal_techno": [
        ["Stark", "Cold", "Raw", "Mono", "Void", "Grid", "Black", "Steel", "Iron", "Null"],
        ["Sector", "Node", "Block", "Cell", "Unit", "Phase", "Vector", "Zone", "Terminal", "Core"],
        [
            "Machine",
            "System",
            "Pattern",
            "Sequence",
            "Matrix",
            "Code",
            "Process",
            "Function",
            "Protocol",
            "Loop",
        ],
    ],
    "neo_classical": [
        [
            "Fallen",
            "Distant",
            "Fading",
            "Silent",
            "Cold",
            "Hollow",
            "Dark",
            "Lost",
            "Buried",
            "Frozen",
        ],
        [
            "Empire",
            "Kingdom",
            "Throne",
            "Skyline",
            "Horizon",
            "Monument",
            "Cathedral",
            "Tower",
            "Citadel",
            "Ruins",
        ],
        [
            "Descent",
            "Requiem",
            "Elegy",
            "Collapse",
            "Awakening",
            "Departure",
            "Ending",
            "Reckoning",
            "Echo",
            "Legacy",
        ],
    ],
    "glitch_chill": [
        [
            "Faded",
            "Hollow",
            "Broken",
            "Cold",
            "Grey",
            "Empty",
            "Lonely",
            "Lost",
            "Distant",
            "Forgotten",
        ],
        [
            "Memory",
            "Shadow",
            "Silence",
            "Winter",
            "Void",
            "Rain",
            "Grief",
            "Absence",
            "Tomb",
            "Dusk",
        ],
        [
            "Decay",
            "Echoes",
            "Loss",
            "Tears",
            "Ache",
            "Sorrow",
            "Fragments",
            "Whispers",
            "Remains",
            "Ghosts",
        ],
    ],
    "dark_electronic": [
        [
            "Midnight",
            "Terminal",
            "Shadow",
            "Carbon",
            "Deep",
            "Static",
            "Noir",
            "Pulse",
            "Dark",
            "Silent",
        ],
        [
            "Code",
            "Signal",
            "Network",
            "System",
            "Grid",
            "Stream",
            "Circuit",
            "Layer",
            "Engine",
            "Core",
        ],
        [
            "Flow",
            "State",
            "Focus",
            "Drift",
            "Loop",
            "Run",
            "Sync",
            "Mode",
            "Cycle",
            "Phase",
        ],
    ],
    "zen_electronic": [
        [
            "Morning",
            "Gentle",
            "Soft",
            "Quiet",
            "Still",
            "Calm",
            "Floating",
            "Drifting",
            "Peaceful",
            "Warm",
        ],
        [
            "Garden",
            "Cloud",
            "Stream",
            "Meadow",
            "Sky",
            "Light",
            "Rain",
            "Mist",
            "Breeze",
            "Dawn",
        ],
        [
            "Rest",
            "Breath",
            "Peace",
            "Flow",
            "Dream",
            "Drift",
            "Calm",
            "Grace",
            "Ease",
            "Glow",
        ],
    ],
    "chillstep": [
        [
            "Ethereal",
            "Distant",
            "Fading",
            "Celestial",
            "Floating",
            "Serene",
            "Luminous",
            "Dreaming",
            "Endless",
            "Soft",
        ],
        [
            "Stars",
            "Skies",
            "Waves",
            "Aurora",
            "Nebula",
            "Horizon",
            "Ocean",
            "Cosmos",
            "Twilight",
            "Haven",
        ],
        [
            "Dreams",
            "Drift",
            "Glow",
            "Pulse",
            "Flow",
            "Light",
            "Peace",
            "Haze",
            "Bliss",
            "Echo",
        ],
    ],
    "winter_focus": [
        [
            "Frozen",
            "Silent",
            "Cold",
            "Midnight",
            "Hollow",
            "Still",
            "Deep",
            "Quiet",
            "Dark",
            "Fading",
        ],
        [
            "Winter",
            "Snow",
            "Frost",
            "Night",
            "Void",
            "Glass",
            "Ice",
            "Haze",
            "Mist",
            "Static",
        ],
        [
            "Focus",
            "Drift",
            "Pulse",
            "State",
            "Flow",
            "Loop",
            "Calm",
            "Breath",
            "Silence",
            "Code",
        ],
    ],
    "true_devotion": [
        [
            "One",
            "Forward",
            "Steady",
            "Further",
            "Clear",
            "True",
            "Deep",
            "Quiet",
            "Devoted",
            "Locked",
        ],
        [
            "Step",
            "Motion",
            "Focus",
            "Progress",
            "Craft",
            "Path",
            "Momentum",
            "Discipline",
            "Session",
            "Current",
        ],
        [
            "Forward",
            "Further",
            "Flow",
            "State",
            "Devotion",
            "Resolve",
            "Drive",
            "Rhythm",
            "Commit",
            "Lock",
        ],
    ],
}


MOOD_WORDS = [
    "HYPERSCALE",
    "MAINFRAME",
    "BINARY",
    "ALONE",
    "DISTANT",
    "RESET",
    "3AM",
    "2AM",
    "RUNTIME",
    "MATRIX",
    "GLITCH",
    "SYNTAX",
    "DRIFT",
    "SIGNAL",
    "BEFORE",
    "AFTER",
    "DEVOTION",
    "FURTHER",
    "LOCKED",
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


# System prompt for generating YouTube video titles
YOUTUBE_TITLE_SYSTEM_PROMPT = """Generate a single YouTube title for a focus music mix.

Genre: {genre_name}
Mood: {mood}
Duration: {duration_hours} hours
Audience: Software engineers, programmers, developers

Requirements:
- Include keywords like "coding", "programming", "focus", or "deep work"
- Be click-worthy but not clickbait
- Vary structure - don't always use colons or pipes
- Be creative with hooks and benefit statements
- Max 70 characters for optimal display
- Make it feel fresh and unique, not templated

Good examples of varied structures:
- "3 Hours Deep Work Synthwave | Code Like a Machine"
- "Enter Flow State: Dark Electronic for Programmers"
- "The Ultimate Coding Playlist | Lo-Fi Focus Music"
- "Late Night Coding Session | Ambient Electronic Mix"
- "Unlock Peak Focus | 2 Hours Programming Music"

Output ONLY the title, nothing else."""


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
    words = TITLE_WORDS.get(genre, TITLE_WORDS["synthwave"])

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
    words = TITLE_WORDS.get(genre, TITLE_WORDS["synthwave"])
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


