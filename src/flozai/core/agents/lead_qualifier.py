"""
🎯 Lead Qualifier Agent
Scores and categorizes leads based on their profile data.
"""
from flozai.core.agents.base_agent import BaseAgent


class LeadQualifierAgent(BaseAgent):
    agent_type = "lead_qualifier"
    name = "Qualify Lead"
    description = "Score and categorize leads as hot, warm, or cold"
    icon = "target"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert sales lead qualifier for small businesses. "
            "You analyze lead data and score them from 1-10 with a category. "
            "Be practical and focus on buying signals. "
            "Always respond in JSON with exactly these fields: "
            '{"score": 8, "category": "hot", "reasoning": "..."}'
            "\nCategories: hot (score 8-10), warm (score 5-7), cold (score 1-4)"
        )

    @property
    def input_schema(self) -> dict:
        return {
            "lead_name": {
                "label": "Lead name",
                "type": "text",
                "required": True,
                "placeholder": "e.g. John Smith",
            },
            "email": {
                "label": "Their email",
                "type": "text",
                "required": False,
                "placeholder": "e.g. john@company.com",
            },
            "company": {
                "label": "Company",
                "type": "text",
                "required": False,
                "placeholder": "e.g. TechStart Inc",
            },
            "source": {
                "label": "Where did they come from?",
                "type": "select",
                "required": False,
                "options": ["Website", "Referral", "LinkedIn", "Cold Outreach", "Event", "Other"],
                "placeholder": "Website",
            },
            "notes": {
                "label": "Additional info",
                "type": "textarea",
                "required": False,
                "placeholder": "e.g. Downloaded pricing PDF, visited 5 pages, enterprise plan interest",
            },
        }

    @property
    def output_schema(self) -> dict:
        return {"score": 8, "category": "hot", "reasoning": "Strong buying signals..."}

    def build_user_prompt(self, inputs: dict) -> str:
        parts = [f"Qualify this lead: {inputs['lead_name']}"]
        if inputs.get("email"):
            parts.append(f"Email: {inputs['email']}")
        if inputs.get("company"):
            parts.append(f"Company: {inputs['company']}")
        if inputs.get("source"):
            parts.append(f"Source: {inputs['source']}")
        if inputs.get("notes"):
            parts.append(f"Notes: {inputs['notes']}")
        return "\n".join(parts)
