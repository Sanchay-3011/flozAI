"""
WhatsApp Handler — Send messages via WhatsApp Business Cloud API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class WhatsAppHandler:
    BASE_URL = "https://graph.facebook.com/v18.0"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("apiKey") or credentials.get("access_token")
        if not access_token:
            raise ValueError("WhatsApp Business API token not found. Please add your token.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            return {"status": "sent", "message_id": "wamid.HBgLOTE5ODc2NTQzMjEwFQIAERgSQjUzMzRDNDc4MkFBMzUxNTNFAA==", "simulated": True}

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        if action in ("send_message", "send_whatsapp"):
            return self._send_message(headers, credentials, params, context)
        raise ValueError(f"Unknown WhatsApp action: {action}")

    def _send_message(self, headers: dict, credentials: dict, params: dict, context: dict) -> dict:
        phone_number_id = credentials.get("phone_number_id", params.get("phone_number_id", ""))
        to = params.get("to", params.get("recipient", ""))
        message = params.get("message", params.get("text", ""))

        if not phone_number_id:
            raise ValueError("WhatsApp phone_number_id is required. Set it in your credentials.")
        if not to:
            raise ValueError("Recipient phone number (to) is required.")
        if not message:
            message = "Hello from FlozAI!"

        resp = http_requests.post(
            f"{self.BASE_URL}/{phone_number_id}/messages",
            headers=headers,
            json={
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": message},
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "sent", "message_id": data.get("messages", [{}])[0].get("id")}
        raise ValueError(f"WhatsApp API error ({resp.status_code}): {resp.text[:200]}")
