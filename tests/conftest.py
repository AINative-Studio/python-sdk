"""
Pytest configuration and fixtures for AINative SDK tests.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import json
import httpx

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ainative import AINativeClient
from ainative.auth import AuthConfig, APIKeyAuth
from ainative.client import ClientConfig


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-12345"


@pytest.fixture
def api_secret():
    """Test API secret."""
    return "test-api-secret-67890"


@pytest.fixture
def auth_config(api_key, api_secret):
    """Auth configuration for testing."""
    return AuthConfig(
        api_key=api_key,
        api_secret=api_secret,
        environment="development"
    )


@pytest.fixture
def client_config():
    """Client configuration for testing."""
    return ClientConfig(
        base_url="https://api.test.ainative.studio",
        timeout=30,
        max_retries=3,
        retry_delay=1.0,
        verify_ssl=True,
        debug=True
    )


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client."""
    with patch('httpx.Client') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def client(auth_config, client_config):
    """AINative client instance for testing."""
    with patch('httpx.Client') as mock_client_class:
        mock_instance = MagicMock()
        mock_client_class.return_value = mock_instance
        
        client = AINativeClient(
            auth_config=auth_config,
            config=client_config
        )
        
        # Mock the HTTP client methods
        mock_instance.request = MagicMock()
        mock_instance.close = MagicMock()
        
        # Replace the httpx client with our mock
        client._client = mock_instance
        
        return client


@pytest.fixture
def mock_response():
    """Factory for creating mock HTTP responses."""
    def _create_response(status_code=200, json_data=None, text="", headers=None):
        response = Mock(spec=httpx.Response)
        response.status_code = status_code
        response.text = text or json.dumps(json_data or {})
        response.json.return_value = json_data or {}
        response.headers = headers or {}
        return response
    return _create_response


@pytest.fixture
def sample_project():
    """Sample project data."""
    return {
        "id": "proj_test123",
        "name": "Test Project",
        "description": "A test project",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "metadata": {"test": True},
        "config": {"dimension": 768}
    }


@pytest.fixture
def sample_vector():
    """Sample vector data."""
    return {
        "id": "vec_test123",
        "vector": [0.1, 0.2, 0.3, 0.4, 0.5],
        "metadata": {
            "text": "Test vector",
            "category": "test"
        },
        "score": 0.95
    }


@pytest.fixture
def sample_memory():
    """Sample memory data."""
    return {
        "id": "mem_test123",
        "content": "Test memory content",
        "title": "Test Memory",
        "tags": ["test", "sample"],
        "priority": "medium",
        "metadata": {"test": True},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_agent():
    """Sample agent data."""
    return {
        "id": "agent_test123",
        "type": "researcher",
        "name": "Test Agent",
        "capabilities": ["web_search", "analysis"],
        "config": {
            "temperature": 0.7,
            "max_tokens": 2000
        }
    }


@pytest.fixture
def sample_swarm():
    """Sample swarm data."""
    return {
        "id": "swarm_test123",
        "project_id": "proj_test123",
        "status": "running",
        "agents": ["agent_001", "agent_002"],
        "objective": "Test objective",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_analytics():
    """Sample analytics data."""
    return {
        "usage": {
            "vectors_stored": 1000,
            "queries_executed": 500,
            "storage_bytes": 1048576
        },
        "performance": {
            "avg_latency_ms": 25,
            "p99_latency_ms": 100,
            "throughput_qps": 50
        },
        "costs": {
            "storage_cost": 10.50,
            "compute_cost": 25.00,
            "total_cost": 35.50
        }
    }


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    env_vars = [
        "AINATIVE_API_KEY",
        "AINATIVE_API_SECRET",
        "AINATIVE_ORG_ID"
    ]
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value


@pytest.fixture
def mock_time():
    """Mock time for testing."""
    with patch('time.time') as mock:
        mock.return_value = 1704067200  # 2024-01-01 00:00:00
        yield mock


@pytest.fixture
def mock_datetime():
    """Mock datetime for testing."""
    with patch('datetime.datetime') as mock:
        mock.now.return_value = datetime(2024, 1, 1, 0, 0, 0)
        mock.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        yield mock