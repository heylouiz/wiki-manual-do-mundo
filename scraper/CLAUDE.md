# Scraper Component

## Purpose
Downloads video metadata, auto-generated Portuguese subtitles, and playlist membership for the Manual do Mundo YouTube channel using yt-dlp. Outputs raw JSON + VTT files to `data/raw/`.

## Entry point
```bash
python scraper/fetch.py              # fetch last N videos (configured in config.yaml)
python scraper/fetch.py --video-id <id>  # fetch a single video
```

## Output format
For each video, two files are written to `data/raw/<video_id>/`:
- `metadata.json` — title, description, upload date, playlist, YouTube URL, tags
- `subtitles.vtt` — auto-generated Portuguese subtitles from yt-dlp

## Key decisions
- Uses `yt-dlp` (not Scrapy or the YouTube Data API) — handles all YouTube-specific logic, rate limiting, and subtitle fetching without credentials.
- Fetches auto-generated subtitles (`--write-auto-sub --sub-lang pt`). These may have transcription errors; the analyzer uses AI to produce clean summaries instead of raw text.
- Cross-references are extracted from video **descriptions only** (link-based) in this version. Subtitle-based cross-reference detection is a future enhancement.
- Channel URL and fetch limit are configured in `scraper/config.yaml`, not hardcoded.

## Configuration (`scraper/config.yaml`)
```yaml
channel_url: https://www.youtube.com/MANUALDOMUNDO
max_videos: 10          # how many recent videos to fetch
language: pt            # subtitle language code
output_dir: data/raw
```

## Extending
- To add more channels: add entries under a `channels:` list in config.yaml and loop in `fetch.py`.
- To schedule fetches: wrap `fetch.py` in a GitHub Actions cron job calling `pipeline.py --fetch`.
