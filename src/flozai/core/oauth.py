"""
OAuth Integration Framework
Handles OAuth2 authorization flows for Gmail, Slack, Salesforce, etc.
"""
import os
import uuid
import json
import requests as http_requests
from typing import Dict, Optional
from pathlib import Path
from urllib.parse import urlencode
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

# ── OAuth Provider Configurations ──────────────────────────────────────

OAUTH_PROVIDERS = {
    "gmail": {
        "name": "Gmail",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"],
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
    },
    "google_forms": {
        "name": "Google Forms",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/forms.responses.readonly"],
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
    },
    "google_sheets": {
        "name": "Google Sheets",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/spreadsheets"],
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
    },
    "slack": {
        "name": "Slack",
        "auth_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "scopes": ["chat:write", "channels:read"],
        "env_client_id": "SLACK_CLIENT_ID",
        "env_client_secret": "SLACK_CLIENT_SECRET",
    },
    "salesforce": {
        "name": "Salesforce",
        "auth_url": "https://login.salesforce.com/services/oauth2/authorize",
        "token_url": "https://login.salesforce.com/services/oauth2/token",
        "scopes": ["api", "refresh_token"],
        "env_client_id": "SALESFORCE_CLIENT_ID",
        "env_client_secret": "SALESFORCE_CLIENT_SECRET",
    },
    "hubspot": {
        "name": "HubSpot",
        "auth_url": "https://app.hubspot.com/oauth/authorize",
        "token_url": "https://api.hubapi.com/oauth/v1/token",
        "scopes": ["crm.objects.contacts.write", "crm.objects.contacts.read"],
        "env_client_id": "HUBSPOT_CLIENT_ID",
        "env_client_secret": "HUBSPOT_CLIENT_SECRET",
    },
    "linkedin": {
        "name": "LinkedIn",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": ["openid", "profile", "w_member_social"],
        "env_client_id": "LINKEDIN_CLIENT_ID",
        "env_client_secret": "LINKEDIN_CLIENT_SECRET",
    },
    "google_calendar": {
        "name": "Google Calendar",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"],
        "env_client_id": "GOOGLE_CLIENT_ID",
        "env_client_secret": "GOOGLE_CLIENT_SECRET",
    },
}

REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/oauth/callback")


def get_supported_oauth_providers():
    """Returns a list of provider IDs that have OAuth credentials configured."""
    available = []
    for provider_id, config in OAUTH_PROVIDERS.items():
        client_id = os.getenv(config["env_client_id"])
        if client_id:
            available.append(provider_id)
    return available


def get_authorization_url(provider: str, user_id: str = "default_user") -> Dict:
    """
    Generates the OAuth authorization URL for a given provider.
    Returns { url, state } or raises ValueError.
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unknown OAuth provider: {provider}")
    
    config = OAUTH_PROVIDERS[provider]
    client_id = os.getenv(config["env_client_id"])
    
    if not client_id:
        raise ValueError(
            f"OAuth not configured for {config['name']}. "
            f"Set {config['env_client_id']} and {config['env_client_secret']} in your .env file."
        )
    
    state_hash = uuid.uuid4().hex
    state = f"{provider}:{user_id}:{state_hash}"
    
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "state": state,
        "access_type": "offline",
        "prompt": "consent",
    }
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    
    return {"url": auth_url, "state": state, "provider": provider}


def exchange_code_for_token(provider: str, code: str) -> Dict:
    """
    Exchanges an authorization code for access + refresh tokens.
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unknown OAuth provider: {provider}")
    
    config = OAUTH_PROVIDERS[provider]
    client_id = os.getenv(config["env_client_id"])
    client_secret = os.getenv(config["env_client_secret"])
    
    if not client_id or not client_secret:
        raise ValueError(f"OAuth credentials not configured for {config['name']}")
    
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    
    response = http_requests.post(config["token_url"], data=data, timeout=15)
    
    if response.status_code != 200:
        logger.error(f"Token exchange failed for {provider}: {response.text}")
        raise ValueError(f"Failed to exchange code: {response.text[:200]}")
    
    token_data = response.json()
    
    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type", "Bearer"),
        "scope": token_data.get("scope", ""),
    }


def refresh_access_token(provider: str, refresh_token: str) -> Dict:
    """
    Refreshes an expired access token using the refresh token.
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unknown OAuth provider: {provider}")
    
    config = OAUTH_PROVIDERS[provider]
    client_id = os.getenv(config["env_client_id"])
    client_secret = os.getenv(config["env_client_secret"])
    
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    
    response = http_requests.post(config["token_url"], data=data, timeout=15)
    
    if response.status_code != 200:
        raise ValueError(f"Token refresh failed: {response.text[:200]}")
    
    token_data = response.json()
    return {
        "access_token": token_data.get("access_token"),
        "expires_in": token_data.get("expires_in"),
    }
