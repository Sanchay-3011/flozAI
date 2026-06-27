"""
Groq LLM Provider
"""
import requests as http_requests
from flozai.core.llm.llm_client import LLMClient
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class GroqProvider(LLMClient):
    provider_name = "groq"
    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self._model = model or "llama-3.3-70b-versatile"

    @property
    def default_model(self) -> str:
        return self._model

    def _raw_chat(self, system_prompt: str, user_prompt: str, model: str = None, max_tokens: int = 800) -> str:
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(self.api_key):
            return f"[Simulated Response from Groq {model or self._model}] System: {system_prompt} | User: {user_prompt}"

        resp = http_requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": model or self._model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        elif resp.status_code == 401:
            raise ValueError("Invalid Groq API key. Please check your key in AI Settings.")
        elif resp.status_code == 429:
            raise ValueError("Groq rate limit reached. Please wait a moment and try again.")
        else:
            raise ValueError(f"Groq error ({resp.status_code}): {resp.text[:200]}")
