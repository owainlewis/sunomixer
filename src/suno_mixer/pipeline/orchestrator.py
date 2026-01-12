"""Pipeline orchestrator for complete mix generation."""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from suno_mixer.audio.downloader import download_tracks
from suno_mixer.audio.mixer import AudioMixer
from suno_mixer.audio.warmth import WarmthProcessor
from suno_mixer.config import Config
from suno_mixer.metadata import (
    YouTubeTitleGenerator,
    format_duration,
    generate_hashtags,
    generate_tags,
    generate_youtube_description,
)
from suno_mixer.models import MixMetadata, MixOutput, TrackRequest
from suno_mixer.presets import GENRE_PRESETS
from suno_mixer.suno.client import SunoClient
from suno_mixer.thumbnail import ThumbnailGenerator
from suno_mixer.titles import TitleGenerator
from suno_mixer.video.composer import VideoComposer

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Pipeline error."""

    pass


class MixPipeline:
    """Orchestrate the complete mix generation pipeline."""

    def __init__(self, config: Config):
        """Initialize pipeline.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize components
        self.suno = SunoClient(config.suno)
        self.mixer = AudioMixer(config.mixer)
        self.warmth = WarmthProcessor()
        self.thumbnail_gen = ThumbnailGenerator(config.thumbnail)
        self.title_gen = TitleGenerator(config.thumbnail)  # Reuses Gemini config
        self.yt_title_gen = YouTubeTitleGenerator(config.thumbnail)  # AI YouTube titles
        self.composer = VideoComposer(config.video, config.overlay, config.visualizer)

        # Directories
        self.output_dir = Path(config.pipeline.output_directory)
        self.temp_dir = Path(config.pipeline.temp_directory)

    async def generate(
        self,
        mood: str,
        genre: str = "dark_synthwave",
        track_count: int = 10,
        on_progress: Optional[callable] = None,
    ) -> MixOutput:
        """Generate a complete mix.

        Args:
            mood: Mood word for overlay (e.g., "FOCUS", "AMBITION")
            genre: Genre preset key
            track_count: Number of tracks to generate
            on_progress: Optional progress callback

        Returns:
            MixOutput with paths to generated files

        Raises:
            PipelineError: If generation fails
        """
        # Validate inputs
        if genre not in GENRE_PRESETS:
            available = ", ".join(GENRE_PRESETS.keys())
            raise PipelineError(f"Unknown genre '{genre}'. Available: {available}")

        preset = GENRE_PRESETS[genre]
        mood = mood.upper()

        # Create output directory with timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{mood.lower()}_{genre}_{timestamp}"
        run_dir = self.output_dir / output_name
        run_dir.mkdir(parents=True, exist_ok=True)

        temp_tracks_dir = self.temp_dir / output_name / "tracks"
        temp_tracks_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting pipeline: mood={mood}, genre={genre}, tracks={track_count}")

        if on_progress:
            on_progress("init", f"Generating {track_count} {preset['name']} tracks")

        # Phase 1: Prepare track requests with unique AI-generated titles
        titles = self.title_gen.generate(
            genre_name=preset["name"],
            style=preset["style"],
            count=track_count
        )
        track_requests = [
            TrackRequest(
                prompt=preset["prompt"],
                style=preset["style"],
                title=titles[i],
                negative_tags=preset["negative_tags"],
            )
            for i in range(track_count)
        ]

        # Phase 2: Parallel generation (tracks + thumbnail)
        async with self.suno:
            if on_progress:
                on_progress("generate", "Generating tracks and thumbnail in parallel")

            # Define status callback for tracks
            def track_status(task_id, title, status):
                if on_progress:
                    on_progress("track_status", f"{title}: {status}")

            # Run track generation and thumbnail generation in parallel
            tracks_task = self.suno.generate_tracks_parallel(
                track_requests, on_status=track_status
            )

            thumbnail_path = run_dir / f"{output_name}_thumb.png"
            thumbnail_task = self.thumbnail_gen.generate(thumbnail_path)

            tracks, thumbnail_path = await asyncio.gather(tracks_task, thumbnail_task)

        if on_progress:
            on_progress("download", f"Downloading {len(tracks)} tracks")

        # Phase 3: Download tracks
        track_urls = [t.audio_url for t in tracks]
        track_filenames = [f"{i + 1:02d}_{t.title.replace(' ', '_')}.mp3" for i, t in enumerate(tracks)]

        downloaded_paths = await download_tracks(
            track_urls,
            temp_tracks_dir,
            filenames=track_filenames,
        )

        if on_progress:
            on_progress("mix", "Mixing audio tracks")

        # Phase 4: Mix audio
        audio_path = run_dir / f"{output_name}.mp3"
        self.mixer.create_mix(downloaded_paths, audio_path)

        if on_progress:
            on_progress("warmth", "Applying analog warmth processing")

        # Phase 4.5: Apply warmth processing
        self.warmth.process(audio_path)

        # Get total duration
        total_duration = self.mixer.get_duration(audio_path)

        if on_progress:
            on_progress("compose", "Composing video")

        # Phase 5: Compose video
        video_path = run_dir / f"{output_name}.mp4"
        video_path, yt_thumbnail_path = self.composer.compose(
            thumbnail_path=thumbnail_path,
            audio_path=audio_path,
            overlay_text=mood,
            output_path=video_path,
        )

        # Phase 6: Generate YouTube metadata
        track_list = [{"title": t.title, "duration": t.duration} for t in tracks]
        duration_formatted = format_duration(total_duration)
        duration_hours = max(1, int(total_duration // 3600))

        # Generate AI-powered YouTube title
        youtube_title = self.yt_title_gen.generate(
            genre_name=preset["name"],
            mood=mood,
            duration_hours=duration_hours,
        )

        metadata = MixMetadata(
            title=youtube_title,
            description=generate_youtube_description(
                mood=mood,
                genre_name=preset["name"],
                duration_formatted=duration_formatted,
                tracks=track_list,
            ),
            tags=generate_tags(mood, preset["name"]),
            hashtags=generate_hashtags(mood, preset["name"]),
            mood=mood,
            genre=genre,
            genre_name=preset["name"],
            bpm=preset["bpm"],
            track_count=len(tracks),
            total_duration_seconds=total_duration,
            tracks=track_list,
            generated_at=datetime.utcnow().isoformat(),
        )

        metadata_path = run_dir / f"{output_name}.json"
        metadata_path.write_text(json.dumps(metadata.model_dump(), indent=2))

        # Cleanup temp files if configured
        if self.config.pipeline.cleanup_temp:
            import shutil
            temp_run_dir = self.temp_dir / output_name
            if temp_run_dir.exists():
                shutil.rmtree(temp_run_dir)
                logger.debug(f"Cleaned up temp directory: {temp_run_dir}")

        if on_progress:
            on_progress("complete", "Pipeline complete")

        logger.info(f"Pipeline complete: {video_path}")

        return MixOutput(
            video_path=video_path,
            thumbnail_path=yt_thumbnail_path,  # YouTube thumbnail with text overlay
            audio_path=audio_path,
            metadata_path=metadata_path,
            mood=mood,
            genre=genre,
            track_count=len(tracks),
            total_duration=total_duration,
        )
