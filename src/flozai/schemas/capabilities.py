"""
Capabilities Schema
Loads and validates the capabilities.yaml file
"""
from typing import List, Optional
from pydantic import BaseModel, Field
import yaml
from pathlib import Path


class ParamDefinition(BaseModel):
    name: str
    type: str
    description: str


class TriggerDefinition(BaseModel):
    id: str
    display_name: str
    description: str
    required_params: List[ParamDefinition]
    optional_params: List[ParamDefinition] = Field(default_factory=list)


class ActionDefinition(BaseModel):
    id: str
    display_name: str
    description: str
    required_params: List[ParamDefinition]
    optional_params: List[ParamDefinition] = Field(default_factory=list)


class IntegrationDefinition(BaseModel):
    id: str
    display_name: str
    supported_triggers: List[str]
    supported_actions: List[str]


class Capabilities(BaseModel):
    triggers: List[TriggerDefinition]
    actions: List[ActionDefinition]
    integrations: List[IntegrationDefinition]

    def get_trigger(self, trigger_id: str) -> Optional[TriggerDefinition]:
        return next((t for t in self.triggers if t.id == trigger_id), None)

    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        return next((a for a in self.actions if a.id == action_id), None)

    def get_integration(self, integration_id: str) -> Optional[IntegrationDefinition]:
        return next((i for i in self.integrations if i.id == integration_id), None)

    def validate_trigger_integration(self, trigger_id: str, integration_id: str) -> bool:
        integration = self.get_integration(integration_id)
        if not integration:
            return False
        return trigger_id in integration.supported_triggers

    def validate_action_integration(self, action_id: str, integration_id: str) -> bool:
        integration = self.get_integration(integration_id)
        if not integration:
            return False
        return action_id in integration.supported_actions


def load_capabilities(config_path: Optional[Path] = None) -> Capabilities:
    if config_path is None:
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = project_root / "config" / "capabilities.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Capabilities file not found: {config_path}")

    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    return Capabilities(**data)


# ── NO singleton cache — always read fresh from YAML ──────────────────
def get_capabilities() -> Capabilities:
    return load_capabilities()