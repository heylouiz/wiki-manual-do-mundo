# Analyzer Component

## Purpose
Reads raw data from `data/raw/` and sends it to an AI model to produce structured analysis per video. Outputs JSON to `data/processed/<video_id>/analysis.json`.

## Entry point
```bash
python analyzer/analyze.py              # analyze all unprocessed videos
python analyzer/analyze.py --video-id <id>  # analyze a single video
```

## Output format (`data/processed/<video_id>/analysis.json`)
```json
{
  "video_id": "...",
  "titulo": "...",
  "data_publicacao": "YYYY-MM-DD",
  "playlist": "...",
  "categorias": ["...", "..."],
  "resumo": "Short Portuguese summary of what the video is about",
  "topicos": ["topic1", "topic2"],
  "links_relacionados": [
    {"video_id": "...", "url": "https://youtu.be/..."}
  ],
  "url": "https://youtu.be/..."
}
```

## AI provider abstraction (`ai_client.py`)
The `AIClient` class has a single public method:
```python
client = AIClient()
response: str = client.complete(prompt)
```
Switch providers by setting `AI_PROVIDER` in `.env`:
- `gemini` (default) — Google Gemini 1.5 Flash, free tier
- `claude` — Anthropic Claude (requires `ANTHROPIC_API_KEY`)
- `ollama` — local Ollama instance (requires `OLLAMA_MODEL` and `OLLAMA_HOST`)

## Key decisions
- Cross-references extracted from video description URLs only (not subtitle text) in v1.
- AI is prompted in English but instructed to return content fields in Brazilian Portuguese.
- Structured output is enforced by asking the model to return JSON; response is parsed and validated with `pydantic`.
- Already-processed videos are skipped unless `--force` flag is passed.

## Prompts (`prompts.py`)
All prompt templates live here. Keep them in this file so they are easy to update without touching analysis logic.

## Extending
- To add subtitle-based cross-reference detection: add a second prompt in `prompts.py` and a second AI call in `analyze.py`.
- To switch AI provider: set `AI_PROVIDER=claude` in `.env` and add `ANTHROPIC_API_KEY`.
