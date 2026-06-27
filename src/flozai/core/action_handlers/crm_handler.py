"""
CRM Action Handler
Creates/updates records in Salesforce, HubSpot, or generic CRM via REST APIs.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class CRMHandler:
    """Handles CRM actions (create record, update record, search)."""
    
    def __init__(self, provider: str = "generic"):
        self.provider = provider
    
    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        if action in ("create_record", "add_lead", "create_contact"):
            return self._create_record(credentials, params, context)
        elif action in ("update_record", "update_contact"):
            return self._update_record(credentials, params, context)
        else:
            raise ValueError(f"Unknown CRM action: {action}")
    
    def _create_record(self, credentials: dict, params: dict, context: dict) -> dict:
        if self.provider == "salesforce":
            return self._salesforce_create(credentials, params, context)
        elif self.provider == "hubspot":
            return self._hubspot_create(credentials, params, context)
        else:
            return self._generic_create(credentials, params, context)
    
    def _salesforce_create(self, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token")
        instance_url = credentials.get("instance_url", "https://login.salesforce.com")
        
        if not access_token:
            raise ValueError("Salesforce OAuth token not found. Please re-authorize.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            sobject = params.get("object_type", "Lead")
            return {"status": "created", "id": "mock-salesforce-id", "object": sobject, "simulated": True}

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        # Default to Lead object
        sobject = params.get("object_type", "Lead")
        data = params.get("data", {})
        
        # Pull from context if no explicit data
        if not data:
            data = {"LastName": "FlozAI Lead", "Company": "Unknown"}
            for key, val in context.items():
                if isinstance(val, dict):
                    if val.get("email"):
                        data["Email"] = val["email"]
                    if val.get("name"):
                        data["LastName"] = val["name"]
        
        resp = http_requests.post(
            f"{instance_url}/services/data/v58.0/sobjects/{sobject}",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if resp.status_code == 201:
            return {"status": "created", "id": resp.json().get("id"), "object": sobject}
        else:
            raise ValueError(f"Salesforce API error ({resp.status_code}): {resp.text[:200]}")
    
    def _hubspot_create(self, credentials: dict, params: dict, context: dict) -> dict:
        access_token = credentials.get("access_token") or credentials.get("apiKey")
        
        if not access_token:
            raise ValueError("HubSpot credentials not found. Please connect HubSpot.")
        
        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(access_token):
            return {"status": "created", "id": "mock-hubspot-id", "object": "contacts", "simulated": True}

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        
        properties = params.get("data", {})
        if not properties:
            properties = {"email": "lead@example.com", "firstname": "FlozAI", "lastname": "Lead"}
            for key, val in context.items():
                if isinstance(val, dict):
                    if val.get("email"):
                        properties["email"] = val["email"]
        
        resp = http_requests.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            headers=headers,
            json={"properties": properties},
            timeout=15
        )
        
        if resp.status_code == 201:
            return {"status": "created", "id": resp.json().get("id"), "object": "contacts"}
        else:
            raise ValueError(f"HubSpot API error ({resp.status_code}): {resp.text[:200]}")
    
    def _generic_create(self, credentials: dict, params: dict, context: dict) -> dict:
        """Fallback for generic CRM — logs the create action."""
        return {
            "status": "simulated",
            "message": "Generic CRM record creation simulated. Configure a specific CRM (Salesforce/HubSpot) for real API calls.",
            "data": params.get("data", {})
        }
    
    def _update_record(self, credentials: dict, params: dict, context: dict) -> dict:
        return {
            "status": "simulated",
            "message": "Record update simulated. Provide record ID and fields to update.",
            "data": params
        }
