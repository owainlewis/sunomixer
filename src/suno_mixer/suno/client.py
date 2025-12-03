"""Async Suno API client with parallel track generation."""

import asyncio
import logging
from typing import Optional

import aiohttp

from suno_mixer.config import SunoConfig
from suno_mixer.models import (
    GenerateResponse,
    TaskStatus,
    TaskStatusResponse,
    TrackRequest,
    TrackResult,
)

logger = logging.getLogger(__name__)


class SunoAPIError(Exception):
    """Suno API error."""

    def __init__(self, message: str, code: Optional[int] = None):
        self.code = code
        super().__init__(message)


class SunoClient:
    """Async client for Suno API with parallel track generation."""

    def __init__(self, config: SunoConfig):
        """Initialize Suno client.

        Args:
            config: Suno API configuration
        """
        self.config = config
        self.base_url = config.base_url
        self.api_key = config.api_key
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def headers(self) -> dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def close(self) -> None:
        """Close the client session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "SunoClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def generate_track(self, request: TrackRequest) -> str:
        """Submit a track generation request.

        Args:
            request: Track generation request

        Returns:
            Task ID for polling

        Raises:
            SunoAPIError: If API request fails
        """
        session = await self._get_session()

        payload = {
            "model": self.config.model,
            "customMode": self.config.custom_mode,
            "instrumental": self.config.instrumental,
            "callBackUrl": self.config.callback_url,
            "prompt": request.prompt,
            "style": request.style,
            "title": request.title,
        }

        if request.negative_tags:
            payload["negativeTags"] = request.negative_tags

        logger.debug(f"Generating track: {request.title}")

        async with session.post(f"{self.base_url}/generate", json=payload) as resp:
            data = await resp.json()
            response = GenerateResponse(**data)

            if not response.is_success:
                raise SunoAPIError(
                    f"Failed to generate track: {response.msg}", code=response.code
                )

            task_id = response.task_id
            if not task_id:
                raise SunoAPIError("No task ID in response")

            logger.info(f"Track '{request.title}' submitted: {task_id}")
            return task_id

    async def get_task_status(self, task_id: str) -> TaskStatusResponse:
        """Get the status of a generation task.

        Args:
            task_id: Task ID to check

        Returns:
            Task status response

        Raises:
            SunoAPIError: If API request fails
        """
        session = await self._get_session()

        async with session.get(
            f"{self.base_url}/generate/record-info", params={"taskId": task_id}
        ) as resp:
            data = await resp.json()
            return TaskStatusResponse(**data)

    async def wait_for_track(
        self,
        task_id: str,
        title: str,
        on_status: Optional[callable] = None,
    ) -> TrackResult:
        """Wait for a track generation to complete.

        Args:
            task_id: Task ID to wait for
            title: Track title (for logging)
            on_status: Optional callback for status updates

        Returns:
            Track result with audio URL

        Raises:
            SunoAPIError: If generation fails or times out
        """
        timeout = self.config.timeout_seconds
        interval = self.config.poll_interval_seconds
        elapsed = 0

        while elapsed < timeout:
            status_response = await self.get_task_status(task_id)

            if on_status:
                on_status(task_id, title, status_response.status)

            if status_response.is_complete:
                tracks = status_response.tracks
                if not tracks:
                    raise SunoAPIError(f"No tracks in completed response for {task_id}")

                track = tracks[0]  # Get first track
                logger.info(f"Track '{title}' complete: {track.duration:.1f}s")

                return TrackResult(
                    task_id=task_id,
                    title=track.title,
                    audio_url=track.audio_url,
                    duration=track.duration,
                    image_url=track.image_url,
                )

            if status_response.is_failed:
                error_msg = status_response.error_message or "Unknown error"
                raise SunoAPIError(
                    f"Track generation failed for '{title}': {error_msg}"
                )

            logger.debug(f"Track '{title}' status: {status_response.status}")
            await asyncio.sleep(interval)
            elapsed += interval

        raise SunoAPIError(f"Timeout waiting for track '{title}' after {timeout}s")

    async def generate_track_and_wait(
        self,
        request: TrackRequest,
        on_status: Optional[callable] = None,
    ) -> TrackResult:
        """Generate a track and wait for completion.

        Args:
            request: Track generation request
            on_status: Optional callback for status updates

        Returns:
            Track result with audio URL
        """
        task_id = await self.generate_track(request)
        return await self.wait_for_track(task_id, request.title, on_status)

    async def generate_tracks_parallel(
        self,
        requests: list[TrackRequest],
        on_status: Optional[callable] = None,
    ) -> list[TrackResult]:
        """Generate multiple tracks in parallel.

        Args:
            requests: List of track generation requests
            on_status: Optional callback for status updates

        Returns:
            List of track results (same order as requests)

        Raises:
            SunoAPIError: If any track generation fails
        """
        logger.info(f"Starting parallel generation of {len(requests)} tracks")

        # Create tasks for all track generations
        tasks = [
            self.generate_track_and_wait(request, on_status) for request in requests
        ]

        # Run all tasks concurrently with semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def limited_task(task):
            async with semaphore:
                return await task

        limited_tasks = [limited_task(task) for task in tasks]

        # Wait for all to complete
        results = await asyncio.gather(*limited_tasks, return_exceptions=True)

        # Check for exceptions
        track_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise SunoAPIError(
                    f"Track {i + 1} '{requests[i].title}' failed: {result}"
                )
            track_results.append(result)

        logger.info(f"All {len(track_results)} tracks generated successfully")
        return track_results
