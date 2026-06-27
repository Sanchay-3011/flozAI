"""
Unified LLM Client Interface
All providers implement this interface so agents work across any LLM.
"""
import json
import re
from abc import ABC, abstractmethod
from flozai.utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for all LLM providers."""

    provider_name: str = "unknown"

    @abstractmethod
    def _raw_chat(self, system_prompt: str, user_prompt: str, model: str, max_tokens: int) -> str:
        """Send a chat request and return raw text response."""
        ...

    def chat(self, system_prompt: str, user_prompt: str, model: str = None,
             output_json: bool = False, max_tokens: int = 800) -> dict:
        """
        High-level chat method with optional JSON output enforcement.
        Returns {"content": str, "model": str, "provider": str} or 
                {"content": parsed_dict, ...} if output_json=True.
        """
        # Append JSON instruction to system prompt
        effective_system = system_prompt
        if output_json:
            effective_system += (
                "\n\nIMPORTANT: You MUST respond with valid JSON only. "
                "No markdown, no code fences, no commentary. Pure JSON."
            )

        raw = self._raw_chat(effective_system, user_prompt, model, max_tokens)

        result = {
            "content": raw,
            "model": model or self.default_model,
            "provider": self.provider_name,
        }

        if output_json:
            parsed = self._parse_json(raw)
            if parsed is not None:
                result["content"] = parsed
            else:
                # Retry once
                logger.warning(f"[{self.provider_name}] JSON parse failed, retrying...")
                retry_prompt = (
                    f"{user_prompt}\n\n"
                    "Your previous response was not valid JSON. "
                    "Please respond with ONLY valid JSON this time."
                )
                raw2 = self._raw_chat(effective_system, retry_prompt, model, max_tokens)
                parsed2 = self._parse_json(raw2)
                if parsed2 is not None:
                    result["content"] = parsed2
                else:
                    logger.error(f"[{self.provider_name}] JSON parse failed after retry")
                    result["content"] = {"error": "Failed to generate valid JSON", "raw": raw2[:500]}
                    result["parse_failed"] = True

        return result

    @staticmethod
    def _parse_json(text: str):
        """Try to parse JSON from LLM output, stripping markdown fences."""
        cleaned = text.strip()
        # Remove markdown code fences
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            return None

    @property
    @abstractmethod
    def default_model(self) -> str:
        ...
