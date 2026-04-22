VIDEO_ANALYSIS_PROMPT = """You are analyzing a video from the Brazilian YouTube channel "Manual do Mundo" (which means "World Manual" or "How-To World"). The channel covers science experiments, DIY projects, curiosities, and educational content, all in Brazilian Portuguese.

Given the video metadata and subtitle transcript below, return a JSON object with the following fields:

- "categorias": list of 1-3 category strings in Portuguese (e.g. "Ciência", "Faça Você Mesmo", "Culinária", "Tecnologia", "Natureza", "Química", "Física", "Curiosidades")
- "resumo": a 2-4 sentence summary in Brazilian Portuguese describing what the video is about and what the viewer will learn
- "topicos": list of 3-6 specific topic strings in Portuguese (e.g. "vulcão de bicarbonato", "reação química", "experiência caseira")

Return ONLY valid JSON, no markdown, no explanation.

---
VIDEO TITLE: {titulo}
PLAYLIST: {playlist}
TAGS: {tags}

DESCRIPTION:
{descricao}

SUBTITLE TRANSCRIPT (auto-generated, may have errors):
{subtitles}
---
"""
