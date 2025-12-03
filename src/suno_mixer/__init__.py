"""Suno Mixer - AI-powered YouTube mix automation."""

__version__ = "0.1.0"

from suno_mixer.pipeline.orchestrator import MixPipeline
from suno_mixer.presets import GENRE_PRESETS, MOOD_WORDS

__all__ = ["MixPipeline", "GENRE_PRESETS", "MOOD_WORDS", "__version__"]
