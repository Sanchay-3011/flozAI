"""
Integration Registry — Single Source of Truth
Defines all 15 core integrations with their triggers, actions, auth type, and handler mapping.
"""

INTEGRATIONS = {
    # ── Communication ─────────────────────────────────────────────────
    "gmail": {
        "id": "gmail",
        "name": "Gmail",
        "category": "communication",
        "authType": "oauth",
        "triggers": ["new_email"],
        "actions": ["send_email", "read_emails"],
        "handler": "gmail_handler.GmailHandler",
        "description": "Send and receive emails via Gmail.",
        "setup_instructions": {
            "steps": [
                "Go to Google Cloud Console → APIs & Services → Credentials",
                "Create an OAuth 2.0 Client ID (Web application)",
                "Add http://localhost:8000/oauth/callback as an authorized redirect URI",
                "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file"
            ],
            "url": "https://console.cloud.google.com/apis/credentials"
        }
    },
    "slack": {
        "id": "slack",
        "name": "Slack",
        "category": "communication",
        "authType": "oauth",
        "triggers": ["new_message"],
        "actions": ["send_message", "post_message"],
        "handler": "slack_handler.SlackHandler",
        "description": "Send messages and notifications to Slack channels.",
        "setup_instructions": {
            "steps": [
                "Go to api.slack.com/apps and create a new app",
                "Under OAuth & Permissions, add chat:write and channels:read scopes",
                "Install the app to your workspace",
                "Set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET in your .env file"
            ],
            "url": "https://api.slack.com/apps"
        }
    },
    "whatsapp": {
        "id": "whatsapp",
        "name": "WhatsApp",
        "category": "communication",
        "authType": "apikey",
        "triggers": ["new_message"],
        "actions": ["send_message"],
        "handler": "whatsapp_handler.WhatsAppHandler",
        "description": "Send messages via WhatsApp Business Cloud API.",
        "setup_instructions": {
            "steps": [
                "Go to Meta for Developers → WhatsApp → Getting Started",
                "Create a business app and get your access token",
                "Copy your WhatsApp Business API Token"
            ],
            "url": "https://developers.facebook.com/apps/"
        }
    },
    "linkedin": {
        "id": "linkedin",
        "name": "LinkedIn",
        "category": "communication",
        "authType": "oauth",
        "triggers": [],
        "actions": ["create_post"],
        "handler": "linkedin_handler.LinkedInHandler",
        "description": "Publish posts to your LinkedIn profile.",
        "setup_instructions": {
            "steps": [
                "Go to LinkedIn Developer Portal → My Apps",
                "Create an app and request the w_member_social scope",
                "Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in your .env file"
            ],
            "url": "https://www.linkedin.com/developers/apps"
        }
    },

    # ── CRM ────────────────────────────────────────────────────────────
    "hubspot": {
        "id": "hubspot",
        "name": "HubSpot",
        "category": "crm",
        "authType": "oauth",
        "triggers": ["new_record", "new_lead"],
        "actions": ["create_record", "update_record"],
        "handler": "crm_handler.CRMHandler",
        "handlerArgs": {"provider": "hubspot"},
        "description": "Manage contacts, leads, and deals in HubSpot CRM.",
        "setup_instructions": {
            "steps": [
                "Go to HubSpot Developer → Create an app",
                "Under Auth, add CRM scopes (contacts write/read)",
                "Set HUBSPOT_CLIENT_ID and HUBSPOT_CLIENT_SECRET in your .env file"
            ],
            "url": "https://developers.hubspot.com/"
        }
    },
    "salesforce": {
        "id": "salesforce",
        "name": "Salesforce",
        "category": "crm",
        "authType": "oauth",
        "triggers": ["new_record", "new_lead"],
        "actions": ["create_record", "update_record"],
        "handler": "crm_handler.CRMHandler",
        "handlerArgs": {"provider": "salesforce"},
        "description": "Manage enterprise CRM records in Salesforce.",
        "setup_instructions": {
            "steps": [
                "Go to Salesforce Setup → App Manager → New Connected App",
                "Enable OAuth and add API + refresh_token scopes",
                "Set SALESFORCE_CLIENT_ID and SALESFORCE_CLIENT_SECRET in your .env file"
            ],
            "url": "https://login.salesforce.com/"
        }
    },

    # ── Data & Storage ─────────────────────────────────────────────────
    "google_sheets": {
        "id": "google_sheets",
        "name": "Google Sheets",
        "category": "data",
        "authType": "oauth",
        "triggers": ["new_record"],
        "actions": ["add_row", "read_range"],
        "handler": "google_sheets_handler.GoogleSheetsHandler",
        "description": "Read and write rows in Google Sheets.",
        "setup_instructions": {
            "steps": [
                "Uses the same Google OAuth as Gmail",
                "Enable the Google Sheets API in your Cloud Console",
                "Your existing GOOGLE_CLIENT_ID/SECRET will work"
            ],
            "url": "https://console.cloud.google.com/apis/library/sheets.googleapis.com"
        }
    },
    "notion": {
        "id": "notion",
        "name": "Notion",
        "category": "data",
        "authType": "apikey",
        "triggers": ["new_record"],
        "actions": ["create_page", "add_to_database"],
        "handler": "notion_handler.NotionHandler",
        "description": "Create pages and database entries in Notion.",
        "setup_instructions": {
            "steps": [
                "Go to notion.so/my-integrations",
                "Create a new internal integration",
                "Copy the Internal Integration Secret"
            ],
            "url": "https://www.notion.so/my-integrations"
        }
    },
    "airtable": {
        "id": "airtable",
        "name": "Airtable",
        "category": "data",
        "authType": "apikey",
        "triggers": ["new_record"],
        "actions": ["create_record", "list_records"],
        "handler": "airtable_handler.AirtableHandler",
        "description": "Create and read records in Airtable bases.",
        "setup_instructions": {
            "steps": [
                "Go to airtable.com/account → API section",
                "Generate a Personal Access Token with data.records:write scope",
                "Copy the token"
            ],
            "url": "https://airtable.com/create/tokens"
        }
    },

    # ── AI ──────────────────────────────────────────────────────────────
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "category": "ai",
        "authType": "apikey",
        "triggers": [],
        "actions": ["generate_content", "ai_summarize", "ai_analyze"],
        "handler": "openai_handler.OpenAIHandler",
        "description": "Generate AI content via OpenAI GPT models.",
        "setup_instructions": {
            "steps": [
                "Go to platform.openai.com → API Keys",
                "Create a new secret key",
                "Copy it and paste it here"
            ],
            "url": "https://platform.openai.com/api-keys"
        }
    },
    "perplexity": {
        "id": "perplexity",
        "name": "Perplexity",
        "category": "ai",
        "authType": "apikey",
        "triggers": [],
        "actions": ["web_search", "ai_search"],
        "handler": "perplexity_handler.PerplexityHandler",
        "description": "Search the web and get AI-summarized answers.",
        "setup_instructions": {
            "steps": [
                "Go to perplexity.ai → Settings → API",
                "Generate an API key",
                "Copy it and paste it here"
            ],
            "url": "https://www.perplexity.ai/settings/api"
        }
    },

    # ── Payments ────────────────────────────────────────────────────────
    "stripe": {
        "id": "stripe",
        "name": "Stripe",
        "category": "payments",
        "authType": "apikey",
        "triggers": ["payment_received", "invoice_paid"],
        "actions": ["log_event", "create_invoice"],
        "handler": "stripe_handler.StripeHandler",
        "description": "Handle payments, invoices, and subscription events.",
        "setup_instructions": {
            "steps": [
                "Go to dashboard.stripe.com → Developers → API Keys",
                "Copy your Secret Key (starts with sk_)",
                "Paste it here"
            ],
            "url": "https://dashboard.stripe.com/apikeys"
        }
    },

    # ── Scheduling ──────────────────────────────────────────────────────
    "scheduler": {
        "id": "scheduler",
        "name": "Scheduler",
        "category": "scheduling",
        "authType": "none",
        "triggers": ["scheduled_time", "recurring"],
        "actions": [],
        "handler": "scheduler_handler.SchedulerHandler",
        "description": "Built-in time-based trigger. No external setup needed.",
        "setup_instructions": None
    },
    "google_calendar": {
        "id": "google_calendar",
        "name": "Google Calendar",
        "category": "scheduling",
        "authType": "oauth",
        "triggers": ["calendar_event", "new_event"],
        "actions": ["create_event", "list_events"],
        "handler": "google_calendar_handler.GoogleCalendarHandler",
        "description": "Create and monitor Google Calendar events.",
        "setup_instructions": {
            "steps": [
                "Uses the same Google OAuth as Gmail",
                "Enable the Google Calendar API in your Cloud Console",
                "Your existing GOOGLE_CLIENT_ID/SECRET will work"
            ],
            "url": "https://console.cloud.google.com/apis/library/calendar-json.googleapis.com"
        }
    },

    # ── Webhook ─────────────────────────────────────────────────────────
    "webhook": {
        "id": "webhook",
        "name": "Webhook",
        "category": "utility",
        "authType": "none",
        "triggers": ["webhook_received", "form_submission"],
        "actions": ["send_webhook", "http_request"],
        "handler": "webhook_handler.WebhookHandler",
        "description": "Send and receive HTTP webhooks. No setup needed.",
        "setup_instructions": None
    },
    "weather": {
        "id": "weather",
        "name": "Weather",
        "category": "utility",
        "authType": "none",
        "triggers": [],
        "actions": ["get_weather"],
        "handler": "weather_handler.WeatherHandler",
        "description": "Get current weather for any location. No setup needed.",
        "setup_instructions": None
    },
}


def get_integration(integration_id: str) -> dict:
    """Get a single integration definition by ID."""
    return INTEGRATIONS.get(integration_id.lower())


def get_all_integrations() -> list:
    """Get all integration definitions as a list."""
    return list(INTEGRATIONS.values())


def get_integrations_by_auth(auth_type: str) -> list:
    """Get integrations filtered by auth type (oauth / apikey / none)."""
    return [i for i in INTEGRATIONS.values() if i["authType"] == auth_type]


def get_integrations_by_category(category: str) -> list:
    """Get integrations filtered by category."""
    return [i for i in INTEGRATIONS.values() if i["category"] == category]
