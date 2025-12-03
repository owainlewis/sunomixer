"""Thumbnail generation using Google Gemini or pre-generated assets."""

import logging
import random
import shutil
from pathlib import Path

from suno_mixer.config import ThumbnailConfig
from suno_mixer.presets import THUMBNAIL_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ThumbnailError(Exception):
    """Thumbnail generation error."""
    pass


class ThumbnailGenerator:
    """Generate thumbnails using pre-generated assets or Google Gemini."""

    def __init__(self, config: ThumbnailConfig):
        self.config = config
        self._client = None

    @property
    def client(self):
        """Lazy-load Gemini client only when needed."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.config.api_key)
        return self._client

    def _get_asset_images(self) -> list[Path]:
        """Get list of pre-generated thumbnail images."""
        assets_dir = Path(self.config.assets_directory)
        if not assets_dir.exists():
            return []
        extensions = ('.png', '.jpg', '.jpeg', '.webp')
        return [f for f in assets_dir.iterdir() if f.suffix.lower() in extensions]

    def _select_random_asset(self, output_path: Path) -> Path:
        """Select a random pre-generated thumbnail and copy to output."""
        assets = self._get_asset_images()
        if not assets:
            raise ThumbnailError("No pre-generated thumbnails found in assets directory")

        selected = random.choice(assets)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(selected, output_path)
        logger.info(f"Selected pre-generated thumbnail: {selected.name} -> {output_path}")
        return output_path

    def _generate_prompt(self) -> str:
        """Use LLM to generate a unique image prompt."""
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=THUMBNAIL_SYSTEM_PROMPT,
        )
        prompt = response.text.strip()
        logger.info(f"Generated prompt: {prompt[:100]}...")
        return prompt

    async def generate(self, output_path: Path) -> Path:
        """Generate a thumbnail from pre-generated assets or dynamically.

        If pre-generated thumbnails exist in assets_directory, randomly
        selects one. Otherwise falls back to Gemini generation.

        Args:
            output_path: Path to save image

        Returns:
            Path to generated image

        Raises:
            ThumbnailError: If generation fails
        """
        # Check for pre-generated assets first
        assets = self._get_asset_images()
        if assets:
            logger.info(f"Found {len(assets)} pre-generated thumbnails, selecting random")
            return self._select_random_asset(output_path)

        # Fall back to Gemini generation
        logger.info("No pre-generated thumbnails found, generating via Gemini")
        try:
            from google.genai import types

            # Step 1: Generate unique prompt
            image_prompt = self._generate_prompt()

            # Step 2: Generate image from prompt
            logger.info("Generating image...")
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=image_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    logger.info(f"Thumbnail saved: {output_path}")
                    return output_path

            raise ThumbnailError("No image data in response")

        except Exception as e:
            if isinstance(e, ThumbnailError):
                raise
            raise ThumbnailError(f"Gemini generation failed: {e}")
