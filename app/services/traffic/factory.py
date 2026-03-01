"""
Factory for creating traffic provider instances
"""
from app.services.traffic.base import TrafficProvider
from app.services.traffic.mock_provider import MockTrafficProvider
from app.services.traffic.mitm_provider import MitmTrafficProvider


def get_traffic_provider(provider_type: str = "mock", **kwargs) -> TrafficProvider:
    """
    Factory function to create traffic provider instances.

    Args:
        provider_type: Type of provider ("mock" or "mitm")
        **kwargs: Additional arguments passed to provider constructor

    Returns:
        TrafficProvider instance

    Raises:
        ValueError: If provider type is unknown
    """
    providers = {
        "mock": MockTrafficProvider,
        "mitm": MitmTrafficProvider,
    }

    provider_class = providers.get(provider_type.lower())

    if provider_class is None:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Valid options: {', '.join(providers.keys())}"
        )

    try:
        return provider_class(**kwargs)
    except NotImplementedError as e:
        raise RuntimeError(f"Provider {provider_type} not available: {e}")
