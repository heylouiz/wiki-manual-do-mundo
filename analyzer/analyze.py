import argparse
import json
import re
import sys
from pathlib import Path

from ai_client import AIClient
from prompts import VIDEO_ANALYSIS_PROMPT

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def load_vtt(path: Path) -> str:
    """Strip VTT timing tags and return plain transcript text."""
    text = path.read_text(encoding="utf-8")
    # Remove WEBVTT header and timing lines
    lines = []
    for line in text.splitlines():
        if line.startswith("WEBVTT") or re.match(r"^\d{2}:\d{2}", line) or line.strip() == "":
            continue
        # Remove inline tags like <00:00:01.000><c>word</c>
        clean = re.sub(r"<[^>]+>", "", line).strip()
        if clean:
            lines.append(clean)
    # Deduplicate consecutive identical lines (common in auto-subs)
    deduped = [lines[0]] if lines else []
    for line in lines[1:]:
        if line != deduped[-1]:
            deduped.append(line)
    return " ".join(deduped)


def analyze_video(video_id: str, client: AIClient, force: bool = False) -> dict | None:
    raw_dir = RAW_DIR / video_id
    out_dir = PROCESSED_DIR / video_id
    out_file = out_dir / "analysis.json"

    if out_file.exists() and not force:
        print(f"  Skipping {video_id} (already processed, use --force to reanalyze)")
        return json.loads(out_file.read_text())

    metadata_path = raw_dir / "metadata.json"
    subtitle_path = raw_dir / "subtitles.vtt"

    if not metadata_path.exists():
        print(f"  Skipping {video_id}: metadata.json not found")
        return None

    metadata = json.loads(metadata_path.read_text())
    subtitles = load_vtt(subtitle_path) if subtitle_path.exists() else "(subtitles not available)"

    prompt = VIDEO_ANALYSIS_PROMPT.format(
        titulo=metadata["titulo"],
        playlist=metadata.get("playlist") or "N/A",
        tags=", ".join(metadata.get("tags", [])),
        descricao=metadata["descricao"][:2000],
        subtitles=subtitles[:6000],
    )

    print(f"  Analyzing {video_id}: {metadata['titulo']}")
    raw_response = client.complete(prompt)

    ai_data = _parse_json_response(raw_response)
    if ai_data is None:
        print(f"  Warning: could not parse AI response for {video_id}")
        ai_data = {"categorias": [], "resumo": "", "topicos": []}

    analysis = {
        "video_id": video_id,
        "titulo": metadata["titulo"],
        "data_publicacao": metadata.get("data_publicacao"),
        "playlist": metadata.get("playlist"),
        "url": metadata["url"],
        "links_relacionados": _resolve_links(metadata.get("links_na_descricao", [])),
        "categorias": ai_data.get("categorias", []),
        "resumo": ai_data.get("resumo", ""),
        "topicos": ai_data.get("topicos", []),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
    return analysis


def _parse_json_response(text: str) -> dict | None:
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _resolve_links(urls: list[str]) -> list[dict]:
    """Extract video IDs from YouTube URLs found in description."""
    results = []
    for url in urls:
        match = re.search(r"(?:v=|youtu\.be/)([\w\-]{11})", url)
        if match:
            results.append({"video_id": match.group(1), "url": url})
    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze downloaded videos with AI")
    parser.add_argument("--video-id", help="Analyze a single video by ID")
    parser.add_argument("--force", action="store_true", help="Re-analyze already processed videos")
    args = parser.parse_args()

    client = AIClient()

    if args.video_id:
        analyze_video(args.video_id, client, force=args.force)
    else:
        video_ids = [d.name for d in RAW_DIR.iterdir() if d.is_dir()]
        if not video_ids:
            print("No raw videos found. Run the scraper first.")
            sys.exit(1)
        print(f"Analyzing {len(video_ids)} videos...")
        for vid in sorted(video_ids):
            analyze_video(vid, client, force=args.force)


if __name__ == "__main__":
    main()
