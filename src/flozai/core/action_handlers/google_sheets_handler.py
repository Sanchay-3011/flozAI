"""
Google Sheets Handler — Add rows and read ranges via Sheets API v4.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleSheetsHandler:
    BASE_URL = "https://sheets.googleapis.com/v4/spreadsheets"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("Google Sheets OAuth token not found. Please re-authorize.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            if action in ("add_row", "append_row"):
                spreadsheet_id = params.get("spreadsheet_id", "mock-sheet-id")
                sheet_range = params.get("range", "Sheet1!A1")
                return {"status": "appended", "updated_range": f"{sheet_range}:Z{len(params.get('values', [])) + 1}", "simulated": True}
            elif action in ("read_range",):
                return {
                    "status": "success",
                    "rows": [
                        ["Header 1", "Header 2", "Header 3"],
                        ["Mock Data 1", "Mock Data 2", "Mock Data 3"]
                    ],
                    "count": 2,
                    "simulated": True
                }

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        if action in ("add_row", "append_row"):
            return self._add_row(headers, params, context)
        elif action in ("read_range",):
            return self._read_range(headers, params)
        else:
            raise ValueError(f"Unknown Sheets action: {action}")

    def _add_row(self, headers: dict, params: dict, context: dict) -> dict:
        spreadsheet_id = params.get("spreadsheet_id", "")
        sheet_range = params.get("range", "Sheet1!A1")
        values = params.get("values", [])

        if not values and context:
            row = []
            for key, val in context.items():
                if isinstance(val, dict):
                    row.extend(str(v) for v in val.values())
                else:
                    row.append(str(val))
            values = [row]

        if not spreadsheet_id:
            raise ValueError("No spreadsheet_id specified.")

        resp = http_requests.post(
            f"{self.BASE_URL}/{spreadsheet_id}/values/{sheet_range}:append?valueInputOption=USER_ENTERED",
            headers=headers,
            json={"values": values},
            timeout=15,
        )
        if resp.status_code == 200:
            return {"status": "appended", "updated_range": resp.json().get("updates", {}).get("updatedRange")}
        raise ValueError(f"Sheets API error ({resp.status_code}): {resp.text[:200]}")

    def _read_range(self, headers: dict, params: dict) -> dict:
        spreadsheet_id = params.get("spreadsheet_id", "")
        sheet_range = params.get("range", "Sheet1!A1:Z100")
        if not spreadsheet_id:
            raise ValueError("No spreadsheet_id specified.")

        resp = http_requests.get(
            f"{self.BASE_URL}/{spreadsheet_id}/values/{sheet_range}",
            headers=headers,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {"status": "success", "rows": data.get("values", []), "count": len(data.get("values", []))}
        raise ValueError(f"Sheets API error ({resp.status_code}): {resp.text[:200]}")
