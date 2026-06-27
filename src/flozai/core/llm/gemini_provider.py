"""
Google Gemini LLM Provider
"""
import requests as http_requests
from flozai.core.llm.llm_client import LLMClient
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(LLMClient):
    provider_name = "gemini"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self._model = model or "gemini-2.0-flash"

    @property
    def default_model(self) -> str:
        return self._model

    def _raw_chat(self, system_prompt: str, user_prompt: str, model: str = None, max_tokens: int = 800) -> str:
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(self.api_key):
            return f"[Simulated Response from Gemini {model or self._model}] System: {system_prompt} | User: {user_prompt}"

        use_model = model or self._model
        resp = http_requests.post(
            f"{self.BASE_URL}/models/{use_model}:generateContent?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7,
                },
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts)
            return ""
        elif resp.status_code == 400 and "API_KEY_INVALID" in resp.text:
            raise ValueError("Invalid Gemini API key. Please check your key in AI Settings.")
        elif resp.status_code == 429:
            raise ValueError("Gemini rate limit reached. Please wait a moment and try again.")
        else:
            raise ValueError(f"Gemini error ({resp.status_code}): {resp.text[:200]}")
