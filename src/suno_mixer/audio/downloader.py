"""Parallel audio file downloader."""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import aiofiles
import aiohttp

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Download error."""

    pass


async def download_file(
    session: aiohttp.ClientSession,
    url: str,
    output_path: Path,
    chunk_size: int = 8192,
) -> Path:
    """Download a single file.

    Args:
        session: aiohttp session
        url: URL to download
        output_path: Local path to save file
        chunk_size: Download chunk size

    Returns:
        Path to downloaded file

    Raises:
        DownloadError: If download fails
    """
    try:
        async with session.get(url) as response:
            if response.status != 200:
                raise DownloadError(
                    f"Failed to download {url}: HTTP {response.status}"
                )

            output_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(output_path, "wb") as f:
                async for chunk in response.content.iter_chunked(chunk_size):
                    await f.write(chunk)

            logger.debug(f"Downloaded: {output_path.name}")
            return output_path

    except aiohttp.ClientError as e:
        raise DownloadError(f"Network error downloading {url}: {e}")


async def download_tracks(
    urls: list[str],
    output_dir: Path,
    filenames: Optional[list[str]] = None,
    max_concurrent: int = 5,
) -> list[Path]:
    """Download multiple tracks in parallel.

    Args:
        urls: List of URLs to download
        output_dir: Directory to save files
        filenames: Optional list of filenames (must match urls length)
        max_concurrent: Maximum concurrent downloads

    Returns:
        List of paths to downloaded files (same order as urls)

    Raises:
        DownloadError: If any download fails
    """
    if filenames and len(filenames) != len(urls):
        raise ValueError("filenames must have same length as urls")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filenames if not provided
    if not filenames:
        filenames = [f"track_{i + 1:02d}.mp3" for i in range(len(urls))]

    logger.info(f"Downloading {len(urls)} tracks to {output_dir}")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_download(session, url, path):
        async with semaphore:
            return await download_file(session, url, path)

    async with aiohttp.ClientSession() as session:
        tasks = [
            limited_download(session, url, output_dir / filename)
            for url, filename in zip(urls, filenames)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check for errors
    paths = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            raise DownloadError(f"Failed to download track {i + 1}: {result}")
        paths.append(result)

    total_size = sum(p.stat().st_size for p in paths) / (1024 * 1024)
    logger.info(f"Downloaded {len(paths)} tracks ({total_size:.1f} MB)")

    return paths
