"""
OpenAI Action Handler
Generates content via OpenAI Chat Completions API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIHandler:
    """Handles OpenAI actions (generate content, summarize, analyze)."""
    
    BASE_URL = "https://api.openai.com/v1"
    
    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        api_key = credentials.get("apiKey") or credentials.get("access_token")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please add your key.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(api_key):
            prompt = params.get("prompt", params.get("message", "Summarize the data"))
            return {
                "status": "success",
                "content": f"Simulated OpenAI response for: '{prompt}'",
                "model": params.get("model", "gpt-4o-mini"),
                "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
                "simulated": True
            }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        if action in ("generate_content", "generate_ai_content", "ai_summarize", "ai_analyze"):
            return self._chat_completion(headers, params, context)
        else:
            raise ValueError(f"Unknown OpenAI action: {action}")
    
    def _chat_completion(self, headers: dict, params: dict, context: dict) -> dict:
        prompt = params.get("prompt", params.get("message", ""))
        model = params.get("model", "gpt-4o-mini")
        
        if not prompt:
            # Build prompt from context
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items() if isinstance(v, dict))
            prompt = f"Summarize the following workflow data:\n{context_str}" if context_str else "Generate a brief summary."
        
        resp = http_requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": params.get("max_tokens", 500),
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {
                "status": "success",
                "content": content,
                "model": model,
                "usage": data.get("usage", {})
            }
        else:
            raise ValueError(f"OpenAI API error ({resp.status_code}): {resp.text[:200]}")
