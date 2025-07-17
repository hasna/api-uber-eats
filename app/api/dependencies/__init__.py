"""
API dependencies
"""
from app.api.dependencies.auth import get_uber_eats_token, get_optional_uber_eats_token

__all__ = [
    "get_uber_eats_token",
    "get_optional_uber_eats_token",
]