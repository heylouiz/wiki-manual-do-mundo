#!/usr/bin/env python3
"""
Main pipeline: fetch → analyze → generate → (optionally) build.

Usage:
  python pipeline.py                          # run full pipeline
  python pipeline.py --fetch                  # only fetch videos
  python pipeline.py --analyze                # only analyze all fetched videos
  python pipeline.py --analyze --video-id ID  # analyze a single video
  python pipeline.py --fetch --video-id ID    # fetch a single video
  python pipeline.py --generate               # only generate docs
  python pipeline.py --build                  # only build site
  python pipeline.py --serve                  # generate + serve locally
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scraper"))
sys.path.insert(0, str(Path(__file__).parent / "analyzer"))
sys.path.insert(0, str(Path(__file__).parent / "generator"))


def run_fetch(video_id: str | None = None):
    print("=== FETCH ===")
    from fetch import fetch_channel, fetch_single, load_config
    config = load_config()
    if video_id:
        fetch_single(video_id, config)
    else:
        fetch_channel(config)


def run_analyze(force: bool = False, video_id: str | None = None):
    print("=== ANALYZE ===")
    from analyze import analyze_video
    from ai_client import AIClient

    raw_dir = Path(__file__).parent / "data" / "raw"
    client = AIClient()

    if video_id:
        analyze_video(video_id, client, force=force)
        return

    video_ids = [d.name for d in raw_dir.iterdir() if d.is_dir()]
    if not video_ids:
        print("No raw videos found. Run --fetch first.")
        return
    for vid in sorted(video_ids):
        analyze_video(vid, client, force=force)


def run_generate():
    print("=== GENERATE ===")
    from generate import main as generate_main
    generate_main()


def run_build():
    print("=== BUILD ===")
    subprocess.run(["mkdocs", "build"], check=True)


def run_serve():
    print("=== SERVE ===")
    subprocess.run(["mkdocs", "serve"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Manual do Mundo wiki pipeline")
    parser.add_argument("--fetch", action="store_true", help="Only fetch videos")
    parser.add_argument("--analyze", action="store_true", help="Only analyze videos")
    parser.add_argument("--generate", action="store_true", help="Only generate docs")
    parser.add_argument("--build", action="store_true", help="Only build site")
    parser.add_argument("--serve", action="store_true", help="Generate and serve locally")
    parser.add_argument("--force", action="store_true", help="Re-analyze already processed videos")
    parser.add_argument("--video-id", dest="video_id", help="Target a single video by ID (works with --fetch and --analyze)")
    args = parser.parse_args()

    any_flag = args.fetch or args.analyze or args.generate or args.build or args.serve

    if not any_flag or args.fetch:
        run_fetch(video_id=args.video_id)
    if not any_flag or args.analyze:
        run_analyze(force=args.force, video_id=args.video_id)
    if not any_flag or args.generate or args.serve:
        run_generate()
    if args.build:
        run_build()
    if args.serve:
        run_serve()


if __name__ == "__main__":
    main()
