"""YouTube API client for uploading videos."""

import logging
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# OAuth scopes required for uploading videos and setting thumbnails
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

# Default paths
DEFAULT_TOKEN_PATH = Path.home() / ".suno-mixer" / "youtube_token.json"


class YouTubeError(Exception):
    """YouTube API error."""

    pass


class YouTubeClient:
    """YouTube API client for uploading videos."""

    def __init__(
        self,
        client_secrets_path: Path,
        token_path: Path = DEFAULT_TOKEN_PATH,
    ):
        """Initialize YouTube client.

        Args:
            client_secrets_path: Path to OAuth client secrets JSON file
            token_path: Path to store/load OAuth token
        """
        self.client_secrets_path = Path(client_secrets_path)
        self.token_path = Path(token_path)

        if not self.client_secrets_path.exists():
            raise YouTubeError(
                f"Client secrets file not found: {self.client_secrets_path}\n"
                "Download OAuth credentials from Google Cloud Console."
            )

        self.credentials = self._get_credentials()
        self.youtube = build("youtube", "v3", credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth credentials."""
        credentials = None

        # Load existing token if available
        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path), SCOPES
            )

        # Refresh or get new credentials
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                logger.info("Refreshing expired credentials")
                credentials.refresh(Request())
            else:
                logger.info("Running OAuth flow (browser will open)")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_path), SCOPES
                )
                credentials = flow.run_local_server(port=0)

            # Save credentials for next time
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as token_file:
                token_file.write(credentials.to_json())
            logger.info(f"Credentials saved to {self.token_path}")

        return credentials

    def upload(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "10",  # Music
        privacy: str = "public",
        thumbnail_path: Optional[Path] = None,
    ) -> str:
        """Upload a video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (10 = Music)
            privacy: Privacy status (private, unlisted, public)
            thumbnail_path: Optional path to thumbnail image

        Returns:
            YouTube video ID

        Raises:
            YouTubeError: If upload fails
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise YouTubeError(f"Video file not found: {video_path}")

        logger.info(f"Uploading video: {video_path.name}")
        logger.info(f"Title: {title}")
        logger.info(f"Privacy: {privacy}")

        # Video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Upload video
        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024,  # 1MB chunks
        )

        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            video_id = response["id"]
            logger.info(f"Upload complete! Video ID: {video_id}")
            logger.info(f"URL: https://youtube.com/watch?v={video_id}")

            # Set thumbnail if provided
            if thumbnail_path:
                self.set_thumbnail(video_id, thumbnail_path)

            return video_id

        except Exception as e:
            raise YouTubeError(f"Upload failed: {e}")

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> None:
        """Set custom thumbnail for a video.

        Note: Requires a verified YouTube account.

        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image (JPEG, PNG, etc.)

        Raises:
            YouTubeError: If setting thumbnail fails
        """
        thumbnail_path = Path(thumbnail_path)

        if not thumbnail_path.exists():
            raise YouTubeError(f"Thumbnail file not found: {thumbnail_path}")

        logger.info(f"Setting thumbnail for video {video_id}")

        try:
            media = MediaFileUpload(str(thumbnail_path), mimetype="image/png")
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media,
            ).execute()
            logger.info("Thumbnail set successfully")

        except Exception as e:
            # Thumbnail setting often fails for unverified accounts
            logger.warning(f"Failed to set thumbnail: {e}")
            logger.warning("Custom thumbnails require a verified YouTube account")
