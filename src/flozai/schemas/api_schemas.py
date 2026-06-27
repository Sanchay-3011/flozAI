"""
API Request/Response Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .intent_schema import ParsedIntent
from .workflow_schema import WorkflowDefinition


class ParseIntentRequest(BaseModel):
    """Request to parse user intent"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_input": "When a new row is added to my spreadsheet, send a Slack message"
            }
        }
    )

    user_input: str = Field(..., description="Natural language workflow description")
    user_id: Optional[str] = Field(None, description="Optional user ID for context")


class ParseIntentResponse(BaseModel):
    """Response from intent parsing"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "intent": {
                    "status": "clear",
                    "original_text": "When a new row is added to my spreadsheet, send a Slack message",
                    "detected_language": "en"
                },
                "workflow": {
                    "name": "Spreadsheet to Slack",
                    "description": "Send Slack notification when new row is added",
                    "trigger": {
                        "type": "new_record",
                        "integration": "google_sheets",
                        "params": {"table_name": "Sheet1"}
                    },
                    "actions": [
                        {
                            "type": "send_slack",
                            "integration": "slack",
                            "params": {
                                "channel": "#general",
                                "message": "New row added to spreadsheet"
                            }
                        }
                    ]
                },
                "explanation": "I'll send a Slack message to #general whenever a new row is added to your spreadsheet."
            }
        }
    )

    intent: ParsedIntent
    workflow: Optional[WorkflowDefinition] = None  # Only if status is CLEAR
    explanation: str = Field(..., description="Plain-English explanation in user's language")
    missing_integrations: Optional[List[dict]] = Field(default_factory=list, description="List of missing integrations for the workflow")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    details: Optional[str] = None