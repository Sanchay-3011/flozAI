"""
📄 Text Summarizer Agent
Summarizes long text into concise summaries.
"""
from flozai.core.agents.base_agent import BaseAgent


class TextSummarizerAgent(BaseAgent):
    agent_type = "text_summarizer"
    name = "Summarize Text"
    description = "Turn long documents or messages into short, clear summaries"
    icon = "file-text"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert at summarizing text clearly and concisely. "
            "Focus on key points, decisions, and action items. "
            "Write in clear business English. "
            "Always respond in JSON with exactly these fields: "
            '{"summary": "..."}'
        )

    @property
    def input_schema(self) -> dict:
        return {
            "long_text": {
                "label": "Text to summarize",
                "type": "textarea",
                "required": True,
                "placeholder": "Paste the text you want to summarize here...",
            },
            "max_length": {
                "label": "Summary length",
                "type": "select",
                "required": False,
                "options": ["1-2 sentences", "Short paragraph", "Bullet points"],
                "placeholder": "Short paragraph",
            },
        }

    @property
    def output_schema(self) -> dict:
        return {"summary": "The meeting covered three key topics..."}

    def build_user_prompt(self, inputs: dict) -> str:
        length = inputs.get("max_length", "Short paragraph")
        return (
            f"Summarize the following text as a {length}:\n\n"
            f"{inputs['long_text']}"
        )
