"""
LLM Client (Groq API)
Wrapper around the Groq SDK for fast inference during development
"""
import os
from typing import Optional, Dict, Any
import json


class LLMClient:
    """Client for interacting with Groq API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        max_tokens: int = 800,
        temperature: float = 0.0
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        try:
            from groq import Groq
        except ImportError:
            raise ImportError(
                "The 'groq' package is required but not installed. "
                "Run: pip install groq   (or use the project venv)"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": self.max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Model returned empty content")
            return content
        except Exception as e:
            print(f"LLM Error: {e}")
            # Fallback JSON to ensure we never crash on empty content or rate limits
            return '{"status": "needs_clarification", "clarification_question": "Temporary API error or rate limit. Please try again later.", "workflow_name": "", "workflow_description": "", "triggers": [], "actions": []}'

    def complete_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        json_system = f"""{system_prompt}

CRITICAL: You MUST respond with ONLY valid JSON. No explanations, no markdown, no code blocks.
Start your response with {{ and end with }}."""

        response_text = self.complete(json_system, user_message, temperature)
        response_text = response_text.strip()

        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON. Raw response:\n{response_text}")
            raise e