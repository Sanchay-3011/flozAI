"""
LinkedIn Handler — Publish posts via LinkedIn Marketing API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class LinkedInHandler:
    BASE_URL = "https://api.linkedin.com/v2"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("LinkedIn OAuth token not found. Please re-authorize.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            return {"status": "published", "post_id": "urn:li:share:mock-linkedin-post-id", "simulated": True}

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"}

        if action in ("create_post", "publish_post", "post"):
            return self._create_post(headers, params, context)
        raise ValueError(f"Unknown LinkedIn action: {action}")

    def _create_post(self, headers: dict, params: dict, context: dict) -> dict:
        text = params.get("text", params.get("content", params.get("message", "")))
        if not text:
            for val in context.values():
                if isinstance(val, dict) and val.get("content"):
                    text = val["content"][:2000]
                    break
            if not text:
                raise ValueError("No post content specified.")

        # First, get the user's URN
        me_resp = http_requests.get(f"{self.BASE_URL}/userinfo", headers=headers, timeout=10)
        if me_resp.status_code != 200:
            raise ValueError(f"Could not fetch LinkedIn profile: {me_resp.text[:200]}")

        person_urn = f"urn:li:person:{me_resp.json().get('sub', '')}"

        body = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        resp = http_requests.post(f"{self.BASE_URL}/ugcPosts", headers=headers, json=body, timeout=15)
        if resp.status_code in (200, 201):
            return {"status": "published", "post_id": resp.json().get("id", "")}
        raise ValueError(f"LinkedIn API error ({resp.status_code}): {resp.text[:200]}")
