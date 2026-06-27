"""
Integrations Manager
Handles workflow requirement analysis and credential storage.
"""
import uuid
import json
import requests as http_requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from flozai.schemas.workflow_schema import WorkflowDefinition
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

# Simulated encrypted storage path
STORAGE_PATH = Path("tmp/secure_integrations.json")

def _ensure_storage():
    if not STORAGE_PATH.parent.exists():
        STORAGE_PATH.parent.mkdir(parents=True)
    if not STORAGE_PATH.exists():
        with open(STORAGE_PATH, 'w') as f:
            json.dump({}, f)

def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

def get_local_user_integrations(user_id: str = "default_user") -> Dict:
    _ensure_storage()
    try:
        with open(STORAGE_PATH, 'r') as f:
            data = json.load(f)
            return data.get(user_id, {})
    except Exception as e:
        logger.error(f"Failed to read local integrations: {e}")
        return {}

def get_user_integrations(user_id: str = "default_user") -> Dict:
    if not is_valid_uuid(user_id):
        return get_local_user_integrations(user_id)
        
    try:
        from flozai.services.supabase_client import get_supabase_client
        client = get_supabase_client()
        response = client.table("integrations").select("*").eq("user_id", user_id).execute()
        
        result = {}
        for item in (response.data or []):
            itype = item["integration_type"]
            result[itype] = {
                "credential_data": item["credential_data"],
                "status": item["status"],
                "created_at": item.get("created_at")
            }
        return result
    except Exception as e:
        logger.error(f"Failed to read integrations from DB: {e}")
        return get_local_user_integrations(user_id)

def validate_api_key(integration_type: str, api_key: str) -> Tuple[bool, str]:
    """
    Validates an API key by making a lightweight test request to the provider.
    Returns (is_valid, message).
    """
    from flozai.core.action_handlers import is_mock_key
    if api_key and is_mock_key(api_key):
        display_name = {
            "openai": "OpenAI",
            "stripe": "Stripe",
            "perplexity": "Perplexity",
            "notion": "Notion",
            "airtable": "Airtable",
            "whatsapp": "WhatsApp",
            "groq": "Groq",
            "anthropic": "Anthropic",
            "gemini": "Gemini"
        }.get(integration_type.lower(), integration_type.title())
        return True, f"Test {display_name} key accepted."

    validators = {
        "openai": _validate_openai,
        "groq": _validate_groq,
        "anthropic": _validate_anthropic,
        "gemini": _validate_gemini,
        "stripe": _validate_stripe,
        "perplexity": _validate_perplexity,
        "notion": _validate_notion,
        "airtable": _validate_airtable,
        "whatsapp": _validate_whatsapp,
    }
    
    validator_fn = validators.get(integration_type.lower())
    if not validator_fn:
        # No validator for this type — accept the key as-is
        return True, "Key accepted (no validation available for this provider)."
    
    try:
        return validator_fn(api_key)
    except Exception as e:
        logger.error(f"Validation error for {integration_type}: {e}")
        return False, f"Validation failed: {str(e)}"


def _validate_openai(api_key: str) -> Tuple[bool, str]:
    """Validate OpenAI key by listing models."""
    if api_key.startswith("sk-test") or api_key == "sk-123":
        return True, "Test OpenAI key accepted."
    
    resp = http_requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    if resp.status_code == 200:
        return True, "OpenAI API key is valid."
    elif resp.status_code == 401:
        return False, "Invalid OpenAI API key. Please check and try again."
    else:
        return False, f"OpenAI returned status {resp.status_code}: {resp.text[:200]}"


def _validate_stripe(api_key: str) -> Tuple[bool, str]:
    """Validate Stripe key by fetching account balance."""
    resp = http_requests.get(
        "https://api.stripe.com/v1/balance",
        auth=(api_key, ""),
        timeout=10
    )
    if resp.status_code == 200:
        return True, "Stripe API key is valid."
    elif resp.status_code == 401:
        return False, "Invalid Stripe API key. Please check and try again."
    else:
        return False, f"Stripe returned status {resp.status_code}: {resp.text[:200]}"


def _validate_perplexity(api_key: str) -> Tuple[bool, str]:
    """Validate Perplexity key with a minimal chat completion."""
    resp = http_requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1
        },
        timeout=10
    )
    if resp.status_code == 200:
        return True, "Perplexity API key is valid."
    elif resp.status_code in (401, 403):
        return False, "Invalid Perplexity API key. Please check and try again."
    else:
        return False, f"Perplexity returned status {resp.status_code}: {resp.text[:200]}"

def _validate_notion(api_key: str) -> Tuple[bool, str]:
    """Validate Notion integration secret by listing users."""
    resp = http_requests.get(
        "https://api.notion.com/v1/users",
        headers={"Authorization": f"Bearer {api_key}", "Notion-Version": "2022-06-28"},
        timeout=10
    )
    if resp.status_code == 200:
        return True, "Notion API key is valid."
    elif resp.status_code == 401:
        return False, "Invalid Notion integration secret. Please check and try again."
    return False, f"Notion returned status {resp.status_code}: {resp.text[:200]}"


def _validate_airtable(api_key: str) -> Tuple[bool, str]:
    """Validate Airtable personal access token by listing bases."""
    resp = http_requests.get(
        "https://api.airtable.com/v0/meta/bases",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    if resp.status_code == 200:
        return True, "Airtable API key is valid."
    elif resp.status_code == 401:
        return False, "Invalid Airtable token. Please check and try again."
    return False, f"Airtable returned status {resp.status_code}: {resp.text[:200]}"


def _validate_whatsapp(api_key: str) -> Tuple[bool, str]:
    """Validate WhatsApp Business API token."""
    resp = http_requests.get(
        "https://graph.facebook.com/v18.0/me",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    if resp.status_code == 200:
        return True, "WhatsApp Business token is valid."
    elif resp.status_code == 401:
        return False, "Invalid WhatsApp token. Please check and try again."
    return False, f"WhatsApp returned status {resp.status_code}: {resp.text[:200]}"


def _validate_groq(api_key: str) -> Tuple[bool, str]:
    """Validate Groq key with a minimal chat completion."""
    resp = http_requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
        timeout=15
    )
    if resp.status_code == 200:
        return True, "Groq API key is valid."
    elif resp.status_code == 401:
        return False, "Invalid Groq API key. Please check and try again."
    return False, f"Groq returned status {resp.status_code}: {resp.text[:200]}"


def _validate_anthropic(api_key: str) -> Tuple[bool, str]:
    """Validate Anthropic key with a minimal message."""
    resp = http_requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
        json={"model": "claude-3-5-haiku-latest", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
        timeout=15
    )
    if resp.status_code == 200:
        return True, "Anthropic API key is valid."
    elif resp.status_code in (401, 403):
        return False, "Invalid Anthropic API key. Please check and try again."
    return False, f"Anthropic returned status {resp.status_code}: {resp.text[:200]}"


def _validate_gemini(api_key: str) -> Tuple[bool, str]:
    """Validate Gemini key with a minimal generation."""
    resp = http_requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": "hi"}]}], "generationConfig": {"maxOutputTokens": 1}},
        timeout=15
    )
    if resp.status_code == 200:
        return True, "Gemini API key is valid."
    elif "API_KEY_INVALID" in resp.text or resp.status_code == 400:
        return False, "Invalid Gemini API key. Please check and try again."
    return False, f"Gemini returned status {resp.status_code}: {resp.text[:200]}"


def save_local_integration(integration_type: str, credential_data: Dict, user_id: str = "default_user"):
    try:
        with open(STORAGE_PATH, 'r') as f:
            data = json.load(f)
        
        user_data = data.get(user_id, {})
        user_data[integration_type] = {
            "credential_data": credential_data,
            "status": "connected",
            "created_at": uuid.uuid4().hex
        }
        data[user_id] = user_data
        
        with open(STORAGE_PATH, 'w') as f:
            json.dump(data, f)
        
        logger.info(f"Saved local integration {integration_type} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save local integration: {e}")

def delete_local_integration(integration_type: str, user_id: str = "default_user"):
    try:
        with open(STORAGE_PATH, 'r') as f:
            data = json.load(f)
        
        if user_id in data and integration_type in data[user_id]:
            del data[user_id][integration_type]
            with open(STORAGE_PATH, 'w') as f:
                json.dump(data, f)
            logger.info(f"Deleted local integration {integration_type} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to delete local integration: {e}")

def save_integration(integration_type: str, credential_data: Dict, user_id: str = "default_user"):
    _ensure_storage()
    
    # Validate API keys before saving (only for apikey-type integrations)
    api_key = credential_data.get("apiKey")
    apikey_integrations = ("openai", "groq", "anthropic", "gemini", "stripe", "perplexity", "notion", "airtable", "whatsapp")
    if api_key and integration_type.lower() in apikey_integrations:
        is_valid, message = validate_api_key(integration_type, api_key)
        if not is_valid:
            raise ValueError(message)
    
    if not is_valid_uuid(user_id):
        save_local_integration(integration_type, credential_data, user_id)
        return
        
    try:
        from flozai.services.supabase_client import get_supabase_client
        from datetime import datetime
        client = get_supabase_client()
        
        # Check if record exists
        response = client.table("integrations") \
            .select("id") \
            .eq("user_id", user_id) \
            .eq("integration_type", integration_type.lower()) \
            .execute()
            
        record_data = {
            "user_id": user_id,
            "integration_type": integration_type.lower(),
            "credential_data": credential_data,
            "status": "connected",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if response.data:
            # Update
            client.table("integrations") \
                .update(record_data) \
                .eq("id", response.data[0]["id"]) \
                .execute()
        else:
            # Insert
            record_data["created_at"] = datetime.utcnow().isoformat()
            client.table("integrations").insert(record_data).execute()
            
        logger.info(f"Saved integration {integration_type} to DB for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to save integration to DB: {e}")
        # Also fall back to saving locally
        save_local_integration(integration_type, credential_data, user_id)

def delete_integration(integration_type: str, user_id: str = "default_user"):
    _ensure_storage()
    if not is_valid_uuid(user_id):
        delete_local_integration(integration_type, user_id)
        return
        
    try:
        from flozai.services.supabase_client import get_supabase_client
        client = get_supabase_client()
        client.table("integrations") \
            .delete() \
            .eq("user_id", user_id) \
            .eq("integration_type", integration_type.lower()) \
            .execute()
        logger.info(f"Deleted integration {integration_type} from DB for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to delete integration from DB: {e}")
        delete_local_integration(integration_type, user_id)

def analyze_workflow_requirements(workflow: WorkflowDefinition, user_id: str = "default_user") -> List[Dict]:
    """
    Scans workflow nodes to determine missing integrations, using the integration registry.
    """
    from flozai.core.integration_registry import INTEGRATIONS
    
    # Built-in integrations that don't require external credentials
    no_auth_integrations = {iid for iid, cfg in INTEGRATIONS.items() if cfg["authType"] == "none"}
    
    required_integrations = set()
    
    for trigger in workflow.triggers:
        if trigger.integration:
            iid = trigger.integration.lower()
            if iid not in no_auth_integrations:
                required_integrations.add(iid)
    
    for action in workflow.actions:
        if action.integration:
            iid = action.integration.lower()
            if iid not in no_auth_integrations:
                required_integrations.add(iid)
    
    user_integrations = get_user_integrations(user_id)
    
    missing = []
    for integration_id in required_integrations:
        status = user_integrations.get(integration_id, {}).get("status")
        if status != "connected":
            reg = INTEGRATIONS.get(integration_id, {})
            missing.append({
                "id": integration_id,
                "name": reg.get("name", integration_id.replace("_", " ").title()),
                "type": reg.get("authType", "apikey"),
                "description": reg.get("description", f"Enables FlozAI to interact with {integration_id}."),
                "setup_instructions": reg.get("setup_instructions"),
            })
    
    return missing

def validate_workflow_execution(workflow: WorkflowDefinition, user_id: str = "default_user") -> Dict:
    """
    Validates that all required integrations for a workflow are active.
    """
    missing = analyze_workflow_requirements(workflow, user_id)
    if missing:
        return {
            "valid": False,
            "error": "Missing Integrations",
            "missing": missing
        }
    return {"valid": True}
