"""
Workflow Schema
"""
from typing import List, Dict, Any, Optional, ClassVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class WorkflowTrigger(BaseModel):
    type: str = Field(..., description="Trigger type ID")
    integration: Optional[str] = Field(None, description="Integration ID")
    params: Dict[str, Any] = Field(default_factory=dict)


class StepCondition(BaseModel):
    """Condition that must be met for a step to execute."""
    enabled: bool = Field(default=True, description="Whether condition checking is active")
    field: str = Field(..., description="Dot-notation field path, e.g. 'lead.status'")
    operator: str = Field(..., description="Comparison operator: equals, not_equals, contains, greater_than, exists, not_exists")
    value: Optional[str] = Field(None, description="Comparison value (not needed for exists/not_exists)")
    natural_language: str = Field(default="", description="Human-readable summary of the condition")

    VALID_OPERATORS: ClassVar[set] = {"equals", "not_equals", "contains", "greater_than", "exists", "not_exists"}

    def is_valid(self) -> bool:
        return self.operator in self.VALID_OPERATORS


class WorkflowAction(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    type: str = Field(..., description="Action type ID (e.g., 'send_email', 'ai_agent')")
    integration: Optional[str] = Field(None, description="Integration ID")
    params: Dict[str, Any] = Field(default_factory=dict)
    
    # Condition evaluation
    condition: Optional[StepCondition] = Field(None, description="Legacy single condition")
    conditions: Optional[List[StepCondition]] = Field(default_factory=list, description="Array of conditions (AND logic)")
    
    # AI Agent specific fields
    agent_type: Optional[str] = Field(None, description="If type is ai_agent, which agent to use")
    provider: Optional[str] = Field(None, description="Preferred LLM provider")
    model_tier: Optional[str] = Field(None, description="fast, balanced, or quality")
    input_mapping: Optional[Dict[str, str]] = Field(default_factory=dict, description="Context mapping for agent inputs")


class WorkflowDefinition(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Multi-Trigger Lead Notification",
                "description": "Notify Slack when leads come from HubSpot or Typeform",
                "triggers": [
                    {
                        "type": "new_lead",
                        "integration": "hubspot",
                        "params": {}
                    },
                    {
                        "type": "form_submission",
                        "integration": "typeform",
                        "params": {}
                    }
                ],
                "actions": [
                    {
                        "type": "send_slack",
                        "integration": "slack",
                        "params": {}
                    }
                ],
                "version": "1.0"
            }
        }
    )

    name: str
    description: str
    triggers: List[WorkflowTrigger] = Field(..., description="One or more triggers")
    actions: List[WorkflowAction] = Field(..., description="Linear sequence of actions")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0")

    def validate_linear_structure(self) -> bool:
        return len(self.actions) > 0 and len(self.triggers) > 0

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @property
    def trigger(self) -> Optional[WorkflowTrigger]:
        """Backwards compatibility — returns first trigger"""
        return self.triggers[0] if self.triggers else None