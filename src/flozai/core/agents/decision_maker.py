"""
🧠 Decision Maker Agent
Makes yes/no decisions based on data and context.
"""
from flozai.core.agents.base_agent import BaseAgent


class DecisionMakerAgent(BaseAgent):
    agent_type = "decision_maker"
    name = "Make Decision"
    description = "Make smart yes/no decisions to control your workflow logic"
    icon = "brain"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a business decision engine. "
            "Given a question and some data, make a clear yes/no decision. "
            "Be practical and business-focused. "
            "Always respond in JSON with exactly these fields: "
            '{"decision": true, "reasoning": "...", "confidence": 0.85}'
            "\nconfidence should be between 0.0 and 1.0"
        )

    @property
    def input_schema(self) -> dict:
        return {
            "question": {
                "label": "What decision to make?",
                "type": "textarea",
                "required": True,
                "placeholder": "e.g. Should we follow up with this lead? Should we escalate this ticket?",
            },
            "data_context": {
                "label": "What data to consider?",
                "type": "textarea",
                "required": False,
                "placeholder": "e.g. Lead score is 8, they visited pricing 3 times, last active 2 hours ago",
            },
        }

    @property
    def output_schema(self) -> dict:
        return {"decision": True, "reasoning": "The lead shows strong buying signals...", "confidence": 0.85}

    def build_user_prompt(self, inputs: dict) -> str:
        parts = [f"Question: {inputs['question']}"]
        if inputs.get("data_context"):
            parts.append(f"Data: {inputs['data_context']}")
        return "\n".join(parts)
