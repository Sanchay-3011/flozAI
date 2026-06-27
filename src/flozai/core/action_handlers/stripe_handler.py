"""
Stripe Handler — Payment events and invoices via Stripe API.
"""
import requests as http_requests
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class StripeHandler:
    BASE_URL = "https://api.stripe.com/v1"

    def execute(self, action: str, credentials: dict, params: dict, context: dict) -> dict:
        api_key = credentials.get("apiKey") or credentials.get("access_token")
        if not api_key:
            raise ValueError("Stripe API key not found. Please add your secret key.")

        from flozai.core.action_handlers import is_mock_key
        if is_mock_key(api_key):
            if action in ("log_event", "check_payment"):
                return {
                    "status": "success",
                    "count": 2,
                    "charges": [
                        {"id": "ch_mock1", "amount": 100.0, "currency": "usd", "status": "succeeded"},
                        {"id": "ch_mock2", "amount": 49.99, "currency": "usd", "status": "succeeded"}
                    ],
                    "simulated": True
                }
            elif action in ("create_invoice",):
                return {"status": "created", "invoice_id": "in_mockInvoice123", "simulated": True}

        if action in ("log_event", "check_payment"):
            return self._list_charges(api_key, params)
        elif action in ("create_invoice",):
            return self._create_invoice(api_key, params, context)
        raise ValueError(f"Unknown Stripe action: {action}")

    def _list_charges(self, api_key: str, params: dict) -> dict:
        limit = params.get("limit", 5)
        resp = http_requests.get(f"{self.BASE_URL}/charges?limit={limit}", auth=(api_key, ""), timeout=15)
        if resp.status_code == 200:
            charges = resp.json().get("data", [])
            return {
                "status": "success",
                "count": len(charges),
                "charges": [{"id": c["id"], "amount": c["amount"] / 100, "currency": c["currency"], "status": c["status"]} for c in charges],
            }
        raise ValueError(f"Stripe API error ({resp.status_code}): {resp.text[:200]}")

    def _create_invoice(self, api_key: str, params: dict, context: dict) -> dict:
        customer = params.get("customer", "")
        if not customer:
            raise ValueError("Customer ID is required to create an invoice.")

        resp = http_requests.post(
            f"{self.BASE_URL}/invoices",
            auth=(api_key, ""),
            data={"customer": customer, "auto_advance": "true"},
            timeout=15,
        )
        if resp.status_code == 200:
            return {"status": "created", "invoice_id": resp.json().get("id")}
        raise ValueError(f"Stripe API error ({resp.status_code}): {resp.text[:200]}")
