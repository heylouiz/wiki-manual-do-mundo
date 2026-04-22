import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

PROJECT_ROOT = Path(__file__).parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
TEMPLATES_DIR = Path(__file__).parent / "templates"
MKDOCS_YML = PROJECT_ROOT / "mkdocs.yml"


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def format_date(date_str: str | None) -> str:
    if not date_str or len(date_str) < 8:
        return "Data desconhecida"
    return f"{date_str[6:8]}/{date_str[4:6]}/{date_str[:4]}"


def load_all_analyses() -> list[dict]:
    analyses = []
    for path in PROCESSED_DIR.glob("*/analysis.json"):
        analyses.append(json.loads(path.read_text()))
    return sorted(analyses, key=lambda v: v.get("data_publicacao") or "", reverse=True)


def build_jinja_env() -> Environment:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), trim_blocks=True, lstrip_blocks=True)
    env.filters["slugify"] = slugify
    env.filters["format_date"] = format_date
    env.filters["truncate"] = lambda s, n: (s[:n] + "…") if len(s) > n else s
    return env


def generate_video_pages(videos: list[dict], env: Environment) -> list[str]:
    out_dir = DOCS_DIR / "videos"
    out_dir.mkdir(parents=True, exist_ok=True)
    template = env.get_template("video.md.j2")
    nav_entries = []

    for video in videos:
        # Try to link related videos to their titles
        for link in video.get("links_relacionados", []):
            linked = next((v for v in videos if v["video_id"] == link["video_id"]), None)
            link["titulo"] = linked["titulo"] if linked else link["video_id"]

        content = template.render(video=video)
        page_path = out_dir / f"{video['video_id']}.md"
        page_path.write_text(content, encoding="utf-8")
        nav_entries.append({video["titulo"]: f"videos/{video['video_id']}.md"})

    return nav_entries


def generate_category_pages(videos: list[dict], env: Environment) -> list[str]:
    out_dir = DOCS_DIR / "categorias"
    out_dir.mkdir(parents=True, exist_ok=True)
    template = env.get_template("categoria.md.j2")

    by_category: dict[str, list] = defaultdict(list)
    for video in videos:
        for cat in video.get("categorias", []):
            by_category[cat].append(video)

    nav_entries = []
    for cat, cat_videos in sorted(by_category.items()):
        content = template.render(categoria=cat, videos=cat_videos)
        slug = slugify(cat)
        page_path = out_dir / f"{slug}.md"
        page_path.write_text(content, encoding="utf-8")
        nav_entries.append({cat: f"categorias/{slug}.md"})

    return nav_entries, dict(by_category)


def generate_index(videos: list[dict], by_category: dict, env: Environment) -> None:
    template = env.get_template("index.md.j2")
    recent = videos[:10]
    categorias = sorted(
        [(cat, len(vids)) for cat, vids in by_category.items()],
        key=lambda x: x[1],
        reverse=True,
    )
    content = template.render(recent_videos=recent, categorias=categorias)
    (DOCS_DIR / "index.md").write_text(content, encoding="utf-8")


def update_mkdocs_nav(video_nav: list, cat_nav: list) -> None:
    if MKDOCS_YML.exists():
        with open(MKDOCS_YML) as f:
            config = yaml.safe_load(f)
    else:
        config = {}

    config["nav"] = [
        {"Início": "index.md"},
        {"Vídeos": video_nav},
        {"Categorias": cat_nav},
    ]

    with open(MKDOCS_YML, "w") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)


def main():
    videos = load_all_analyses()
    if not videos:
        print("No processed analyses found. Run the analyzer first.")
        return

    print(f"Generating pages for {len(videos)} videos...")
    env = build_jinja_env()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    video_nav = generate_video_pages(videos, env)
    cat_nav, by_category = generate_category_pages(videos, env)
    generate_index(videos, by_category, env)
    update_mkdocs_nav(video_nav, cat_nav)

    print(f"  {len(videos)} video pages")
    print(f"  {len(cat_nav)} category pages")
    print("Done. Run 'mkdocs serve' to preview or 'mkdocs gh-deploy' to publish.")


if __name__ == "__main__":
    main()
