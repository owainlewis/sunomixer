"""Data models for Suno Mixer."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Suno task status values."""

    PENDING = "PENDING"
    TEXT_SUCCESS = "TEXT_SUCCESS"
    FIRST_SUCCESS = "FIRST_SUCCESS"
    SUCCESS = "SUCCESS"
    CREATE_TASK_FAILED = "CREATE_TASK_FAILED"
    GENERATE_AUDIO_FAILED = "GENERATE_AUDIO_FAILED"
    CALLBACK_EXCEPTION = "CALLBACK_EXCEPTION"
    SENSITIVE_WORD_ERROR = "SENSITIVE_WORD_ERROR"


class TrackRequest(BaseModel):
    """Request to generate a single track."""

    prompt: str
    style: str
    title: str
    negative_tags: Optional[str] = None


class SunoTrackData(BaseModel):
    """Track data from Suno API response."""

    id: str
    audio_url: str = Field(alias="audioUrl")
    stream_audio_url: Optional[str] = Field(default=None, alias="streamAudioUrl")
    image_url: Optional[str] = Field(default=None, alias="imageUrl")
    title: str
    tags: Optional[str] = None
    duration: float

    class Config:
        populate_by_name = True


class GenerateResponse(BaseModel):
    """Response from Suno generate endpoint."""

    code: int
    msg: str
    data: Optional[dict] = None

    @property
    def task_id(self) -> Optional[str]:
        """Extract task ID from response."""
        if self.data:
            return self.data.get("taskId")
        return None

    @property
    def is_success(self) -> bool:
        """Check if request was successful."""
        return self.code == 200


class TaskStatusResponse(BaseModel):
    """Response from Suno task status endpoint."""

    code: int
    msg: str
    data: Optional[dict] = None

    @property
    def status(self) -> Optional[TaskStatus]:
        """Extract status from response."""
        if self.data:
            status_str = self.data.get("status")
            if status_str:
                try:
                    return TaskStatus(status_str)
                except ValueError:
                    return None
        return None

    @property
    def is_complete(self) -> bool:
        """Check if task is complete."""
        return self.status == TaskStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        if self.status:
            return self.status in [
                TaskStatus.CREATE_TASK_FAILED,
                TaskStatus.GENERATE_AUDIO_FAILED,
                TaskStatus.CALLBACK_EXCEPTION,
                TaskStatus.SENSITIVE_WORD_ERROR,
            ]
        return False

    @property
    def is_pending(self) -> bool:
        """Check if task is still pending."""
        return self.status in [
            TaskStatus.PENDING,
            TaskStatus.TEXT_SUCCESS,
            TaskStatus.FIRST_SUCCESS,
        ]

    @property
    def tracks(self) -> list[SunoTrackData]:
        """Extract track data from response."""
        if self.data and "response" in self.data:
            response = self.data["response"]
            if "sunoData" in response:
                return [SunoTrackData(**track) for track in response["sunoData"]]
        return []

    @property
    def error_message(self) -> Optional[str]:
        """Extract error message if present."""
        if self.data:
            return self.data.get("errorMessage")
        return None


class TrackResult(BaseModel):
    """Result of a track generation."""

    task_id: str
    title: str
    audio_url: str
    duration: float
    image_url: Optional[str] = None


class MixOutput(BaseModel):
    """Output of a complete mix generation."""

    video_path: Path
    thumbnail_path: Path
    audio_path: Path
    metadata_path: Path
    mood: str
    genre: str
    track_count: int
    total_duration: float
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MixMetadata(BaseModel):
    """Metadata for a generated mix."""

    title: str
    description: str
    tags: list[str]
    hashtags: str
    mood: str
    genre: str
    genre_name: str
    bpm: int
    track_count: int
    total_duration_seconds: float
    tracks: list[dict]
    generated_at: str
    # YouTube fields (populated after publishing)
    youtube_id: Optional[str] = None
    youtube_url: Optional[str] = None
    published_at: Optional[str] = None
