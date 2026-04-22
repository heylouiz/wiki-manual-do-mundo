import os
import time
from dotenv import load_dotenv

load_dotenv()

_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
# Delay between requests to stay well under the 30 RPM free-tier limit
_GEMINI_REQUEST_DELAY = float(os.getenv("GEMINI_REQUEST_DELAY", "3"))
_CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
_MAX_RETRIES = 3


class AIClient:
    def __init__(self):
        self._provider = _PROVIDER
        self._client = self._build_client()

    def complete(self, prompt: str) -> str:
        if self._provider == "gemini":
            return self._complete_gemini(prompt)
        elif self._provider == "claude":
            return self._complete_claude(prompt)
        elif self._provider == "ollama":
            return self._complete_ollama(prompt)
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {self._provider}")

    def _build_client(self):
        if self._provider == "gemini":
            from google import genai
            return genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        elif self._provider == "claude":
            import anthropic
            return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        elif self._provider == "ollama":
            return None
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {self._provider}")

    def _complete_gemini(self, prompt: str) -> str:
        from google.genai.errors import ClientError
        time.sleep(_GEMINI_REQUEST_DELAY)
        for attempt in range(_MAX_RETRIES):
            try:
                response = self._client.models.generate_content(
                    model=_GEMINI_MODEL,
                    contents=prompt,
                )
                return response.text
            except ClientError as e:
                error_str = str(e)
                is_rate_limit = "429" in error_str
                # Daily quota exhausted — retrying won't help, fail immediately
                is_daily_exhausted = is_rate_limit and (
                    "per_day" in error_str.lower()
                    or "GenerateRequestsPerDay" in error_str
                    or "limit: 0" in error_str
                )
                if is_daily_exhausted:
                    raise RuntimeError(
                        "Daily Gemini free-tier quota exhausted. "
                        "Wait until midnight Pacific time or set GEMINI_MODEL=gemini-2.5-flash "
                        "and enable billing."
                    ) from e
                if is_rate_limit and attempt < _MAX_RETRIES - 1:
                    wait = 60 * (attempt + 1)
                    print(f"  Rate limited (RPM), waiting {wait}s before retry...")
                    time.sleep(wait)
                else:
                    raise

    def _complete_claude(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=_CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def _complete_ollama(self, prompt: str) -> str:
        import requests
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2")
        response = requests.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return response.json()["response"]
