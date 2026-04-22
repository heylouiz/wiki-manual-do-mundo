# Generator Component

## Purpose
Reads all `data/processed/<video_id>/analysis.json` files and generates MkDocs Markdown pages under `docs/`. One page per video, one page per category, plus an index page.

## Entry point
```bash
python generator/generate.py   # regenerate all docs/ pages from processed data
```

## Output structure under `docs/`
```
docs/
├── index.md              # homepage: latest videos + category list
├── videos/
│   └── <video_id>.md     # one page per video
└── categorias/
    └── <slug>.md         # one page per category (aggregated)
```

## Page content
**Video page** (`docs/videos/<video_id>.md`):
- Title, publication date, playlist
- Embedded YouTube iframe
- AI-generated summary (in Portuguese)
- Topics (tags)
- Related videos (cross-references from description links)

**Category page** (`docs/categorias/<slug>.md`):
- Category name
- List of all videos in that category, sorted by date

**Index page** (`docs/index.md`):
- 10 most recent videos
- All categories with video count

## Templating
Pages are built with Jinja2 templates in `generator/templates/`:
- `video.md.j2`
- `categoria.md.j2`
- `index.md.j2`

Edit templates to change page layout without touching generation logic.

## Key decisions
- `docs/` is fully regenerated on every run — do not manually edit files there.
- MkDocs nav is written programmatically to `mkdocs.yml` under the `nav:` key by this generator, so pages are always in sync.
- Category slugs are derived from playlist names: lowercased, spaces replaced with hyphens, accents stripped.

## Extending
- To add a new page type (e.g. per-topic pages): add a template in `templates/` and a generation function in `generate.py`.
- To change summary language or format: edit `generator/templates/video.md.j2`.
