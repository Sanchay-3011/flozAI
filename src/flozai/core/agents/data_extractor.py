"""
🔍 Data Extractor Agent
Extracts structured data from unstructured text.
"""
from flozai.core.agents.base_agent import BaseAgent


class DataExtractorAgent(BaseAgent):
    agent_type = "data_extractor"
    name = "Extract Data"
    description = "Pull names, emails, phone numbers, and other data from text"
    icon = "search"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a precise data extraction engine. "
            "Extract the requested fields from raw text. "
            "If a field is not found, set it to null. "
            "Always respond in JSON with an 'extracted' object containing the requested fields: "
            '{"extracted": {"name": "...", "email": "...", ...}}'
        )

    @property
    def input_schema(self) -> dict:
        return {
            "raw_text": {
                "label": "Text to extract from",
                "type": "textarea",
                "required": True,
                "placeholder": "Paste the raw text (email, form, message, etc.)",
            },
            "fields_to_extract": {
                "label": "What data to extract?",
                "type": "text",
                "required": True,
                "placeholder": "e.g. name, email, company, phone number",
            },
        }

    @property
    def output_schema(self) -> dict:
        return {"extracted": {"name": "John Smith", "email": "john@example.com", "company": "Acme"}}

    def build_user_prompt(self, inputs: dict) -> str:
        return (
            f"Extract these fields: {inputs['fields_to_extract']}\n\n"
            f"From this text:\n{inputs['raw_text']}"
        )
