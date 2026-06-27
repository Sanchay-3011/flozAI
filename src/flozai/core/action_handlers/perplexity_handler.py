"""
Perplexity Handler — Web search via Perplexity Sonar API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class PerplexityHandler:
    BASE_URL = "https://api.perplexity.ai"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        api_key = credentials.get("apiKey") or credentials.get("access_token")
        if not api_key:
            raise ValueError("Perplexity API key not found. Please add your key.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(api_key):
            query = params.get("query", params.get("prompt", "Mock search query"))
            return {
                "status": "success",
                "content": f"Simulated Perplexity search response for: '{query}'",
                "query": query,
                "simulated": True
            }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        if action in ("web_search", "ai_search", "search"):
            return self._search(headers, params, context)
        raise ValueError(f"Unknown Perplexity action: {action}")

    def _search(self, headers: dict, params: dict, context: dict) -> dict:
        query = params.get("query", params.get("prompt", ""))
        if not query:
            for val in context.values():
                if isinstance(val, dict) and val.get("content"):
                    query = f"Search for: {val['content'][:200]}"
                    break
            if not query:
                query = "Latest technology news"

        resp = http_requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{"role": "user", "content": query}],
                "max_tokens": 500,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"status": "success", "content": content, "query": query}
        raise ValueError(f"Perplexity API error ({resp.status_code}): {resp.text[:200]}")
