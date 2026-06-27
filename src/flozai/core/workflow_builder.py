"""
Workflow Builder
Converts ParsedIntent into WorkflowDefinition JSON
"""
from typing import Optional
from flozai.schemas.intent_schema import ParsedIntent, IntentStatus
from flozai.schemas.workflow_schema import (
    WorkflowDefinition,
    WorkflowTrigger,
    WorkflowAction
)

NULL_VALUES = {"none", "null", "n/a", "unknown", "undefined", "na", "nil", ""}

TRIGGER_DEFAULTS = {
    "scheduled_time":    "scheduler",
    "new_email":         "gmail",
    "form_submission":   "google_forms",
    "new_lead":          "hubspot",
    "lead_score_change": "hubspot",
    "new_payment":       "stripe",
    "failed_payment":    "stripe",
    "new_ticket":        "zendesk",
    "new_row":           "google_sheets",
    "new_record":        "crm",
    "new_mention":       "twitter",
    "webhook":           "webhook",
    "manual":            "scheduler",
}

ACTION_DEFAULTS = {
    "send_email":          "gmail",
    "send_slack":          "slack",
    "send_whatsapp":       "whatsapp",
    "create_post":         "linkedin",
    "create_record":       "crm",
    "update_record":       "crm",
    "create_task":         "asana",
    "enrich_contact":      "clearbit",
    "assign_owner":        "hubspot",
    "add_to_sequence":     "mailchimp",
    "sync_record":         "quickbooks",
    "generate_content":    "openai",
    "search_web":          "perplexity",
    "add_spreadsheet_row": "google_sheets",
    "add_row":             "google_sheets",
    "read_range":          "google_sheets",
    "send_notification":   "slack",
    "log_event":           "webhook",
    "send_webhook":        "webhook",
    "http_request":        "webhook",
    "wait":                "scheduler",
    "create_page":         "notion",
    "add_to_database":     "notion",
    "list_records":        "airtable",
    "create_invoice":      "stripe",
    "send_message":        "slack",
    "post_message":        "slack",
    "create_event":        "google_calendar",
    "list_events":         "google_calendar",
    "ai_summarize":        "openai",
    "ai_analyze":          "openai",
    "ai_search":           "perplexity",
}


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if str(value).lower().strip() in NULL_VALUES:
        return None
    return value


class WorkflowBuilder:

    def build(self, intent: ParsedIntent) -> Optional[WorkflowDefinition]:
        if intent.status != IntentStatus.CLEAR:
            return None

        # Get all triggers using unified method
        all_triggers = intent.get_all_triggers()

        if not all_triggers:
            raise ValueError("Cannot build workflow: missing triggers")
        if not intent.actions:
            raise ValueError("Cannot build workflow: missing actions")
        if not intent.workflow_name:
            raise ValueError("Cannot build workflow: missing workflow name")
        if not intent.workflow_description:
            raise ValueError("Cannot build workflow: missing workflow description")

        # Build all triggers
        triggers = []
        for t in all_triggers:
            trigger_type        = t.type or ""
            trigger_integration = _clean(t.integration)

            if not trigger_integration:
                trigger_integration = TRIGGER_DEFAULTS.get(trigger_type)

            triggers.append(WorkflowTrigger(
                type=trigger_type,
                integration=trigger_integration,
                params=t.params or {}
            ))

        # Build actions
        actions = []
        for a in intent.actions:
            action_type        = a.type or ""
            action_integration = _clean(a.integration)

            if not action_integration:
                action_integration = ACTION_DEFAULTS.get(action_type)

            actions.append(WorkflowAction(
                type=action_type,
                integration=action_integration,
                params=a.params or {}
            ))

        return WorkflowDefinition(
            name=intent.workflow_name,
            description=intent.workflow_description,
            triggers=triggers,
            actions=actions
        )