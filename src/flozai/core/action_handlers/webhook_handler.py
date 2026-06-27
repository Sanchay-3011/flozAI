"""
Webhook Action Handler
Sends/receives HTTP webhooks.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class WebhookHandler:
    """Handles webhook actions (send HTTP request, receive webhook)."""
    
    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        if action in ("send_webhook", "http_request"):
            return self._send_webhook(params, context)
        elif action in ("receive_webhook", "webhook"):
            return {"status": "listening", "message": "Webhook listener is active."}
        else:
            raise ValueError(f"Unknown webhook action: {action}")
    
    def _send_webhook(self, params: dict, context: dict) -> dict:
        url = params.get("url", params.get("webhook_url", ""))
        method = params.get("method", "POST").upper()
        
        if not url:
            raise ValueError("No webhook URL specified. Provide a 'url' parameter.")
        
        # Build payload from params or context
        payload = params.get("body", params.get("data", {}))
        if not payload and context:
            payload = {k: v for k, v in context.items() if isinstance(v, dict)}
        
        headers = params.get("headers", {"Content-Type": "application/json"})
        
        if method == "GET":
            resp = http_requests.get(url, headers=headers, timeout=15)
        else:
            resp = http_requests.request(method, url, headers=headers, json=payload, timeout=15)
        
        return {
            "status": "sent",
            "method": method,
            "url": url,
            "response_code": resp.status_code,
            "response_body": resp.text[:500]
        }
