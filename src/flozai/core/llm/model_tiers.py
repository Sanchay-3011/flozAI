"""
Model Tier Mapping
Maps user-friendly tiers (Fast/Balanced/Quality) to provider-specific models.
"""

MODEL_TIERS = {
    "openai": {
        "fast":     "gpt-4o-mini",
        "balanced": "gpt-4o-mini",
        "quality":  "gpt-4o",
    },
    "groq": {
        "fast":     "llama-3.3-70b-versatile",
        "balanced": "llama-3.3-70b-versatile",
        "quality":  "llama-3.3-70b-versatile",
    },
    "anthropic": {
        "fast":     "claude-3-5-haiku-latest",
        "balanced": "claude-3-5-haiku-latest",
        "quality":  "claude-sonnet-4-20250514",
    },
    "gemini": {
        "fast":     "gemini-2.0-flash",
        "balanced": "gemini-2.0-flash",
        "quality":  "gemini-2.5-pro-preview-06-05",
    },
}

TIER_LABELS = {
    "fast":     {"label": "Fast", "emoji": "⚡", "description": "Quick responses, lower cost"},
    "balanced": {"label": "Balanced", "emoji": "⚖️", "description": "Good balance of speed and quality"},
    "quality":  {"label": "High Quality", "emoji": "🏆", "description": "Best output, slower and more expensive"},
}

# Available models per provider (for advanced users)
PROVIDER_MODELS = {
    "openai":    ["gpt-4o-mini", "gpt-4o"],
    "groq":      ["llama-3.3-70b-versatile"],
    "anthropic": ["claude-3-5-haiku-latest", "claude-sonnet-4-20250514"],
    "gemini":    ["gemini-2.0-flash", "gemini-2.5-pro-preview-06-05"],
}


def resolve_model(provider: str, tier: str = "fast") -> str:
    """Get the specific model name for a provider + tier combination."""
    provider_tiers = MODEL_TIERS.get(provider, {})
    return provider_tiers.get(tier, provider_tiers.get("fast", "gpt-4o-mini"))
