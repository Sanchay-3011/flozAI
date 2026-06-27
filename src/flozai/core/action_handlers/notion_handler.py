"""
Notion Handler — Create pages and database entries via Notion API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class NotionHandler:
    BASE_URL = "https://api.notion.com/v1"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        api_key = credentials.get("apiKey") or credentials.get("access_token")
        if not api_key:
            raise ValueError("Notion API key not found. Please add your integration secret.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(api_key):
            if action in ("create_page",):
                title = params.get("title", "FlozAI Page")
                return {"status": "created", "id": "mock-page-uuid", "title": title, "simulated": True}
            elif action in ("add_to_database", "create_record"):
                return {"status": "created", "id": "mock-entry-uuid", "simulated": True}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        if action in ("create_page",):
            return self._create_page(headers, params, context)
        elif action in ("add_to_database", "create_record"):
            return self._add_to_database(headers, params, context)
        raise ValueError(f"Unknown Notion action: {action}")

    def _create_page(self, headers: dict, params: dict, context: dict) -> dict:
        parent_id = params.get("parent_id", params.get("page_id", ""))
        title = params.get("title", "FlozAI Page")
        content = params.get("content", "")

        if not content:
            for val in context.values():
                if isinstance(val, dict) and val.get("content"):
                    content = val["content"]
                    break

        body = {
            "parent": {"page_id": parent_id} if parent_id else {"type": "page_id", "page_id": ""},
            "properties": {"title": [{"text": {"content": title}}]},
            "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": content or "Created by FlozAI"}}]}}],
        }

        resp = http_requests.post(f"{self.BASE_URL}/pages", headers=headers, json=body, timeout=15)
        if resp.status_code in (200, 201):
            return {"status": "created", "id": resp.json().get("id"), "title": title}
        raise ValueError(f"Notion API error ({resp.status_code}): {resp.text[:200]}")

    def _add_to_database(self, headers: dict, params: dict, context: dict) -> dict:
        database_id = params.get("database_id", "")
        if not database_id:
            raise ValueError("No database_id specified.")

        properties = params.get("properties", {})
        if not properties:
            properties = {"Name": {"title": [{"text": {"content": "FlozAI Entry"}}]}}

        body = {"parent": {"database_id": database_id}, "properties": properties}
        resp = http_requests.post(f"{self.BASE_URL}/pages", headers=headers, json=body, timeout=15)
        if resp.status_code in (200, 201):
            return {"status": "created", "id": resp.json().get("id")}
        raise ValueError(f"Notion API error ({resp.status_code}): {resp.text[:200]}")
