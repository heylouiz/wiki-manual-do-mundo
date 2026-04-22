import os
from dotenv import load_dotenv

load_dotenv()

_PROVIDER = os.getenv("AI_PROVIDER", "gemini")


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
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            return genai.GenerativeModel("gemini-1.5-flash")
        elif self._provider == "claude":
            import anthropic
            return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        elif self._provider == "ollama":
            return None
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {self._provider}")

    def _complete_gemini(self, prompt: str) -> str:
        response = self._client.generate_content(prompt)
        return response.text

    def _complete_claude(self, prompt: str) -> str:
        message = self._client.messages.create(
            model="claude-sonnet-4-6",
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
