"""YouTube metadata generation module."""

from suno_mixer.metadata.youtube import (
    YouTubeTitleGenerator,
    format_duration,
    generate_hashtags,
    generate_tags,
    generate_youtube_description,
    generate_youtube_title,
)

__all__ = [
    "format_duration",
    "generate_hashtags",
    "generate_tags",
    "generate_youtube_description",
    "generate_youtube_title",
    "YouTubeTitleGenerator",
]
