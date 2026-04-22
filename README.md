# Wiki — Manual do Mundo

Automated wiki for the YouTube channel [Manual do Mundo](https://www.youtube.com/MANUALDOMUNDO). A Python pipeline downloads video metadata and subtitles, analyzes them with AI, and generates a static [MkDocs](https://squidfunk.github.io/mkdocs-material/) site deployable to GitHub Pages.

## How it works

```
yt-dlp → data/raw/ → AI analysis → data/processed/ → MkDocs pages → GitHub Pages
```

Each video gets its own wiki page with an AI-generated summary, categories, topics, and links to related videos mentioned in the description.

---

## Requirements

- Python 3.11+
- A [pyenv](https://github.com/pyenv/pyenv) virtualenv (or any Python virtualenv)
- An AI provider API key (see step 2)

---

## Setup

### 1. Install dependencies

```bash
# Create and activate a virtualenv (example using pyenv-virtualenv)
pyenv virtualenv 3.11.11 wiki
pyenv activate wiki

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials. You need **one** of the following AI providers:

#### Option A — Google Gemini (free tier, recommended to start)
1. Go to [aistudio.google.com](https://aistudio.google.com) and create an API key
2. Set in `.env`:
```
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```
Free tier limits: 30 requests/min, 1,500 requests/day. Resets at midnight Pacific.

#### Option B — Anthropic Claude (paid, ~$0.01 per video)
1. Go to [console.anthropic.com](https://console.anthropic.com), add billing, and create an API key
2. Set in `.env`:
```
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
```

#### Option C — Ollama (local, fully free)
1. Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.2`
2. Set in `.env`:
```
AI_PROVIDER=ollama
OLLAMA_MODEL=llama3.2
```

---

## Running the pipeline

### Full pipeline (fetch → analyze → generate)

```bash
python pipeline.py
```

### Step by step

```bash
# 1. Download the last 10 videos (subtitles + metadata)
python pipeline.py --fetch

# 2. Analyze with AI and produce structured JSON
python pipeline.py --analyze

# 3. Generate MkDocs pages from the analysis
python pipeline.py --generate
```

### Single video (useful for testing)

```bash
# Fetch + analyze + generate one video by its YouTube ID
python pipeline.py --video-id <VIDEO_ID>

# Or individual steps
python pipeline.py --fetch --video-id <VIDEO_ID>
python pipeline.py --analyze --video-id <VIDEO_ID>

# Re-analyze a video that was already processed
python pipeline.py --analyze --video-id <VIDEO_ID> --force
```

To find a video ID: it's the part after `?v=` in the YouTube URL.  
Example: `https://www.youtube.com/watch?v=3gmyg-kLQ-s` → ID is `3gmyg-kLQ-s`

### Change how many videos to fetch

Edit `scraper/config.yaml`:

```yaml
max_videos: 10  # increase this to fetch more
```

---

## Previewing the wiki locally

```bash
python pipeline.py --generate
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Publishing to GitHub Pages

### First time setup

1. Create a GitHub repository and push the code:
```bash
git remote add origin https://github.com/<your-username>/wiki-manual-do-mundo.git
git push -u origin main
```

2. Update `site_url` in `mkdocs.yml` to match your GitHub Pages URL:
```yaml
site_url: https://<your-username>.github.io/wiki-manual-do-mundo
```

### Deploy

```bash
mkdocs gh-deploy
```

This builds the site and pushes it to the `gh-pages` branch. GitHub Pages will serve it automatically.

**Note:** `data/` and generated `docs/` content are in `.gitignore` — only the pipeline code is committed. Each deploy runs the pipeline locally and pushes the built site.

---

## Project structure

```
wiki-manual-do-mundo/
├── scraper/          # yt-dlp wrapper — downloads subtitles and metadata
├── analyzer/         # AI client and analysis logic
├── generator/        # Builds MkDocs .md pages from analysis JSON
├── data/
│   ├── raw/          # Downloaded subtitles and metadata (gitignored)
│   └── processed/    # AI analysis output JSON (gitignored)
├── docs/             # Generated MkDocs source (gitignored)
├── pipeline.py       # Main entry point
├── mkdocs.yml        # MkDocs configuration
└── requirements.txt
```

Each component has its own `CLAUDE.md` with detailed documentation.

---

## Branch policy

`main` is the stable branch. Every change after the initial version must be made in a new branch and merged via pull request.

```bash
git checkout -b feature/my-change
# make changes
git push origin feature/my-change
# open a pull request
```
