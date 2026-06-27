"""
LLM Client Factory
Creates the right LLM client based on user's connected providers.
"""
from typing import Optional
from flozai.core.integrations import get_user_integrations
from flozai.core.llm.model_tiers import resolve_model
from flozai.utils.logger import get_logger

logger = get_logger(__name__)

# Priority order when no provider specified
PROVIDER_PRIORITY = ["openai", "groq", "anthropic", "gemini"]


def get_llm_client(user_id: str = "default_user", provider: str = None,
                   tier: str = "fast"):
    """
    Create an LLM client for the user.
    
    Args:
        user_id: User identifier
        provider: Specific provider to use (None = auto-detect from connected providers)
        tier: Model quality tier — "fast", "balanced", or "quality"
    
    Returns:
        LLMClient instance ready to use
    
    Raises:
        ValueError if no AI provider is connected
    """
    from flozai.core.llm.openai_provider import OpenAIProvider
    from flozai.core.llm.groq_provider import GroqProvider
    from flozai.core.llm.anthropic_provider import AnthropicProvider
    from flozai.core.llm.gemini_provider import GeminiProvider

    integrations = get_user_integrations(user_id)
    
    # Map provider names to classes
    provider_classes = {
        "openai": OpenAIProvider,
        "groq": GroqProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
    }

    # If specific provider requested
    if provider:
        config = integrations.get(provider, {})
        api_key = config.get("credential_data", {}).get("apiKey")
        if not api_key:
            raise ValueError(
                f"{provider.title()} is not connected. "
                f"Go to Settings → AI Providers to add your {provider.title()} API key."
            )
        cls = provider_classes.get(provider)
        if not cls:
            raise ValueError(f"Unknown AI provider: {provider}")
        model = resolve_model(provider, tier)
        return cls(api_key=api_key, model=model)

    # Auto-detect: use first connected provider by priority
    for prov in PROVIDER_PRIORITY:
        config = integrations.get(prov, {})
        api_key = config.get("credential_data", {}).get("apiKey")
        if api_key:
            cls = provider_classes[prov]
            model = resolve_model(prov, tier)
            logger.info(f"Using {prov} as LLM provider (model: {model})")
            return cls(api_key=api_key, model=model)

    raise ValueError(
        "No AI provider connected. Go to Settings → AI Providers "
        "to connect OpenAI, Groq, Claude, or Gemini."
    )


def get_connected_providers(user_id: str = "default_user") -> list:
    """Returns list of connected AI provider IDs."""
    integrations = get_user_integrations(user_id)
    connected = []
    for prov in PROVIDER_PRIORITY:
        config = integrations.get(prov, {})
        if config.get("credential_data", {}).get("apiKey"):
            connected.append(prov)
    return connected
