"""
Intent Schema
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum

NULL_VALUES = {"none", "null", "n/a", "unknown", "undefined", "na", "nil", ""}


class IntentStatus(str, Enum):
    CLEAR = "clear"
    NEEDS_CLARIFICATION = "needs_clarification"
    OUT_OF_SCOPE = "out_of_scope"
    INVALID = "invalid"


class ExtractedTrigger(BaseModel):
    type: Optional[str] = None
    integration: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)

    @field_validator("integration", mode="before")
    @classmethod
    def clean_integration(cls, v):
        if v is None:
            return None
        if str(v).lower().strip() in NULL_VALUES:
            return None
        return v

    @field_validator("params", mode="before")
    @classmethod
    def ensure_dict(cls, v):
        return v if isinstance(v, dict) else {}


class ExtractedAction(BaseModel):
    type: Optional[str] = None
    integration: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)

    @field_validator("integration", mode="before")
    @classmethod
    def clean_integration(cls, v):
        if v is None:
            return None
        if str(v).lower().strip() in NULL_VALUES:
            return None
        return v

    @field_validator("params", mode="before")
    @classmethod
    def ensure_dict(cls, v):
        return v if isinstance(v, dict) else {}


class ParsedIntent(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "clear",
                "original_text": "When a HubSpot lead is created or a Typeform is submitted, notify Slack",
                "detected_language": "en",
                "workflow_name": "Multi-Trigger Lead Notification",
                "workflow_description": "Notify Slack when leads come in from multiple sources",
                "triggers": [
                    {
                        "type": "new_lead",
                        "integration": "hubspot",
                        "params": {},
                        "confidence": 0.95
                    },
                    {
                        "type": "form_submission",
                        "integration": "typeform",
                        "params": {},
                        "confidence": 0.95
                    }
                ],
                "actions": [
                    {
                        "type": "send_slack",
                        "integration": "slack",
                        "params": {},
                        "confidence": 0.95
                    }
                ]
            }
        }
    )

    status: IntentStatus
    original_text: str = Field(..., description="Original user input")
    detected_language: str = Field(default="en")

    workflow_name: Optional[str] = None
    workflow_description: Optional[str] = None

    # Multi-trigger support — always a list now
    triggers: List[ExtractedTrigger] = Field(default_factory=list)

    # Keep single trigger as alias for backwards compatibility
    trigger: Optional[ExtractedTrigger] = None

    actions: List[ExtractedAction] = Field(default_factory=list)

    clarification_question: Optional[str] = None
    missing_info: List[str] = Field(default_factory=list)

    out_of_scope_reason: Optional[str] = None
    suggested_alternative: Optional[str] = None

    def get_all_triggers(self) -> List[ExtractedTrigger]:
        """
        Returns unified trigger list.
        Handles both old single-trigger and new multi-trigger LLM responses.
        """
        if self.triggers:
            return self.triggers
        if self.trigger:
            return [self.trigger]
        return []