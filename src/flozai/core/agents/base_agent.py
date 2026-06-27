"""
Base AI Agent
All agents inherit from this and define prompts + schemas.
"""
from abc import ABC, abstractmethod
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for AI agents."""

    agent_type: str = ""
    name: str = ""
    description: str = ""
    icon: str = ""  # lucide icon name

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @property
    @abstractmethod
    def input_schema(self) -> dict:
        """
        Returns dict of input fields:
        {
            "field_name": {
                "label": "Human Friendly Label",
                "type": "text" | "textarea" | "select",
                "required": True/False,
                "placeholder": "...",
                "options": [...] (for select type)
            }
        }
        """
        ...

    @property
    @abstractmethod
    def output_schema(self) -> dict:
        """Returns example output shape."""
        ...

    @abstractmethod
    def build_user_prompt(self, inputs: dict) -> str:
        """Build the user prompt from inputs."""
        ...

    def execute(self, inputs: dict, llm_client) -> dict:
        """
        Run the agent with given inputs and LLM client.
        Returns structured output dict.
        """
        # Validate required inputs
        missing = []
        for field, config in self.input_schema.items():
            if config.get("required") and not inputs.get(field):
                missing.append(config.get("label", field))

        if missing:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing)}",
                "output": None,
            }

        # Build prompt
        user_prompt = self.build_user_prompt(inputs)

        try:
            result = llm_client.chat(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                output_json=True,
                max_tokens=800,
            )

            if result.get("parse_failed"):
                logger.warning(f"Agent {self.agent_type} JSON parse failed")
                return {
                    "status": "partial",
                    "output": result["content"],
                    "model": result.get("model"),
                    "provider": result.get("provider"),
                    "warning": "Output may not be properly structured",
                }

            return {
                "status": "success",
                "output": result["content"],
                "model": result.get("model"),
                "provider": result.get("provider"),
            }

        except ValueError as e:
            error_msg = str(e)
            logger.error(f"Agent {self.agent_type} failed: {error_msg}")
            return {
                "status": "error",
                "error": error_msg,
                "output": None,
            }
        except Exception as e:
            logger.error(f"Agent {self.agent_type} unexpected error: {e}")
            return {
                "status": "error",
                "error": "An unexpected error occurred. Please try again.",
                "output": None,
            }

    def to_metadata(self) -> dict:
        """Return agent metadata for the frontend."""
        return {
            "agent_type": self.agent_type,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
        }
