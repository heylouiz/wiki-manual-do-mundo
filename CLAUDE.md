# Wiki Manual do Mundo — Project Root

## Overview
Automated wiki for the YouTube channel "Manual do Mundo". A Python pipeline downloads video metadata and subtitles via yt-dlp, analyzes them with an AI model, and generates a static MkDocs site deployable to GitHub Pages.

## Components
| Directory    | Purpose |
|--------------|---------|
| `scraper/`   | Downloads video metadata, subtitles, and playlist info via yt-dlp |
| `analyzer/`  | Sends data to AI and produces structured JSON analysis per video |
| `generator/` | Reads analysis JSON and writes MkDocs Markdown pages |
| `data/`      | Raw yt-dlp output (`raw/`) and AI analysis results (`processed/`) |
| `docs/`      | MkDocs source — auto-generated, do not edit manually |

## Running the full pipeline
```bash
python pipeline.py          # fetch → analyze → generate → build
python pipeline.py --fetch  # only fetch new videos
python pipeline.py --analyze  # only analyze
python pipeline.py --generate # only generate docs
mkdocs serve                # preview locally
mkdocs gh-deploy            # deploy to GitHub Pages
```

## Environment variables
```
GEMINI_API_KEY=...   # Google Gemini free tier (default AI provider)
```
Copy `.env.example` to `.env` and fill in the values.

## Branch policy
- `main` contains the stable version of the pipeline and generated site.
- **Every change after the initial version must be made in a new branch** and merged via pull request.
- Branch naming: `feature/<topic>`, `fix/<topic>`, `chore/<topic>`.

## Language conventions
- Code and comments: English
- Content (wiki pages, prompts context, summaries): Brazilian Portuguese
- Commit messages: English

## Adding a new AI provider
Edit `analyzer/ai_client.py`. The `AIClient` class exposes a single method `complete(prompt: str) -> str`. Swap the provider by changing `AI_PROVIDER` in `.env`.
