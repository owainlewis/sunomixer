"""YouTube metadata generation for Suno Mixer."""

import random

NEWSLETTER_LINK = "https://newsletter.owainlewis.com/subscribe"
SKOOL_LINK = "https://skool.com/aiengineer/about"

# Genre-specific vibe descriptions
GENRE_VIBES = {
    "Dark Synthwave": "Dark, atmospheric synthwave with neon-lit highways and retro-futuristic energy to suppress distractions and fuel your late-night coding sessions.",
    "Deep House": "Warm, rolling basslines and hypnotic grooves that create the perfect flow state for extended programming sprints.",
    "Ambient Electronic": "Ethereal soundscapes and gentle rhythms that calm the mind while maintaining razor-sharp focus on complex problems.",
    "Lo-Fi Beats": "Dusty, nostalgic beats with jazzy undertones that transform your workspace into a cozy productivity sanctuary.",
    "Minimal Techno": "Hypnotic, repetitive patterns that drive deep concentration and eliminate mental noise during intensive technical work.",
    "Neo Classical": "Emotional piano melodies and subtle strings that inspire creativity while maintaining deep focus.",
}

# Power words for title hooks
TITLE_HOOKS = [
    "Ultrahuman Focus",
    "Unstoppable Deep Work",
    "Peak Performance",
    "Limitless Clarity",
    "Elite Focus",
    "Absolute Concentration",
    "Unbreakable Flow",
    "Maximum Output",
    "Zero Distractions",
    "Laser Precision",
    "Infinite Momentum",
    "Pure Focus State",
    "Relentless Clarity",
    "Superhuman Flow",
    "Total Immersion",
    "Locked In",
    "Unwavering Focus",
    "God Mode",
    "Tunnel Vision",
    "Mental Fortress",
    "Prime State",
    "Cognitive Surge",
    "Beast Mode",
    "Deep Code",
    "Silent Mastery",
    "Monk Mode",
    "Grind State",
    "Flow Protocol",
    "Dark Focus",
    "Productivity",
]


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)

    if hours > 0:
        return f"{hours} Hour{'s' if hours > 1 else ''} {minutes} Minutes"
    return f"{minutes} Minutes"


def generate_youtube_title(mood: str, genre_name: str) -> str:
    """Generate YouTube title following SOP format.

    Format: [Strong Benefit/Hook] | [Keywords/Audience] | [Music Vibe]
    """
    hook = random.choice(TITLE_HOOKS)
    return f"{hook}: Deep Work Music for Coding & Programming | {genre_name}"


def generate_youtube_description(
    mood: str,
    genre_name: str,
    duration_formatted: str,
    tracks: list[dict],
) -> str:
    """Generate full YouTube description per SOP structure."""

    vibe_description = GENRE_VIBES.get(
        genre_name,
        "Atmospheric electronic music designed for peak cognitive performance and deep focus.",
    )

    # Build tracklist with timestamps
    tracklist_lines = []
    current_time = 0
    for track in tracks:
        hours = int(current_time // 3600)
        minutes = int((current_time % 3600) // 60)
        seconds = int(current_time % 60)

        if hours > 0:
            timestamp = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            timestamp = f"{minutes}:{seconds:02d}"

        tracklist_lines.append(f"{timestamp} - {track['title']}")
        current_time += track.get("duration", 180)  # Default 3 min if not specified

    tracklist = "\n".join(tracklist_lines)

    hashtags = generate_hashtags(mood, genre_name)
    keywords = generate_keywords(mood, genre_name)

    description = f"""FREE AI engineering tutorials: {NEWSLETTER_LINK}

---

{duration_formatted} of {genre_name}. {vibe_description}

Perfect for deep coding sessions, technical problem-solving, system design, and late-night hacking.

Tracklist:
{tracklist}

Join the best AI engineering community, earn more, build real automated systems: {SKOOL_LINK}

{hashtags}

{keywords}"""

    return description


def generate_tags(mood: str, genre_name: str) -> list[str]:
    """Generate YouTube tags for the video."""
    base_tags = [
        "coding music",
        "programming music",
        "deep work music",
        "focus music",
        "study music",
        "concentration music",
        "work music",
        "productivity music",
        genre_name.lower(),
        f"{genre_name.lower()} mix",
        "music for coding",
        "music for programming",
        "developer music",
        "software engineer music",
        mood.lower(),
        f"{mood.lower()} music",
    ]
    return base_tags


def generate_hashtags(mood: str, genre_name: str) -> str:
    """Generate hashtag string for description."""
    hashtags = [
        "#CodingMusic",
        "#DeepWork",
        "#ProgrammingMusic",
        "#FocusMusic",
        "#StudyMusic",
        "#AIEngineer",
        "#ProductivityMusic",
        f"#{genre_name.replace(' ', '')}",
        f"#{mood.title()}",
        "#TechMusic",
    ]
    return " ".join(hashtags)


def generate_keywords(mood: str, genre_name: str) -> str:
    """Generate comma-separated keywords for SEO."""
    keywords = [
        "coding music",
        "programming music",
        "deep work",
        "focus music for coding",
        "study music",
        "concentration music",
        f"{genre_name.lower()} for coding",
        "music for programmers",
        "developer playlist",
        "software engineer music",
        "work from home music",
        "lo-fi coding",
        "ambient coding music",
        f"{mood.lower()} music",
        "productivity playlist",
        "music for deep focus",
        "coding playlist",
        "hacking music",
        "late night coding",
        "flow state music",
    ]
    return ", ".join(keywords)
