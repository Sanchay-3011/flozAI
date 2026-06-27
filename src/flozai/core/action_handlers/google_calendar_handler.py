"""
Google Calendar Handler — Create and list events via Calendar API v3.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class GoogleCalendarHandler:
    BASE_URL = "https://www.googleapis.com/calendar/v3"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("Google Calendar OAuth token not found. Please re-authorize.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            if action in ("create_event",):
                summary = params.get("summary", params.get("title", "FlozAI Event"))
                return {"status": "created", "event_id": "mock-event-id", "link": "https://calendar.google.com/calendar/event?eid=mock", "simulated": True}
            elif action in ("list_events",):
                return {
                    "status": "success",
                    "count": 2,
                    "events": [
                        {"id": "mock-evt-1", "summary": "Mock Event 1", "start": "2026-06-17T10:00:00Z"},
                        {"id": "mock-evt-2", "summary": "Mock Event 2", "start": "2026-06-18T12:00:00Z"}
                    ],
                    "simulated": True
                }

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        if action in ("create_event",):
            return self._create_event(headers, params, context)
        elif action in ("list_events",):
            return self._list_events(headers, params)
        raise ValueError(f"Unknown Calendar action: {action}")

    def _create_event(self, headers: dict, params: dict, context: dict) -> dict:
        calendar_id = params.get("calendar_id", "primary")
        summary = params.get("summary", params.get("title", "FlozAI Event"))
        start = params.get("start", "")
        end = params.get("end", "")
        description = params.get("description", "")

        if not start or not end:
            raise ValueError("Both 'start' and 'end' datetime strings are required (ISO 8601).")

        body = {
            "summary": summary,
            "description": description or "Created by FlozAI",
            "start": {"dateTime": start, "timeZone": params.get("timezone", "UTC")},
            "end": {"dateTime": end, "timeZone": params.get("timezone", "UTC")},
        }

        resp = http_requests.post(f"{self.BASE_URL}/calendars/{calendar_id}/events", headers=headers, json=body, timeout=15)
        if resp.status_code == 200:
            return {"status": "created", "event_id": resp.json().get("id"), "link": resp.json().get("htmlLink")}
        raise ValueError(f"Calendar API error ({resp.status_code}): {resp.text[:200]}")

    def _list_events(self, headers: dict, params: dict) -> dict:
        calendar_id = params.get("calendar_id", "primary")
        max_results = params.get("max_results", 10)

        resp = http_requests.get(
            f"{self.BASE_URL}/calendars/{calendar_id}/events?maxResults={max_results}&orderBy=startTime&singleEvents=true",
            headers=headers,
            timeout=15,
        )
        if resp.status_code == 200:
            events = resp.json().get("items", [])
            return {
                "status": "success",
                "count": len(events),
                "events": [{"id": e.get("id"), "summary": e.get("summary"), "start": e.get("start", {}).get("dateTime")} for e in events],
            }
        raise ValueError(f"Calendar API error ({resp.status_code}): {resp.text[:200]}")
