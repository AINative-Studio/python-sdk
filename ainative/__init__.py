"""
AINative Python SDK

Official Python SDK for AINative Studio APIs including ZeroDB and Agent Swarm operations.
"""

__version__ = "0.1.0"
__author__ = "AINative Team"
__email__ = "support@ainative.studio"

from .client import AINativeClient
from .auth import AuthConfig, APIKeyAuth
from .exceptions import (
    AINativeException,
    AuthenticationError,
    APIError,
    NetworkError,
    ValidationError,
    RateLimitError,
)

# Convenience imports for common operations
from .zerodb import ZeroDBClient
from .agent_swarm import AgentSwarmClient

__all__ = [
    "AINativeClient",
    "AuthConfig",
    "APIKeyAuth",
    "AINativeException",
    "AuthenticationError",
    "APIError",
    "NetworkError",
    "ValidationError",
    "RateLimitError",
    "ZeroDBClient",
    "AgentSwarmClient",
]