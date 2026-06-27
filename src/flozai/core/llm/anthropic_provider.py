"""
Anthropic (Claude) LLM Provider
"""
import requests as http_requests
from flozai.core.llm.llm_client import LLMClient
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class AnthropicProvider(LLMClient):
    provider_name = "anthropic"
    BASE_URL = "https://api.anthropic.com/v1"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self._model = model or "claude-3-5-haiku-latest"

    @property
    def default_model(self) -> str:
        return self._model

    def _raw_chat(self, system_prompt: str, user_prompt: str, model: str = None, max_tokens: int = 800) -> str:
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(self.api_key):
            return f"[Simulated Response from Anthropic {model or self._model}] System: {system_prompt} | User: {user_prompt}"

        resp = http_requests.post(
            f"{self.BASE_URL}/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": model or self._model,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Anthropic returns content as array of blocks
            blocks = data.get("content", [])
            return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        elif resp.status_code == 401:
            raise ValueError("Invalid Anthropic API key. Please check your key in AI Settings.")
        elif resp.status_code == 429:
            raise ValueError("Anthropic rate limit reached. Please wait a moment and try again.")
        else:
            raise ValueError(f"Anthropic error ({resp.status_code}): {resp.text[:200]}")
