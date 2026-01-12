"""Configuration management using Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SunoConfig(BaseSettings):
    """Suno API configuration."""

    api_key: str = Field(..., alias="SUNO_API_KEY")
    base_url: str = "https://api.sunoapi.org/api/v1"
    callback_url: str = "https://api.example.com/callback"
    model: str = "V5"
    custom_mode: bool = True
    instrumental: bool = True
    poll_interval_seconds: int = 30
    timeout_seconds: int = 600
    max_concurrent: int = 10


class MixerConfig(BaseSettings):
    """Audio mixer configuration."""

    transition_type: str = "cut"  # "cut" for clean cuts, "crossfade" for crossfades
    crossfade_duration_ms: int = 3000  # Only used if transition_type is "crossfade"
    target_loudness_dbfs: float = -14.0
    output_format: str = "mp3"
    output_bitrate: str = "320k"


class ThumbnailConfig(BaseSettings):
    """Thumbnail generation configuration."""

    api_key: str = Field(default="", alias="GEMINI_API_KEY")
    model: str = "gemini-3-pro-image-preview"
    assets_directory: Path = Path("./assets/thumbnails")


class VideoConfig(BaseSettings):
    """Video composition configuration."""

    resolution: str = "1920x1080"
    fps: int = 30
    codec: str = "libx264"
    preset: str = "medium"
    crf: int = 18
    audio_codec: str = "aac"
    audio_bitrate: str = "320k"


class OverlayConfig(BaseSettings):
    """Text overlay configuration."""

    font: str = "Montserrat-Black"
    font_size: int = 140
    font_color: str = "white"
    position: str = "center"
    letter_spacing: int = 25  # Pixels between characters for that premium look
    shadow: bool = True
    shadow_color: str = "black"
    shadow_offset: int = 4
    glow: bool = True
    glow_color: str = "black"
    glow_radius: int = 15  # Blur radius for glow effect
    glow_opacity: int = 180  # 0-255


class VisualizerConfig(BaseSettings):
    """Audio visualizer configuration."""

    enabled: bool = True
    style: str = "p2p"  # "lissajous", "wave", "line", "spectrum", "bars", or "p2p"
    height: int = 60  # Height of visualizer in pixels (also width for lissajous)
    width: int = 200  # Width of visualizer in pixels (ignored for lissajous)
    position: str = "bottom"  # "bottom", "top", or "center"
    horizontal_position: str = "right"  # "left", "center", or "right"
    color: str = "white"
    opacity: float = 0.9  # 0.0 to 1.0
    margin_bottom: int = 40  # Pixels from bottom edge
    margin_side: int = 50  # Pixels from left/right edge


class PipelineConfig(BaseSettings):
    """Pipeline configuration."""

    output_directory: Path = Path("./output")
    temp_directory: Path = Path("./temp")
    cleanup_temp: bool = True


class Config(BaseSettings):
    """Main configuration container."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    suno: SunoConfig = Field(default_factory=SunoConfig)
    mixer: MixerConfig = Field(default_factory=MixerConfig)
    thumbnail: ThumbnailConfig = Field(default_factory=ThumbnailConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    overlay: OverlayConfig = Field(default_factory=OverlayConfig)
    visualizer: VisualizerConfig = Field(default_factory=VisualizerConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)


def load_config() -> Config:
    """Load configuration from environment and defaults."""
    return Config()
