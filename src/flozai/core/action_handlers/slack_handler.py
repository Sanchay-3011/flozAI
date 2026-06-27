"""
Slack Action Handler
Posts messages to Slack channels via the Slack Web API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class SlackHandler:
    """Handles Slack actions (send message, post to channel)."""
    
    BASE_URL = "https://slack.com/api"
    
    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        token = credentials.get("access_token") or credentials.get("apiKey")
        if not token:
            raise ValueError("Slack token not found. Please connect Slack.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(token):
            channel = params.get("channel", "#general")
            message = params.get("message", params.get("text", "Mock Slack message"))
            return {
                "status": "sent",
                "channel": channel,
                "ts": "mock-ts-123456.789",
                "simulated": True,
                "message": message
            }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        if action in ("send_slack", "send_message", "post_message"):
            return self._post_message(headers, params, context)
        else:
            raise ValueError(f"Unknown Slack action: {action}")
    
    def _post_message(self, headers: dict, params: dict, context: dict) -> dict:
        channel = params.get("channel", "#general")
        message = params.get("message", params.get("text", ""))
        
        if not message:
            # Build a default message from context
            parts = []
            for key, val in context.items():
                if isinstance(val, dict):
                    parts.append(f"• {key}: {val.get('status', str(val))}")
            message = f"🤖 FlozAI Workflow Update:\n" + "\n".join(parts) if parts else "FlozAI workflow executed successfully."
        
        resp = http_requests.post(
            f"{self.BASE_URL}/chat.postMessage",
            headers=headers,
            json={"channel": channel, "text": message},
            timeout=15
        )
        
        data = resp.json()
        
        if data.get("ok"):
            return {"status": "sent", "channel": data.get("channel"), "ts": data.get("ts")}
        else:
            error = data.get("error", "unknown_error")
            raise ValueError(f"Slack API error: {error}")
