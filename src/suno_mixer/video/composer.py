"""Video composition with FFmpeg."""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from suno_mixer.config import OverlayConfig, VideoConfig, VisualizerConfig

logger = logging.getLogger(__name__)


class ComposerError(Exception):
    """Video composer error."""

    pass


class VideoComposer:
    """Compose video from thumbnail, audio, and text overlay."""

    def __init__(
        self,
        video_config: VideoConfig,
        overlay_config: OverlayConfig,
        visualizer_config: Optional[VisualizerConfig] = None,
    ):
        """Initialize video composer.

        Args:
            video_config: Video encoding configuration
            overlay_config: Text overlay configuration
            visualizer_config: Audio visualizer configuration (optional)
        """
        self.video_config = video_config
        self.overlay_config = overlay_config
        self.visualizer_config = visualizer_config or VisualizerConfig()

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

    def _build_visualizer_filter(self, video_width: int, video_height: int) -> str:
        """Build FFmpeg filter string for audio visualization.

        Args:
            video_width: Width of the video in pixels
            video_height: Height of the video in pixels

        Returns:
            FFmpeg filter_complex string for the visualizer
        """
        viz = self.visualizer_config
        viz_height = viz.height
        fps = self.video_config.fps

        # Calculate Y position based on config
        if viz.position == "bottom":
            y_pos = video_height - viz_height - viz.margin_bottom
        elif viz.position == "top":
            y_pos = viz.margin_bottom
        else:  # center
            y_pos = (video_height - viz_height) // 2

        # Build the visualizer filter based on style
        if viz.style == "lissajous":
            # avectorscope in lissajous mode - circular, hypnotic, zen
            viz_filter = (
                f"avectorscope=s={viz_height}x{viz_height}:"
                f"mode=lissajous:rate={fps}:draw=line:"
                f"scale=sqrt:rc=40:gc=40:bc=40"
            )
        elif viz.style == "wave":
            # showwaves with centered line mode - clean and professional
            viz_filter = (
                f"showwaves=s={video_width}x{viz_height}:"
                f"mode=cline:rate={fps}:colors={viz.color}"
            )
        elif viz.style == "line":
            # showwaves with simple line mode - minimal and subtle
            viz_filter = (
                f"showwaves=s={video_width}x{viz_height}:"
                f"mode=line:rate={fps}:colors={viz.color}"
            )
        elif viz.style == "spectrum":
            # showfreqs for frequency spectrum visualization
            viz_filter = (
                f"showfreqs=s={video_width}x{viz_height}:"
                f"mode=bar:fscale=log:colors={viz.color}"
            )
        elif viz.style == "bars":
            # showcqt for constant-Q transform (spectrum bars)
            viz_filter = (
                f"showcqt=s={video_width}x{viz_height}:"
                f"count=5:bar_g=2:sono_g=4"
            )
        else:
            # Default to lissajous
            viz_filter = (
                f"avectorscope=s={viz_height}x{viz_height}:"
                f"mode=lissajous:rate={fps}:draw=line:"
                f"scale=sqrt:rc=40:gc=40:bc=40"
            )

        # Build the complete filter_complex string
        # [0:a] = audio input, [1:v] = image input
        # Scale image, generate visualizer, overlay visualizer on image
        opacity_hex = format(int(viz.opacity * 255), "02x")

        # Calculate X position (centered for lissajous, full width for others)
        if viz.style == "lissajous":
            x_pos = (video_width - viz_height) // 2  # Center the square
        else:
            x_pos = 0

        filter_complex = (
            f"[1:v]scale={video_width}:{video_height},fade=t=in:st=0:d=2[bg];"
            f"[0:a]{viz_filter},format=rgba,"
            f"colorchannelmixer=aa={viz.opacity}[wave];"
            f"[bg][wave]overlay={x_pos}:{y_pos}:format=auto[out]"
        )

        return filter_complex

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

        # Parse video resolution
        width, height = map(int, self.video_config.resolution.split("x"))

        # Build FFmpeg command - use ORIGINAL image (no text) for video
        # Input order matters for filter_complex: audio first, then image
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output
            "-i", str(audio_path),  # Input 0: audio
            "-loop", "1",  # Loop image
            "-i", str(thumbnail_path),  # Input 1: original image (NO text)
        ]

        # Add visualizer or simple fade-in based on config
        if self.visualizer_config.enabled:
            # Use filter_complex for audio visualization
            filter_complex = self._build_visualizer_filter(width, height)
            logger.info(f"Adding audio visualizer (style={self.visualizer_config.style})")
            cmd.extend(["-filter_complex", filter_complex, "-map", "[out]", "-map", "0:a"])
        else:
            # Simple fade-in without visualizer
            cmd.extend(["-vf", f"scale={width}:{height},fade=t=in:st=0:d=2"])

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
