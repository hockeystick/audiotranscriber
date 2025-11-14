"""
Transcription Provider Factory
===============================
Factory for creating and managing transcription providers
"""

from .base import TranscriptionProvider
from .openai_provider import OpenAIProvider
from .google_provider import GoogleCloudProvider


# Available providers
PROVIDERS = {
    'openai': OpenAIProvider,
    'google': GoogleCloudProvider,
}


def get_provider(provider_name: str) -> TranscriptionProvider:
    """
    Get a transcription provider instance by name.

    Args:
        provider_name: Name of the provider ('openai' or 'google')

    Returns:
        TranscriptionProvider instance

    Raises:
        ValueError: If provider name is invalid
    """
    provider_name = provider_name.lower()

    if provider_name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {list(PROVIDERS.keys())}"
        )

    return PROVIDERS[provider_name]()


def get_available_providers() -> dict:
    """
    Get all available and configured providers.

    Returns:
        Dictionary mapping provider names to their info
    """
    available = {}

    for name, provider_class in PROVIDERS.items():
        provider = provider_class()
        info = provider.get_info()
        available[name] = info

    return available


__all__ = [
    'TranscriptionProvider',
    'OpenAIProvider',
    'GoogleCloudProvider',
    'get_provider',
    'get_available_providers',
    'PROVIDERS',
]
