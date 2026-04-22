import argparse
import json
import os
import re
import sys
from pathlib import Path

import yaml
import yt_dlp

CONFIG_PATH = Path(__file__).parent / "config.yaml"
PROJECT_ROOT = Path(__file__).parent.parent


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def output_dir(config: dict) -> Path:
    return PROJECT_ROOT / config["output_dir"]


def fetch_channel(config: dict) -> None:
    out = output_dir(config)
    out.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [config["language"]],
        "subtitlesformat": "vtt",
        "skip_download": True,
        "playlistend": config["max_videos"],
        "outtmpl": str(out / "%(id)s/%(id)s.%(ext)s"),
        "writeinfojson": True,
        "ignoreerrors": True,
    }

    url = f"{config['channel_url']}/videos"
    print(f"Fetching last {config['max_videos']} videos from {url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    _normalize_raw_output(out, config["language"])


def fetch_single(video_id: str, config: dict) -> None:
    out = output_dir(config)
    out.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": [config["language"]],
        "subtitlesformat": "vtt",
        "skip_download": True,
        "outtmpl": str(out / f"{video_id}/{video_id}.%(ext)s"),
        "writeinfojson": True,
        "ignoreerrors": True,
    }

    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Fetching video {video_id}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    _normalize_raw_output(out / video_id, config["language"], single=True)


def _normalize_raw_output(base: Path, lang: str, single: bool = False) -> None:
    """Rename yt-dlp output files to canonical names and extract metadata.json."""
    dirs = [base] if single else [d for d in base.iterdir() if d.is_dir()]

    for video_dir in dirs:
        video_id = video_dir.name

        # Find and rename info json
        for f in video_dir.glob("*.info.json"):
            with open(f) as fh:
                info = json.load(fh)
            metadata = _extract_metadata(info)
            with open(video_dir / "metadata.json", "w") as fh:
                json.dump(metadata, fh, ensure_ascii=False, indent=2)
            f.unlink()

        # Find and rename subtitle file
        for f in video_dir.glob(f"*.{lang}.vtt"):
            f.rename(video_dir / "subtitles.vtt")
            break

        print(f"  Saved {video_id}")


def _extract_metadata(info: dict) -> dict:
    youtube_urls = _extract_youtube_urls(info.get("description", ""))
    return {
        "video_id": info.get("id"),
        "titulo": info.get("title"),
        "descricao": info.get("description", ""),
        "data_publicacao": info.get("upload_date"),
        "playlist": info.get("playlist_title") or info.get("playlist"),
        "tags": info.get("tags", []),
        "url": f"https://www.youtube.com/watch?v={info.get('id')}",
        "links_na_descricao": youtube_urls,
    }


def _extract_youtube_urls(text: str) -> list[str]:
    pattern = r"(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+)"
    return list(set(re.findall(pattern, text)))


def main():
    parser = argparse.ArgumentParser(description="Fetch Manual do Mundo videos")
    parser.add_argument("--video-id", help="Fetch a single video by ID")
    args = parser.parse_args()

    config = load_config()

    if args.video_id:
        fetch_single(args.video_id, config)
    else:
        fetch_channel(config)


if __name__ == "__main__":
    main()
