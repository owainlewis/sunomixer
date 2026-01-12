"""Command-line interface for Suno Mixer."""

import asyncio
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from suno_mixer.config import load_config
from suno_mixer.pipeline.orchestrator import MixPipeline
from suno_mixer.presets import GENRE_PRESETS, MOOD_WORDS


def format_duration(seconds: float) -> str:
    """Format duration as HH:MM:SS or MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


console = Console()


def setup_logging(verbose: bool = False):
    """Setup logging with Rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def main(ctx, verbose):
    """Suno Mixer - AI-powered YouTube mix automation."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@main.command()
@click.option("--mood", "-m", required=True, help="Mood word for overlay (e.g., FOCUS, AMBITION)")
@click.option(
    "--genre",
    "-g",
    default="dark_synthwave",
    type=click.Choice(list(GENRE_PRESETS.keys())),
    help="Music genre preset",
)
@click.option("--tracks", "-t", default=10, help="Number of tracks to generate")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.pass_context
def generate(ctx, mood, genre, tracks, output):
    """Generate a complete YouTube-ready mix."""
    console.print("\n[bold cyan]Suno Mixer[/bold cyan] v0.1.0\n")

    preset = GENRE_PRESETS[genre]
    console.print(f"  [bold]Mood:[/bold]   {mood.upper()}")
    console.print(f"  [bold]Genre:[/bold]  {preset['name']} ({preset['bpm']} BPM)")
    console.print(f"  [bold]Tracks:[/bold] {tracks}\n")

    try:
        config = load_config()

        if output:
            config.pipeline.output_directory = Path(output)

        pipeline = MixPipeline(config)

        # Run the async pipeline
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Starting...", total=None)

            def on_progress(phase, message):
                progress.update(task, description=f"[cyan]{message}")

            result = asyncio.run(
                pipeline.generate(
                    mood=mood,
                    genre=genre,
                    track_count=tracks,
                    on_progress=on_progress,
                )
            )

        # Print results
        console.print("\n[bold green]Complete![/bold green]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Label", style="bold")
        table.add_column("Value")

        table.add_row("Video", str(result.video_path))
        table.add_row("Thumbnail", str(result.thumbnail_path))
        table.add_row("Audio", str(result.audio_path))
        table.add_row("Metadata", str(result.metadata_path))

        table.add_row("Duration", format_duration(result.total_duration))
        table.add_row("Tracks", str(result.track_count))

        console.print(table)
        console.print()

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


@main.group("list")
def list_cmd():
    """List available options."""
    pass


@list_cmd.command("genres")
def list_genres():
    """List available genre presets."""
    table = Table(title="Available Genres")
    table.add_column("Key", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("BPM", justify="right")

    for key, preset in GENRE_PRESETS.items():
        table.add_row(
            key,
            preset["name"],
            str(preset["bpm"]),
        )

    console.print(table)


@list_cmd.command("moods")
def list_moods():
    """List available mood words."""
    console.print("\n[bold]Available Mood Words:[/bold]\n")

    # Print in columns
    cols = 4
    rows = (len(MOOD_WORDS) + cols - 1) // cols

    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row + col * rows
            if idx < len(MOOD_WORDS):
                line += f"  {MOOD_WORDS[idx]:<15}"
        console.print(line)

    console.print()


@main.command()
@click.option("--output", "-o", type=click.Path(), default="./thumbnail.png", help="Output path")
def thumbnail(output):
    """Generate a thumbnail image with dynamic prompt."""
    console.print("\n[cyan]Generating thumbnail...[/cyan]")
    console.print(f"  Output: {output}\n")

    try:
        config = load_config()
        from suno_mixer.thumbnail import ThumbnailGenerator

        generator = ThumbnailGenerator(config.thumbnail)
        result = asyncio.run(generator.generate(Path(output)))

        console.print(f"[green]Thumbnail saved:[/green] {result}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    "input_dir",
    required=True,
    type=click.Path(exists=True),
    help="Input directory with MP3 files",
)
@click.option("--output", "-o", required=True, type=click.Path(), help="Output file path")
@click.option("--crossfade", "-c", default=10, help="Crossfade duration in seconds")
def mix(input_dir, output, crossfade):
    """Mix existing local audio tracks."""
    input_path = Path(input_dir)
    output_path = Path(output)

    # Find MP3 files
    tracks = sorted(input_path.glob("*.mp3"))

    if not tracks:
        console.print(f"[red]No MP3 files found in {input_dir}[/red]")
        sys.exit(1)

    console.print(f"\n[cyan]Mixing {len(tracks)} tracks...[/cyan]")
    console.print(f"  Crossfade: {crossfade}s")
    console.print(f"  Output: {output}\n")

    try:
        config = load_config()
        config.mixer.crossfade_duration_ms = crossfade * 1000

        from suno_mixer.audio.mixer import AudioMixer

        mixer = AudioMixer(config.mixer)
        result = mixer.create_mix(tracks, output_path)

        console.print(f"[green]Mix saved:[/green] {result}")
        console.print(f"[green]Duration:[/green] {format_duration(mixer.get_duration(result))}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.argument("mix_path", type=click.Path(exists=True))
@click.option(
    "--privacy",
    "-p",
    default="private",
    type=click.Choice(["private", "unlisted", "public"]),
    help="Video privacy status",
)
@click.option(
    "--secrets",
    "-s",
    type=click.Path(),
    default="credentials.json",
    envvar="YOUTUBE_CLIENT_SECRETS_PATH",
    help="Path to OAuth client secrets JSON (default: credentials.json)",
)
@click.pass_context
def publish(ctx, mix_path, privacy, secrets):
    """Publish a mix to YouTube.

    MIX_PATH is the directory containing the generated mix files.

    Example:
        suno-mixer publish output/focus_dark_synthwave --privacy unlisted
    """
    import json

    from suno_mixer.youtube import YouTubeClient, YouTubeError

    mix_dir = Path(mix_path)
    console.print("\n[bold cyan]Publishing to YouTube[/bold cyan]\n")

    # Find metadata JSON file
    json_files = list(mix_dir.glob("*.json"))
    if not json_files:
        console.print(f"[red]No metadata JSON found in {mix_dir}[/red]")
        sys.exit(1)

    metadata_path = json_files[0]
    with open(metadata_path) as f:
        metadata = json.load(f)

    # Find video and thumbnail files
    video_files = list(mix_dir.glob("*.mp4"))
    thumb_files = list(mix_dir.glob("*_yt_thumb.png"))

    if not video_files:
        console.print(f"[red]No video file found in {mix_dir}[/red]")
        sys.exit(1)

    video_path = video_files[0]
    thumbnail_path = thumb_files[0] if thumb_files else None

    # Display what we're uploading
    console.print(f"  [bold]Title:[/bold]     {metadata['title']}")
    console.print(f"  [bold]Video:[/bold]     {video_path.name}")
    console.print(f"  [bold]Thumbnail:[/bold] {thumbnail_path.name if thumbnail_path else 'None'}")
    console.print(f"  [bold]Privacy:[/bold]   {privacy}")
    console.print()

    # Check for secrets file
    secrets_path = Path(secrets)
    if not secrets_path.exists():
        console.print(f"[red]YouTube client secrets not found: {secrets}[/red]")
        console.print("Set YOUTUBE_CLIENT_SECRETS_PATH or use --secrets flag.")
        console.print("\nTo get credentials:")
        console.print("1. Go to Google Cloud Console")
        console.print("2. Enable YouTube Data API v3")
        console.print("3. Create OAuth 2.0 credentials (Desktop app)")
        console.print("4. Download as client_secrets.json")
        sys.exit(1)

    try:
        client = YouTubeClient(secrets_path)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            progress.add_task("[cyan]Uploading video...", total=None)

            video_id = client.upload(
                video_path=video_path,
                title=metadata["title"],
                description=metadata["description"],
                tags=metadata.get("tags", []),
                privacy=privacy,
                thumbnail_path=thumbnail_path,
            )

        console.print("\n[bold green]Published![/bold green]")
        console.print(f"\n  Video ID: {video_id}")
        console.print(f"  URL: https://youtube.com/watch?v={video_id}\n")

        # Update metadata with YouTube info
        metadata["youtube_id"] = video_id
        metadata["youtube_url"] = f"https://youtube.com/watch?v={video_id}"

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        console.print(f"[dim]Metadata updated: {metadata_path}[/dim]\n")

    except YouTubeError as e:
        console.print(f"\n[bold red]YouTube Error:[/bold red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        if ctx.obj.get("verbose"):
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
