"""
Unit tests for the client module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
import json
import time

from ainative.client import AINativeClient, ClientConfig
from ainative.auth import AuthConfig
from ainative.exceptions import (
    APIError,
    NetworkError,
    RateLimitError,
    AuthenticationError
)


class TestClientConfig:
    """Test ClientConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = ClientConfig()
        assert config.base_url == "https://api.ainative.studio/api/v1"
        assert config.timeout == 30
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
        assert config.verify_ssl is True
        assert config.debug is False
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = ClientConfig(
            base_url="https://custom.example.com",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            verify_ssl=False,
            debug=True
        )
        assert config.base_url == "https://custom.example.com/api/v1"
        assert config.timeout == 60
        assert config.max_retries == 5
        assert config.retry_delay == 2.0
        assert config.verify_ssl is False
        assert config.debug is True
    
    def test_base_url_normalization(self):
        """Test base URL normalization."""
        # Removes trailing slash
        config1 = ClientConfig(base_url="https://example.com/")
        assert config1.base_url == "https://example.com/api/v1"
        
        # Adds API version if not present
        config2 = ClientConfig(base_url="https://example.com")
        assert config2.base_url == "https://example.com/api/v1"
        
        # Preserves existing API version
        config3 = ClientConfig(base_url="https://example.com/api/v1")
        assert config3.base_url == "https://example.com/api/v1"
        
        # Preserves different API version
        config4 = ClientConfig(base_url="https://example.com/api/v2")
        assert config4.base_url == "https://example.com/api/v2"


class TestAINativeClient:
    """Test AINativeClient class."""
    
    def test_init_default_config(self, api_key):
        """Test initialization with default configuration."""
        with patch('httpx.Client'):
            client = AINativeClient(api_key=api_key)
            
            assert client.auth_config.api_key == api_key
            assert client.config.base_url == "https://api.ainative.studio/api/v1"
            assert client.organization_id is None
    
    def test_init_custom_config(self, auth_config, client_config):
        """Test initialization with custom configuration."""
        with patch('httpx.Client'):
            client = AINativeClient(
                auth_config=auth_config,
                config=client_config,
                organization_id="org_123"
            )
            
            assert client.auth_config == auth_config
            assert client.config == client_config
            assert client.organization_id == "org_123"
    
    def test_init_with_direct_params(self):
        """Test initialization with direct parameters."""
        with patch('httpx.Client'):
            client = AINativeClient(
                api_key="direct-key",
                api_secret="direct-secret",
                base_url="https://direct.example.com",
                organization_id="direct-org"
            )
            
            assert client.auth_config.api_key == "direct-key"
            assert client.auth_config.api_secret == "direct-secret"
            assert client.config.base_url == "https://direct.example.com/api/v1"
            assert client.organization_id == "direct-org"
    
    def test_httpx_client_initialization(self, client_config):
        """Test httpx client initialization."""
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            client = AINativeClient(api_key="test", config=client_config)
            
            mock_client_class.assert_called_once_with(
                timeout=client_config.timeout,
                verify=client_config.verify_ssl
            )
            assert client._client == mock_client
    
    def test_sub_clients_lazy_initialization(self, client):
        """Test that sub-clients are created lazily."""
        # Initially None
        assert client._zerodb is None
        assert client._agent_swarm is None
        
        # Created on first access
        zerodb = client.zerodb
        agent_swarm = client.agent_swarm
        
        assert client._zerodb is not None
        assert client._agent_swarm is not None
        
        # Same instance returned on subsequent access
        assert client.zerodb is zerodb
        assert client.agent_swarm is agent_swarm


class TestAINativeClientRequests:
    """Test AINativeClient request methods."""
    
    def test_successful_request(self, client, mock_response):
        """Test successful API request."""
        response_data = {"status": "success", "data": {"id": "123"}}
        mock_resp = mock_response(200, response_data)
        client._client.request.return_value = mock_resp
        
        result = client.request("GET", "/test")
        
        assert result == response_data
        client._client.request.assert_called_once()
    
    def test_request_with_data(self, client, mock_response):
        """Test request with JSON data."""
        request_data = {"name": "test", "value": 123}
        response_data = {"created": True}
        mock_resp = mock_response(201, response_data)
        client._client.request.return_value = mock_resp
        
        result = client.request("POST", "/test", data=request_data)
        
        assert result == response_data
        client._client.request.assert_called_once_with(
            method="POST",
            url=client.config.base_url + "/test",
            json=request_data,
            params=None,
            headers=client.auth.get_headers()
        )
    
    def test_request_with_params(self, client, mock_response):
        """Test request with query parameters."""
        params = {"limit": 10, "offset": 0}
        response_data = {"items": []}
        mock_resp = mock_response(200, response_data)
        client._client.request.return_value = mock_resp
        
        result = client.request("GET", "/test", params=params)
        
        assert result == response_data
        call_args = client._client.request.call_args
        assert call_args[1]["params"] == params
    
    def test_request_with_custom_headers(self, client, mock_response):
        """Test request with additional headers."""
        custom_headers = {"Custom-Header": "value"}
        mock_resp = mock_response(200, {})
        client._client.request.return_value = mock_resp
        
        client.request("GET", "/test", headers=custom_headers)
        
        call_args = client._client.request.call_args
        headers = call_args[1]["headers"]
        assert headers["Custom-Header"] == "value"
        # Should also include auth headers
        assert "X-API-Key" in headers
    
    def test_request_with_organization_id(self, client, mock_response):
        """Test request includes organization ID header when set."""
        client.organization_id = "org_456"
        mock_resp = mock_response(200, {})
        client._client.request.return_value = mock_resp
        
        client.request("GET", "/test")
        
        call_args = client._client.request.call_args
        headers = call_args[1]["headers"]
        assert headers["X-Organization-ID"] == "org_456"
    
    def test_request_empty_response(self, client):
        """Test request with empty response."""
        mock_resp = Mock()
        mock_resp.status_code = 204
        mock_resp.text = ""
        client._client.request.return_value = mock_resp
        
        result = client.request("DELETE", "/test")
        assert result == {}
    
    def test_url_construction(self, client, mock_response):
        """Test URL construction with different endpoint formats."""
        mock_resp = mock_response(200, {})
        client._client.request.return_value = mock_resp
        
        # Test various endpoint formats
        endpoints = [
            "/test",
            "test",
            "/api/test",
            "api/test"
        ]
        
        for endpoint in endpoints:
            client.request("GET", endpoint)
            call_args = client._client.request.call_args
            url = call_args[1]["url"]
            assert url.endswith("/test") or url.endswith("/api/test")


class TestAINativeClientErrorHandling:
    """Test AINativeClient error handling."""
    
    def test_rate_limit_error(self, client):
        """Test rate limit error handling."""
        mock_resp = Mock()
        mock_resp.status_code = 429
        mock_resp.headers = {"Retry-After": "60"}
        client._client.request.return_value = mock_resp
        
        with pytest.raises(RateLimitError) as exc_info:
            client.request("GET", "/test")
        
        assert exc_info.value.retry_after == 60
    
    def test_authentication_error(self, client):
        """Test authentication error handling."""
        mock_resp = Mock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        client._client.request.return_value = mock_resp
        
        with pytest.raises(AuthenticationError):
            client.request("GET", "/test")
    
    def test_api_error_400(self, client):
        """Test API error for 400 status."""
        mock_resp = Mock()
        mock_resp.status_code = 400
        mock_resp.text = '{"error": "Bad request"}'
        client._client.request.return_value = mock_resp
        
        with pytest.raises(APIError) as exc_info:
            client.request("POST", "/test")
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.response_body == '{"error": "Bad request"}'
    
    def test_api_error_500(self, client):
        """Test API error for 500 status."""
        mock_resp = Mock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        client._client.request.return_value = mock_resp
        
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/test")
        
        assert exc_info.value.status_code == 500
    
    def test_network_error(self, client):
        """Test network error handling."""
        client._client.request.side_effect = httpx.NetworkError("Connection failed")
        
        with pytest.raises(NetworkError) as exc_info:
            client.request("GET", "/test")
        
        assert "Connection failed" in str(exc_info.value)
    
    def test_timeout_error(self, client):
        """Test timeout error handling."""
        client._client.request.side_effect = httpx.TimeoutException("Request timeout")
        
        with pytest.raises(NetworkError) as exc_info:
            client.request("GET", "/test")
        
        assert "timed out" in str(exc_info.value).lower()
    
    @patch('time.sleep')
    def test_retry_logic_network_error(self, mock_sleep, client, mock_response):
        """Test retry logic for network errors."""
        # First two calls fail, third succeeds
        client._client.request.side_effect = [
            httpx.NetworkError("Connection failed"),
            httpx.NetworkError("Connection failed"),
            mock_response(200, {"success": True})
        ]
        
        result = client.request("GET", "/test")
        
        assert result == {"success": True}
        assert client._client.request.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('time.sleep')
    def test_retry_exhausted(self, mock_sleep, client):
        """Test when all retries are exhausted."""
        client._client.request.side_effect = httpx.NetworkError("Persistent failure")
        
        with pytest.raises(NetworkError):
            client.request("GET", "/test")
        
        assert client._client.request.call_count == 3  # Initial + 2 retries
        assert mock_sleep.call_count == 2
    
    @patch('time.sleep')
    def test_retry_delay_increases(self, mock_sleep, client):
        """Test that retry delay increases with each attempt."""
        client._client.request.side_effect = httpx.NetworkError("Failure")
        
        with pytest.raises(NetworkError):
            client.request("GET", "/test")
        
        # Check that sleep was called with increasing delays
        sleep_calls = [call.args[0] for call in mock_sleep.call_calls]
        assert len(sleep_calls) == 2
        assert sleep_calls[0] < sleep_calls[1]  # Delay increases


class TestAINativeClientConvenienceMethods:
    """Test convenience HTTP methods."""
    
    def test_get_method(self, client, mock_response):
        """Test GET convenience method."""
        response_data = {"data": "test"}
        mock_resp = mock_response(200, response_data)
        client._client.request.return_value = mock_resp
        
        result = client.get("/test", params={"key": "value"})
        
        assert result == response_data
        client._client.request.assert_called_once()
        call_args = client._client.request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["params"] == {"key": "value"}
    
    def test_post_method(self, client, mock_response):
        """Test POST convenience method."""
        request_data = {"name": "test"}
        response_data = {"created": True}
        mock_resp = mock_response(201, response_data)
        client._client.request.return_value = mock_resp
        
        result = client.post("/test", data=request_data)
        
        assert result == response_data
        call_args = client._client.request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["json"] == request_data
    
    def test_put_method(self, client, mock_response):
        """Test PUT convenience method."""
        mock_resp = mock_response(200, {"updated": True})
        client._client.request.return_value = mock_resp
        
        result = client.put("/test", data={"field": "value"})
        
        assert result == {"updated": True}
        call_args = client._client.request.call_args
        assert call_args[1]["method"] == "PUT"
    
    def test_delete_method(self, client, mock_response):
        """Test DELETE convenience method."""
        mock_resp = mock_response(204, {})
        client._client.request.return_value = mock_resp
        
        result = client.delete("/test")
        
        assert result == {}
        call_args = client._client.request.call_args
        assert call_args[1]["method"] == "DELETE"
    
    def test_patch_method(self, client, mock_response):
        """Test PATCH convenience method."""
        mock_resp = mock_response(200, {"patched": True})
        client._client.request.return_value = mock_resp
        
        result = client.patch("/test", data={"update": "value"})
        
        assert result == {"patched": True}
        call_args = client._client.request.call_args
        assert call_args[1]["method"] == "PATCH"


class TestAINativeClientUtilityMethods:
    """Test utility methods."""
    
    def test_health_check(self, client, mock_response):
        """Test health check method."""
        health_data = {"status": "healthy", "version": "1.0.0"}
        mock_resp = mock_response(200, health_data)
        client._client.request.return_value = mock_resp
        
        result = client.health_check()
        
        assert result == health_data
        call_args = client._client.request.call_args
        assert call_args[1]["url"].endswith("/health")
    
    def test_close_method(self, client):
        """Test client close method."""
        client.close()
        client._client.close.assert_called_once()
    
    def test_context_manager_enter(self, client):
        """Test context manager entry."""
        result = client.__enter__()
        assert result is client
    
    def test_context_manager_exit(self, client):
        """Test context manager exit."""
        client.__exit__(None, None, None)
        client._client.close.assert_called_once()
    
    def test_context_manager_usage(self, auth_config):
        """Test full context manager usage."""
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            with AINativeClient(auth_config=auth_config) as client:
                assert isinstance(client, AINativeClient)
            
            mock_client.close.assert_called_once()


class TestAINativeClientIntegration:
    """Test client integration scenarios."""
    
    def test_full_request_flow(self, auth_config, client_config):
        """Test complete request flow."""
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = '{"result": "success"}'
            mock_resp.json.return_value = {"result": "success"}
            
            mock_client.request.return_value = mock_resp
            mock_client_class.return_value = mock_client
            
            client = AINativeClient(
                auth_config=auth_config,
                config=client_config,
                organization_id="org_test"
            )
            
            result = client.post("/projects", data={"name": "Test Project"})
            
            assert result == {"result": "success"}
            
            # Verify the call was made correctly
            mock_client.request.assert_called_once()
            call_args = mock_client.request.call_args
            
            assert call_args[1]["method"] == "POST"
            assert call_args[1]["url"] == client_config.base_url + "/projects"
            assert call_args[1]["json"] == {"name": "Test Project"}
            
            headers = call_args[1]["headers"]
            assert headers["X-API-Key"] == auth_config.api_key
            assert headers["X-Organization-ID"] == "org_test"
            assert "X-SDK-Version" in headers
    
    def test_error_handling_flow(self, client):
        """Test error handling in request flow."""
        # Test multiple error types in sequence
        errors = [
            (httpx.NetworkError("Network issue"), NetworkError),
            (Mock(status_code=401), AuthenticationError),
            (Mock(status_code=429, headers={"Retry-After": "30"}), RateLimitError),
            (Mock(status_code=500, text="Server Error"), APIError)
        ]
        
        for error_input, expected_exception in errors:
            client._client.request.side_effect = [error_input]
            
            with pytest.raises(expected_exception):
                client.request("GET", "/test")
            
            client._client.request.reset_mock()