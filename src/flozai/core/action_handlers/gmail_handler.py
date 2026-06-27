"""
Gmail Action Handler
Sends emails via Gmail API using OAuth tokens.
"""
import base64
from email.mime.text import MIMEText
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class GmailHandler:
    """Handles Gmail actions (send email, read emails)."""
    
    BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
    
    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("Gmail OAuth token not found. Please re-authorize Gmail.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            if action in ("send_email", "send_gmail"):
                to = params.get("to", params.get("recipient", "mock@example.com"))
                return {"status": "sent", "message_id": "mock-gmail-msg-id", "to": to, "simulated": True}
            elif action in ("read_emails", "new_email"):
                return {
                    "status": "success",
                    "count": 2,
                    "message_ids": ["mock-msg-1", "mock-msg-2"],
                    "simulated": True
                }

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        if action in ("send_email", "send_gmail"):
            return self._send_email(headers, params, context)
        elif action in ("read_emails", "new_email"):
            return self._list_emails(headers, params)
        else:
            raise ValueError(f"Unknown Gmail action: {action}")
    
    def _send_email(self, headers: dict, params: dict, context: dict) -> dict:
        to = params.get("to", params.get("recipient", ""))
        subject = params.get("subject", "FlozAI Automated Email")
        body = params.get("body", params.get("message", "This is an automated email from FlozAI."))
        
        # Use context from previous steps if available
        if not to:
            for key, val in context.items():
                if isinstance(val, dict) and val.get("email"):
                    to = val["email"]
                    break
        
        if not to:
            raise ValueError("No recipient email specified. Provide a 'to' parameter.")
        
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        
        resp = http_requests.post(
            f"{self.BASE_URL}/messages/send",
            headers=headers,
            json={"raw": raw},
            timeout=15
        )
        
        if resp.status_code == 200:
            msg_data = resp.json()
            return {"status": "sent", "message_id": msg_data.get("id"), "to": to}
        else:
            raise ValueError(f"Gmail API error ({resp.status_code}): {resp.text[:200]}")
    
    def _list_emails(self, headers: dict, params: dict) -> dict:
        max_results = params.get("max_results", 5)
        resp = http_requests.get(
            f"{self.BASE_URL}/messages?maxResults={max_results}",
            headers=headers,
            timeout=15
        )
        
        if resp.status_code == 200:
            messages = resp.json().get("messages", [])
            return {"status": "success", "count": len(messages), "message_ids": [m["id"] for m in messages]}
        else:
            raise ValueError(f"Gmail API error ({resp.status_code}): {resp.text[:200]}")
