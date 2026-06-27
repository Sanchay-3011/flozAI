"""
Airtable Handler — Create and read records via Airtable API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class AirtableHandler:
    BASE_URL = "https://api.airtable.com/v0"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        api_key = credentials.get("apiKey") or credentials.get("access_token")
        if not api_key:
            raise ValueError("Airtable API key not found. Please add your Personal Access Token.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(api_key):
            if action in ("create_record", "add_record"):
                return {"status": "created", "id": "recMockRecord123", "simulated": True}
            elif action in ("list_records", "read_records"):
                return {
                    "status": "success",
                    "count": 2,
                    "records": [
                        {"Name": "Mock Record 1", "Status": "Done"},
                        {"Name": "Mock Record 2", "Status": "In Progress"}
                    ],
                    "simulated": True
                }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        if action in ("create_record", "add_record"):
            return self._create_record(headers, params, context)
        elif action in ("list_records", "read_records"):
            return self._list_records(headers, params)
        raise ValueError(f"Unknown Airtable action: {action}")

    def _create_record(self, headers: dict, params: dict, context: dict) -> dict:
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", params.get("table", ""))
        fields = params.get("fields", params.get("data", {}))

        if not base_id or not table_name:
            raise ValueError("Both base_id and table_name are required.")

        if not fields and context:
            fields = {}
            for key, val in context.items():
                if isinstance(val, dict):
                    for k, v in val.items():
                        fields[k] = str(v) if not isinstance(v, str) else v

        resp = http_requests.post(
            f"{self.BASE_URL}/{base_id}/{table_name}",
            headers=headers,
            json={"records": [{"fields": fields}]},
            timeout=15,
        )
        if resp.status_code == 200:
            records = resp.json().get("records", [])
            return {"status": "created", "id": records[0]["id"] if records else None}
        raise ValueError(f"Airtable API error ({resp.status_code}): {resp.text[:200]}")

    def _list_records(self, headers: dict, params: dict) -> dict:
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", params.get("table", ""))
        if not base_id or not table_name:
            raise ValueError("Both base_id and table_name are required.")

        resp = http_requests.get(f"{self.BASE_URL}/{base_id}/{table_name}?maxRecords=10", headers=headers, timeout=15)
        if resp.status_code == 200:
            records = resp.json().get("records", [])
            return {"status": "success", "count": len(records), "records": [r.get("fields", {}) for r in records]}
        raise ValueError(f"Airtable API error ({resp.status_code}): {resp.text[:200]}")
