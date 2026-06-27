from flozai.core.workflow_builder import WorkflowBuilder
from flozai.schemas.intent_schema import ParsedIntent, TriggerIntent, ActionIntent, IntentStatus
import json

intent = ParsedIntent(
    status=IntentStatus.CLEAR,
    workflow_name="Test Workflow",
    workflow_description="Testing the builder",
    trigger=TriggerIntent(type="scheduled_time", integration="scheduler"),
    actions=[
        ActionIntent(type="generate_content", integration="openai"),
        ActionIntent(type="send_slack", integration="slack")
    ]
)

builder = WorkflowBuilder()
wf = builder.build(intent)
print(json.dumps(wf.model_dump(), indent=2))
