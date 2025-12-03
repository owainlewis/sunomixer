"""Video composition with FFmpeg."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from suno_mixer.config import OverlayConfig, VideoConfig

logger = logging.getLogger(__name__)


class ComposerError(Exception):
    """Video composer error."""

    pass


class VideoComposer:
    """Compose video from thumbnail, audio, and text overlay."""

    def __init__(self, video_config: VideoConfig, overlay_config: OverlayConfig):
        """Initialize video composer.

        Args:
            video_config: Video encoding configuration
            overlay_config: Text overlay configuration
        """
        self.video_config = video_config
        self.overlay_config = overlay_config

        # Check for ffmpeg
        if not shutil.which("ffmpeg"):
            raise ComposerError("ffmpeg not found. Please install ffmpeg.")

    def _get_text_width_with_spacing(
        self, text: str, font: ImageFont.FreeTypeFont, letter_spacing: int
    ) -> int:
        """Calculate total text width including letter spacing."""
        total_width = 0
        for i, char in enumerate(text):
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            total_width += char_width
            if i < len(text) - 1:
                total_width += letter_spacing
        return total_width

    def _find_optimal_font_size(
        self,
        text: str,
        img_width: int,
        img_height: int,
        font_path: Optional[Path],
        base_font_size: int,
        letter_spacing: int,
        margin_percent: float = 0.08,
    ) -> tuple[ImageFont.FreeTypeFont, int]:
        """Find optimal font size that fits within image margins.

        Args:
            text: Text to render
            img_width: Image width in pixels
            img_height: Image height in pixels
            font_path: Optional path to font file
            base_font_size: Starting font size
            letter_spacing: Letter spacing in pixels
            margin_percent: Margin as percentage of image dimensions (default 8%)

        Returns:
            Tuple of (font, adjusted_letter_spacing)
        """
        max_width = int(img_width * (1 - 2 * margin_percent))
        max_height = int(img_height * (1 - 2 * margin_percent))
        font_size = base_font_size
        min_font_size = 40

        while font_size >= min_font_size:
            # Scale letter spacing proportionally with font size
            scaled_spacing = int(letter_spacing * (font_size / base_font_size))

            # Try to load font at this size
            font = self._load_font(font_path, font_size)

            # Calculate text dimensions
            text_width = self._get_text_width_with_spacing(text, font, scaled_spacing)
            bbox = font.getbbox(text[0]) if text else (0, 0, 0, 0)
            text_height = bbox[3] - bbox[1]

            # Check if text fits
            if text_width <= max_width and text_height <= max_height:
                if font_size < base_font_size:
                    logger.info(f"Reduced font size from {base_font_size} to {font_size} to fit text")
                return font, scaled_spacing

            # Reduce font size and try again
            font_size -= 10

        # Return minimum size if nothing fits
        logger.warning(f"Text may overflow, using minimum font size {min_font_size}")
        font = self._load_font(font_path, min_font_size)
        scaled_spacing = int(letter_spacing * (min_font_size / base_font_size))
        return font, scaled_spacing

    def _load_font(
        self, font_path: Optional[Path], font_size: int
    ) -> ImageFont.FreeTypeFont:
        """Load font at specified size.

        Args:
            font_path: Optional path to font file
            font_size: Font size in pixels

        Returns:
            Loaded font
        """
        try:
            if font_path and font_path.exists():
                return ImageFont.truetype(str(font_path), font_size)
            else:
                for font_name in ["Montserrat-Black", "Arial Black", "Helvetica Bold", "Arial"]:
                    try:
                        return ImageFont.truetype(font_name, font_size)
                    except OSError:
                        continue
                logger.warning("Could not load font, using default")
                return ImageFont.load_default()
        except OSError:
            logger.warning("Could not load font, using default")
            return ImageFont.load_default()

    def _draw_text_with_spacing(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        x: int,
        y: int,
        font: ImageFont.FreeTypeFont,
        fill: str,
        letter_spacing: int,
    ) -> None:
        """Draw text with custom letter spacing."""
        current_x = x
        for char in text:
            draw.text((current_x, y), char, font=font, fill=fill)
            bbox = font.getbbox(char)
            char_width = bbox[2] - bbox[0]
            current_x += char_width + letter_spacing

    def add_text_overlay(
        self,
        image_path: Path,
        text: str,
        output_path: Path,
        font_path: Optional[Path] = None,
    ) -> Path:
        """Add text overlay to an image with letter-spacing and glow effects.

        Args:
            image_path: Path to input image
            text: Text to overlay
            output_path: Path for output image
            font_path: Optional path to font file

        Returns:
            Path to output image
        """
        logger.info(f"Adding text overlay: '{text}'")

        # Open image
        img = Image.open(image_path).convert("RGBA")

        # Find optimal font size that fits within margins
        font, letter_spacing = self._find_optimal_font_size(
            text=text,
            img_width=img.width,
            img_height=img.height,
            font_path=font_path,
            base_font_size=self.overlay_config.font_size,
            letter_spacing=self.overlay_config.letter_spacing,
        )

        # Calculate text dimensions with letter spacing
        text_width = self._get_text_width_with_spacing(text, font, letter_spacing)
        bbox = font.getbbox(text[0]) if text else (0, 0, 0, 0)
        text_height = bbox[3] - bbox[1]

        # Calculate position (center)
        x = (img.width - text_width) // 2
        y = (img.height - text_height) // 2

        # Create glow effect if enabled
        if self.overlay_config.glow:
            # Create a transparent layer for the glow
            glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)

            # Draw text for glow (slightly larger area)
            glow_color = self.overlay_config.glow_color
            self._draw_text_with_spacing(
                glow_draw, text, x, y, font, glow_color, letter_spacing
            )

            # Apply blur for glow effect
            glow_layer = glow_layer.filter(
                ImageFilter.GaussianBlur(radius=self.overlay_config.glow_radius)
            )

            # Adjust glow opacity
            glow_data = glow_layer.split()
            if len(glow_data) == 4:
                alpha = glow_data[3].point(
                    lambda p: min(p * 2, self.overlay_config.glow_opacity)
                )
                glow_layer.putalpha(alpha)

            # Composite glow onto image
            img = Image.alpha_composite(img, glow_layer)

        # Create text layer
        text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)

        # Draw shadow if enabled
        if self.overlay_config.shadow:
            shadow_offset = self.overlay_config.shadow_offset
            shadow_color = self.overlay_config.shadow_color
            self._draw_text_with_spacing(
                text_draw,
                text,
                x + shadow_offset,
                y + shadow_offset,
                font,
                shadow_color,
                letter_spacing,
            )

        # Draw main text
        self._draw_text_with_spacing(
            text_draw, text, x, y, font, self.overlay_config.font_color, letter_spacing
        )

        # Composite text onto image
        img = Image.alpha_composite(img, text_layer)

        # Convert back to RGB for saving
        img = img.convert("RGB")

        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")

        logger.debug(f"Saved overlay image: {output_path}")
        return output_path

    def compose(
        self,
        thumbnail_path: Path,
        audio_path: Path,
        overlay_text: str,
        output_path: Path,
        font_path: Optional[Path] = None,
    ) -> tuple[Path, Path]:
        """Compose final video from thumbnail and audio.

        Creates two outputs:
        1. YouTube thumbnail: image WITH text overlay
        2. Video: image WITHOUT text overlay (clean image + audio)

        Args:
            thumbnail_path: Path to thumbnail image
            audio_path: Path to audio file
            overlay_text: Text to overlay on thumbnail
            output_path: Path for output video
            font_path: Optional path to font file

        Returns:
            Tuple of (video_path, thumbnail_with_text_path)

        Raises:
            ComposerError: If composition fails
        """
        thumbnail_path = Path(thumbnail_path)
        audio_path = Path(audio_path)
        output_path = Path(output_path)

        # Create YouTube thumbnail with text overlay (separate file)
        thumbnail_with_text_path = output_path.parent / f"{output_path.stem}_yt_thumb.png"
        self.add_text_overlay(thumbnail_path, overlay_text, thumbnail_with_text_path, font_path)

        logger.info(f"Composing video: {output_path}")

        # Build FFmpeg command - use ORIGINAL image (no text) for video
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-loop", "1",  # Loop image
            "-i", str(thumbnail_path),  # Input: original image (NO text)
            "-i", str(audio_path),  # Input audio
        ]

        # Add fade-in from black effect
        cmd.extend(["-vf", "fade=t=in:st=0:d=2"])

        cmd.extend([
            "-c:v", self.video_config.codec,
            "-preset", self.video_config.preset,
            "-crf", str(self.video_config.crf),
            "-c:a", self.video_config.audio_codec,
            "-b:a", self.video_config.audio_bitrate,
            "-pix_fmt", "yuv420p",  # Compatibility
            "-shortest",  # End when audio ends
            "-r", str(self.video_config.fps),
            str(output_path),
        ])

        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"Video created: {output_path}")
            logger.info(f"YouTube thumbnail created: {thumbnail_with_text_path}")
            return output_path, thumbnail_with_text_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise ComposerError(f"FFmpeg failed: {e.stderr}")
