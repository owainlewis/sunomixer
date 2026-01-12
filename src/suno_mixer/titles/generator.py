"""AI-powered track title generation using Google Gemini."""

import logging

from suno_mixer.config import ThumbnailConfig
from suno_mixer.presets import TITLE_SYSTEM_PROMPT
from suno_mixer.presets import generate_titles as generate_titles_fallback

logger = logging.getLogger(__name__)


class TitleGenerationError(Exception):
    """Title generation error."""
    pass


class TitleGenerator:
    """Generate unique track titles using AI or fallback to word combinations."""

    def __init__(self, config: ThumbnailConfig):
        """Initialize title generator.

        Args:
            config: Thumbnail config (reuses Gemini API key)
        """
        self.config = config
        self._client = None

    @property
    def client(self):
        """Lazy-load Gemini client only when needed."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.config.api_key)
        return self._client

    def generate(self, genre_name: str, style: str, count: int) -> list[str]:
        """Generate unique track titles using AI.

        Args:
            genre_name: Human-readable genre name (e.g., "Dark Lo-Fi")
            style: Style tags (e.g., "Dark lo-fi, industrial lo-fi, electronic beats")
            count: Number of titles to generate

        Returns:
            List of unique track titles

        Raises:
            TitleGenerationError: If generation fails and no fallback available
        """
        # Check if API key is configured
        if not self.config.api_key:
            logger.warning("No Gemini API key configured, using fallback title generation")
            return self._fallback_generate(count)

        try:
            prompt = TITLE_SYSTEM_PROMPT.format(
                genre_name=genre_name,
                style=style,
                count=count
            )

            logger.info(f"Generating {count} AI titles for genre: {genre_name}")

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )

            # Parse response - one title per line
            text = response.text.strip()
            titles = [line.strip() for line in text.split('\n') if line.strip()]

            # Ensure we have enough titles
            if len(titles) < count:
                logger.warning(f"AI generated {len(titles)} titles, needed {count}. Padding with fallback.")
                fallback = self._fallback_generate(count - len(titles))
                titles.extend(fallback)

            # Trim to exact count
            titles = titles[:count]

            logger.info(f"Generated titles: {titles}")
            return titles

        except Exception as e:
            logger.error(f"AI title generation failed: {e}, using fallback")
            return self._fallback_generate(count)

    def _fallback_generate(self, count: int) -> list[str]:
        """Fallback to word-based title generation.

        Args:
            count: Number of titles to generate

        Returns:
            List of titles from word combinations
        """
        # Use lofi_beats as default fallback genre
        return generate_titles_fallback("lofi_beats", count)
