"""Analog warmth processing using Spotify's Pedalboard library.

Subtle Boards of Canada-inspired processing: warm, hazy, nostalgic.
"""

import logging
from pathlib import Path

from pedalboard import (
    Pedalboard,
    Compressor,
    Chorus,
    HighShelfFilter,
    LowShelfFilter,
    LowpassFilter,
    Reverb,
    Gain,
)
from pedalboard.io import AudioFile

logger = logging.getLogger(__name__)


class WarmthProcessor:
    """Apply analog warmth effects to audio files.

    Inspired by Boards of Canada's warm, degraded analog aesthetic.
    All effects are kept subtle and musical.
    """

    def __init__(
        self,
        low_shelf_gain_db: float = 2.5,
        low_shelf_freq_hz: float = 180.0,
        high_shelf_gain_db: float = -2.0,
        high_shelf_freq_hz: float = 7000.0,
        lowpass_freq_hz: float = 14000.0,
        chorus_rate_hz: float = 0.2,
        chorus_depth: float = 0.08,
        chorus_mix: float = 0.12,
        reverb_room_size: float = 0.25,
        reverb_damping: float = 0.8,
        reverb_wet: float = 0.08,
        compressor_threshold_db: float = -18.0,
        compressor_ratio: float = 2.0,
        makeup_gain_db: float = 1.0,
    ):
        """Initialize warmth processor with configurable parameters.

        Args:
            low_shelf_gain_db: Low frequency boost in dB
            low_shelf_freq_hz: Low shelf cutoff frequency
            high_shelf_gain_db: High frequency adjustment in dB (negative for roll-off)
            high_shelf_freq_hz: High shelf cutoff frequency
            lowpass_freq_hz: Gentle lowpass to tame digital harshness
            chorus_rate_hz: Chorus modulation rate (slow for subtle movement)
            chorus_depth: Chorus depth (0-1)
            chorus_mix: Chorus wet/dry mix (0-1)
            reverb_room_size: Reverb room size (0-1)
            reverb_damping: Reverb high frequency damping (higher = darker)
            reverb_wet: Reverb wet level (keep low for subtlety)
            compressor_threshold_db: Compressor threshold
            compressor_ratio: Compressor ratio
            makeup_gain_db: Final makeup gain
        """
        self.board = Pedalboard([
            # Warm low-end boost - BoC's rich bass
            LowShelfFilter(
                cutoff_frequency_hz=low_shelf_freq_hz,
                gain_db=low_shelf_gain_db,
                q=0.6,
            ),
            # Roll off harsh highs - tape-like darkness
            HighShelfFilter(
                cutoff_frequency_hz=high_shelf_freq_hz,
                gain_db=high_shelf_gain_db,
                q=0.6,
            ),
            # Gentle lowpass - removes digital edge
            LowpassFilter(cutoff_frequency_hz=lowpass_freq_hz),
            # Very slow, subtle chorus - tape-like drift
            Chorus(
                rate_hz=chorus_rate_hz,
                depth=chorus_depth,
                centre_delay_ms=8.0,
                feedback=0.0,
                mix=chorus_mix,
            ),
            # Touch of dark reverb - hazy dreaminess
            Reverb(
                room_size=reverb_room_size,
                damping=reverb_damping,
                wet_level=reverb_wet,
                dry_level=1.0,
                width=0.8,
            ),
            # Gentle compression for cohesion
            Compressor(
                threshold_db=compressor_threshold_db,
                ratio=compressor_ratio,
                attack_ms=15,
                release_ms=150,
            ),
            # Makeup gain
            Gain(gain_db=makeup_gain_db),
        ])

    def process(self, input_path: Path, output_path: Path | None = None) -> Path:
        """Apply warmth processing to an audio file.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file. If None, overwrites input.

        Returns:
            Path to processed audio file
        """
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)

        logger.info(f"Applying warmth processing to: {input_path.name}")

        with AudioFile(str(input_path)) as f:
            audio = f.read(f.frames)
            samplerate = f.samplerate
            logger.debug(f"Sample rate: {samplerate}Hz, Duration: {f.frames / samplerate:.1f}s")

        processed = self.board(audio, samplerate)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with AudioFile(str(output_path), 'w', samplerate, processed.shape[0]) as f:
            f.write(processed)

        logger.info(f"Warmth processing complete: {output_path.name}")
        return output_path
