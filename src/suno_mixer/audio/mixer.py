"""Audio mixing with crossfades and normalization."""

import logging
from pathlib import Path
from typing import Optional

from pydub import AudioSegment

from suno_mixer.config import MixerConfig

logger = logging.getLogger(__name__)


class MixerError(Exception):
    """Audio mixer error."""

    pass


class AudioMixer:
    """Mix multiple audio tracks with crossfades."""

    def __init__(self, config: MixerConfig):
        """Initialize mixer.

        Args:
            config: Mixer configuration
        """
        self.config = config
        self.transition_type = config.transition_type
        self.crossfade_ms = config.crossfade_duration_ms
        self.target_dbfs = config.target_loudness_dbfs

    def load_track(self, path: Path) -> AudioSegment:
        """Load an audio track.

        Args:
            path: Path to audio file

        Returns:
            AudioSegment

        Raises:
            MixerError: If file cannot be loaded
        """
        try:
            logger.debug(f"Loading: {path.name}")
            return AudioSegment.from_file(str(path))
        except Exception as e:
            raise MixerError(f"Failed to load {path}: {e}")

    def normalize(self, audio: AudioSegment) -> AudioSegment:
        """Normalize audio to target loudness.

        Args:
            audio: Audio to normalize

        Returns:
            Normalized audio
        """
        change_in_dbfs = self.target_dbfs - audio.dBFS
        return audio.apply_gain(change_in_dbfs)

    def create_mix(
        self,
        track_paths: list[Path],
        output_path: Path,
        normalize: bool = True,
    ) -> Path:
        """Mix multiple tracks with crossfades.

        Args:
            track_paths: List of paths to audio files
            output_path: Path for output file
            normalize: Whether to normalize each track

        Returns:
            Path to mixed audio file

        Raises:
            MixerError: If mixing fails
        """
        if not track_paths:
            raise MixerError("No tracks provided")

        if self.transition_type == "crossfade":
            logger.info(f"Mixing {len(track_paths)} tracks with {self.crossfade_ms}ms crossfade")
        else:
            logger.info(f"Mixing {len(track_paths)} tracks with clean cuts")

        # Load first track
        mixed = self.load_track(track_paths[0])
        if normalize:
            mixed = self.normalize(mixed)

        # Append remaining tracks
        for i, path in enumerate(track_paths[1:], start=2):
            track = self.load_track(path)
            if normalize:
                track = self.normalize(track)

            # Apply transition based on type
            if self.transition_type == "crossfade":
                mixed = mixed.append(track, crossfade=self.crossfade_ms)
            else:
                # Clean cut - simple concatenation
                mixed = mixed + track
            logger.debug(f"Added track {i}/{len(track_paths)}")

        # Get duration
        duration_seconds = len(mixed) / 1000
        duration_str = self._format_duration(duration_seconds)

        logger.info(f"Mix complete: {duration_str}")

        # Export
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_format = self.config.output_format
        export_params = {}

        if export_format == "mp3":
            export_params["bitrate"] = self.config.output_bitrate

        logger.info(f"Exporting to {output_path}")
        mixed.export(str(output_path), format=export_format, **export_params)

        return output_path

    def get_duration(self, path: Path) -> float:
        """Get duration of an audio file in seconds.

        Args:
            path: Path to audio file

        Returns:
            Duration in seconds
        """
        audio = self.load_track(path)
        return len(audio) / 1000

    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration as HH:MM:SS.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
