"""
✉️ Email Writer Agent
Writes personalized follow-up emails for leads.
"""
from flozai.core.agents.base_agent import BaseAgent


class EmailWriterAgent(BaseAgent):
    agent_type = "email_writer"
    name = "Write Email"
    description = "Write personalized follow-up emails for leads and prospects"
    icon = "mail"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a professional email copywriter for small businesses. "
            "You write short, personalized follow-up emails that feel human and warm. "
            "Never use corporate jargon. Keep emails under 150 words. "
            "Always respond in JSON with exactly these fields: "
            '{"subject": "...", "body": "..."}'
        )

    @property
    def input_schema(self) -> dict:
        return {
            "lead_name": {
                "label": "Who is this for?",
                "type": "text",
                "required": True,
                "placeholder": "e.g. Sarah Johnson",
            },
            "company": {
                "label": "Their company",
                "type": "text",
                "required": False,
                "placeholder": "e.g. Acme Corp",
            },
            "context": {
                "label": "What's the context?",
                "type": "textarea",
                "required": True,
                "placeholder": "e.g. They signed up for a demo yesterday but didn't show up",
            },
            "tone": {
                "label": "What tone?",
                "type": "select",
                "required": False,
                "options": ["Professional", "Friendly", "Casual"],
                "placeholder": "Professional",
            },
        }

    @property
    def output_schema(self) -> dict:
        return {"subject": "Follow up on your demo", "body": "Hi Sarah, ..."}

    def build_user_prompt(self, inputs: dict) -> str:
        parts = [f"Write a follow-up email for {inputs['lead_name']}."]
        if inputs.get("company"):
            parts.append(f"They work at {inputs['company']}.")
        parts.append(f"Context: {inputs['context']}")
        if inputs.get("tone"):
            parts.append(f"Tone: {inputs['tone']}")
        return " ".join(parts)
