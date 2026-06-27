"""
Validator
Validates workflows against supported capabilities.
"""
from typing import List, Tuple, Optional
from flozai.schemas.workflow_schema import WorkflowDefinition
from flozai.schemas.capabilities import Capabilities, get_capabilities

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
    "send_notification":   "slack",
    "log_event":           "webhook",
    "check_availability":  "google_calendar",
    "create_appointment":  "google_calendar",
    "wait":                "scheduler",
}

ACTION_ALIASES = {
    "send_post": "create_post", "post_linkedin": "create_post",
    "post_twitter": "create_post", "post_instagram": "create_post",
    "publish_post": "create_post", "social_post": "create_post",
    "linkedin_post": "create_post", "tweet": "create_post",
    "email": "send_email", "send_message": "send_email",
    "slack_message": "send_slack", "notify_slack": "send_slack",
    "notify": "send_notification", "push_notification": "send_notification",
    "add_record": "create_record", "insert_record": "create_record",
    "add_task": "create_task", "new_task": "create_task",
    "enrich": "enrich_contact", "enrich_lead": "enrich_contact",
    "sync": "sync_record", "transfer": "sync_record",
    "generate": "generate_content", "ai_generate": "generate_content",
    "write_content": "generate_content", "fetch_news": "search_web",
    "search_news": "search_web", "get_news": "search_web",
    "add_row": "add_spreadsheet_row", "append_row": "add_spreadsheet_row",
    "log": "log_event",     "check_calendar":      "check_availability",
    "get_availability":    "check_availability",
    "find_slot":           "check_availability",
    "book_appointment":    "create_appointment",
    "schedule_meeting":    "create_appointment",
    "create_meeting":      "create_appointment",
    "book_meeting":        "create_appointment",
    "wait":                "wait",
    "delay":               "wait",
    "pause":               "wait",
}

TRIGGER_ALIASES = {
    "scheduled": "scheduled_time", "cron": "scheduled_time",
    "timer": "scheduled_time", "time_based": "scheduled_time",
    "daily": "scheduled_time", "weekly": "scheduled_time",
    "email_received": "new_email", "incoming_email": "new_email",
    "lead_created": "new_lead", "new_contact": "new_lead",
    "score_threshold": "lead_score_change",
    "payment_received": "new_payment", "payment_success": "new_payment",
    "charge_failed": "failed_payment", "payment_failed": "failed_payment",
    "ticket_created": "new_ticket", "support_ticket": "new_ticket",
    "spreadsheet_row": "new_row", "mention": "new_mention",
    "social_mention": "new_mention", "new_booking":        "form_submission",
"booking_created":    "form_submission",
"meeting_scheduled":  "form_submission",
"appointment_booked": "form_submission",
"calendly_booking":   "form_submission",
"new_appointment":    "form_submission",
}

INTEGRATION_ALIASES = {
    "linked_in": "linkedin", "linkedin_api": "linkedin",
    "twitter_x": "twitter", "x": "twitter",
    "google_mail": "gmail", "google_sheet": "google_sheets",
    "sheets": "google_sheets", "google_form": "google_forms",
    "forms": "google_forms", "hubspot_crm": "hubspot",
    "salesforce_crm": "salesforce", "sf": "salesforce",
    "qb": "quickbooks", "quick_books": "quickbooks",
    "whatsapp_business": "whatsapp", "gpt": "openai", "open_ai": "openai",
}

TEMPLATE_PARAMS = {
    "form_id", "table_name", "to", "phone_number", "channel",
    "message", "body", "record_id", "field_mappings", "sheet_id",
    "row_data", "sequence_id", "owner", "email", "content",
    "prompt", "query", "title", "source", "destination",
    "endpoint", "event_name", "properties", "assignee",
    "due_date", "description", "subject", "schedule",
    "url", "spreadsheet_id", "customer", "location", "duration", # new required params
    # User-specific values filled in at activation time
    "threshold", "amount_threshold", "lead_score_threshold",
    "filter_condition", "sheet_name", "keyword", "source",
    "priority_filter", "from_filter", "subject_filter",
    "image_url", "schedule_time", "tone", "length",
    "round_robin", "event_name",
}


def _clean_integration(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = raw.lower().strip()
    if key in NULL_VALUES:
        return None
    if key in INTEGRATION_ALIASES:
        return INTEGRATION_ALIASES[key]
    return key


def _clean_type(raw: Optional[str], aliases: dict) -> Optional[str]:
    if not raw:
        return raw
    key = raw.lower().strip()
    return aliases.get(key, key)


class WorkflowValidator:

    def __init__(self, capabilities: Capabilities = None):
        self.capabilities = capabilities or get_capabilities()

    def validate(self, workflow: WorkflowDefinition) -> Tuple[bool, List[str]]:
        self.capabilities = get_capabilities()
        self._normalize(workflow)

        errors = []
        errors.extend(self._validate_triggers(workflow))
        errors.extend(self._validate_actions(workflow))

        if not workflow.validate_linear_structure():
            errors.append("Workflow must have at least one trigger and one action")

        return (len(errors) == 0, errors)

    def _normalize(self, workflow: WorkflowDefinition):
        # Normalize all triggers
        for t in workflow.triggers:
            t.type        = _clean_type(t.type, TRIGGER_ALIASES)
            t.integration = _clean_integration(t.integration)
            if not t.integration:
                t.integration = TRIGGER_DEFAULTS.get(t.type)

        # Normalize all actions
        for action in workflow.actions:
            action.type        = _clean_type(action.type, ACTION_ALIASES)
            action.integration = _clean_integration(action.integration)
            if not action.integration:
                action.integration = ACTION_DEFAULTS.get(action.type)

    def _validate_triggers(self, workflow: WorkflowDefinition) -> List[str]:
        errors = []

        for idx, t in enumerate(workflow.triggers):
            label = f"Trigger {idx + 1}" if len(workflow.triggers) > 1 else "Trigger"

            trigger_def = self.capabilities.get_trigger(t.type)
            if not trigger_def:
                errors.append(f"{label}: Unsupported trigger type '{t.type}'")
                continue

            if t.integration:
                if not self.capabilities.get_integration(t.integration):
                    errors.append(f"{label}: Unsupported integration '{t.integration}'")
                    continue
                if not self.capabilities.validate_trigger_integration(t.type, t.integration):
                    errors.append(
                        f"{label}: '{t.integration}' does not support trigger '{t.type}'"
                    )

            required = {p.name for p in trigger_def.required_params}
            critical_missing = (required - set(t.params.keys())) - TEMPLATE_PARAMS
            if critical_missing:
                errors.append(f"{label}: missing params: {', '.join(critical_missing)}")

        return errors

    def _validate_actions(self, workflow: WorkflowDefinition) -> List[str]:
        errors = []

        for i, action in enumerate(workflow.actions, 1):
            action_def = self.capabilities.get_action(action.type)
            if not action_def:
                errors.append(f"Action {i}: Unsupported action type '{action.type}'")
                continue

            if action.integration:
                if not self.capabilities.get_integration(action.integration):
                    errors.append(f"Action {i}: Unsupported integration '{action.integration}'")
                    continue
                if not self.capabilities.validate_action_integration(action.type, action.integration):
                    errors.append(
                        f"Action {i}: '{action.integration}' does not support '{action.type}'"
                    )

            required = {p.name for p in action_def.required_params}
            critical_missing = (required - set(action.params.keys())) - TEMPLATE_PARAMS
            if critical_missing:
                errors.append(f"Action {i}: missing params: {', '.join(critical_missing)}")

        return errors