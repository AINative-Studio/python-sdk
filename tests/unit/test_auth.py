"""
Unit tests for the authentication module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
import time
import hashlib
import hmac
import base64

from ainative.auth import AuthConfig, APIKeyAuth, MultiTenantAuth


class TestAuthConfig:
    """Test AuthConfig class."""
    
    def test_init_with_direct_values(self):
        """Test initialization with direct values."""
        config = AuthConfig(
            api_key="test-key",
            api_secret="test-secret",
            environment="production"
        )
        assert config.api_key == "test-key"
        assert config.api_secret == "test-secret"
        assert config.environment == "production"
        assert config.auto_refresh is True
        assert config.timeout == 30
    
    def test_init_from_environment(self):
        """Test initialization from environment variables."""
        with patch.dict(os.environ, {
            'AINATIVE_API_KEY': 'env-key',
            'AINATIVE_API_SECRET': 'env-secret'
        }):
            config = AuthConfig()
            assert config.api_key == "env-key"
            assert config.api_secret == "env-secret"
    
    def test_environment_override(self):
        """Test that direct values override environment variables."""
        with patch.dict(os.environ, {
            'AINATIVE_API_KEY': 'env-key',
            'AINATIVE_API_SECRET': 'env-secret'
        }):
            config = AuthConfig(
                api_key="direct-key",
                api_secret="direct-secret"
            )
            assert config.api_key == "direct-key"
            assert config.api_secret == "direct-secret"
    
    def test_invalid_environment(self):
        """Test initialization with invalid environment."""
        with pytest.raises(ValueError, match="Invalid environment"):
            AuthConfig(environment="invalid")
    
    def test_valid_environments(self):
        """Test all valid environment options."""
        valid_envs = ["production", "staging", "development", "local"]
        for env in valid_envs:
            config = AuthConfig(api_key="key", environment=env)
            assert config.environment == env
    
    def test_is_configured_with_api_key(self):
        """Test is_configured property with API key."""
        config = AuthConfig(api_key="test-key")
        assert config.is_configured is True
    
    def test_is_configured_without_api_key(self):
        """Test is_configured property without API key."""
        config = AuthConfig()
        assert config.is_configured is False
    
    def test_post_init_processing(self):
        """Test post-initialization processing."""
        config = AuthConfig(
            api_key="test-key",
            timeout=60,
            auto_refresh=False
        )
        assert config.timeout == 60
        assert config.auto_refresh is False


class TestAPIKeyAuth:
    """Test APIKeyAuth class."""
    
    def test_init(self, auth_config):
        """Test initialization."""
        auth = APIKeyAuth(auth_config)
        assert auth.config == auth_config
        assert auth._token_cache is None
        assert auth._token_expiry == 0
    
    def test_get_headers_basic(self, auth_config):
        """Test getting basic headers."""
        auth = APIKeyAuth(auth_config)
        headers = auth.get_headers()
        
        assert headers["X-API-Key"] == auth_config.api_key
        assert headers["X-SDK-Version"] == "0.1.0"
        assert headers["X-SDK-Language"] == "Python"
    
    def test_get_headers_no_api_key(self):
        """Test getting headers without API key."""
        config = AuthConfig()
        auth = APIKeyAuth(config)
        
        with pytest.raises(ValueError, match="API key not configured"):
            auth.get_headers()
    
    @patch('time.time')
    def test_get_headers_with_signature(self, mock_time, auth_config):
        """Test getting headers with HMAC signature."""
        mock_time.return_value = 1704067200
        
        auth = APIKeyAuth(auth_config)
        headers = auth.get_headers()
        
        assert "X-Timestamp" in headers
        assert headers["X-Timestamp"] == "1704067200"
        assert "X-Signature" in headers
        
        # Verify signature format
        signature = headers["X-Signature"]
        assert len(signature) > 0
        # Should be base64 encoded
        try:
            base64.b64decode(signature)
        except Exception:
            pytest.fail("Signature is not valid base64")
    
    @patch('time.time')
    def test_generate_signature(self, mock_time, auth_config):
        """Test signature generation."""
        mock_time.return_value = 1704067200
        
        auth = APIKeyAuth(auth_config)
        timestamp = "1704067200"
        signature = auth._generate_signature(timestamp)
        
        # Recreate expected signature
        message = f"{auth_config.api_key}{timestamp}"
        expected = hmac.new(
            auth_config.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_b64 = base64.b64encode(expected).decode()
        
        assert signature == expected_b64
    
    def test_get_headers_without_secret(self):
        """Test getting headers without API secret."""
        config = AuthConfig(api_key="test-key")  # No secret
        auth = APIKeyAuth(config)
        headers = auth.get_headers()
        
        assert "X-API-Key" in headers
        assert "X-Timestamp" not in headers
        assert "X-Signature" not in headers
    
    def test_get_bearer_token(self, auth_config):
        """Test getting bearer token (placeholder)."""
        auth = APIKeyAuth(auth_config)
        token = auth.get_bearer_token()
        assert token is None  # Placeholder for future OAuth
    
    def test_validate_credentials_valid(self, auth_config):
        """Test credential validation with valid config."""
        auth = APIKeyAuth(auth_config)
        assert auth.validate_credentials() is True
    
    def test_validate_credentials_invalid(self):
        """Test credential validation with invalid config."""
        config = AuthConfig()  # No API key
        auth = APIKeyAuth(config)
        assert auth.validate_credentials() is False
    
    def test_refresh_token(self, auth_config):
        """Test token refresh (placeholder)."""
        auth = APIKeyAuth(auth_config)
        assert auth.refresh_token() is True  # Placeholder


class TestMultiTenantAuth:
    """Test MultiTenantAuth class."""
    
    def test_init_with_org_id(self, auth_config):
        """Test initialization with organization ID."""
        auth = MultiTenantAuth(auth_config, organization_id="org-123")
        assert auth.organization_id == "org-123"
        assert auth.config == auth_config
    
    def test_init_from_environment(self, auth_config):
        """Test initialization with org ID from environment."""
        with patch.dict(os.environ, {'AINATIVE_ORG_ID': 'env-org-456'}):
            auth = MultiTenantAuth(auth_config)
            assert auth.organization_id == "env-org-456"
    
    def test_init_direct_overrides_env(self, auth_config):
        """Test that direct org ID overrides environment."""
        with patch.dict(os.environ, {'AINATIVE_ORG_ID': 'env-org'}):
            auth = MultiTenantAuth(auth_config, organization_id="direct-org")
            assert auth.organization_id == "direct-org"
    
    def test_get_headers_with_org(self, auth_config):
        """Test getting headers with organization ID."""
        auth = MultiTenantAuth(auth_config, organization_id="org-789")
        headers = auth.get_headers()
        
        assert headers["X-Organization-ID"] == "org-789"
        assert headers["X-API-Key"] == auth_config.api_key
        assert headers["X-SDK-Version"] == "0.1.0"
    
    def test_get_headers_without_org(self, auth_config):
        """Test getting headers without organization ID."""
        auth = MultiTenantAuth(auth_config)
        headers = auth.get_headers()
        
        assert "X-Organization-ID" not in headers
        assert headers["X-API-Key"] == auth_config.api_key
    
    @patch('time.time')
    def test_get_headers_full_context(self, mock_time, auth_config):
        """Test getting headers with full context."""
        mock_time.return_value = 1704067200
        
        auth = MultiTenantAuth(auth_config, organization_id="org-full")
        headers = auth.get_headers()
        
        # Should have all headers
        assert headers["X-API-Key"] == auth_config.api_key
        assert headers["X-Organization-ID"] == "org-full"
        assert headers["X-SDK-Version"] == "0.1.0"
        assert headers["X-SDK-Language"] == "Python"
        assert headers["X-Timestamp"] == "1704067200"
        assert "X-Signature" in headers
    
    def test_inheritance_from_base(self, auth_config):
        """Test that MultiTenantAuth inherits from APIKeyAuth."""
        auth = MultiTenantAuth(auth_config, organization_id="org-test")
        
        # Should have inherited methods
        assert hasattr(auth, 'get_bearer_token')
        assert hasattr(auth, 'validate_credentials')
        assert hasattr(auth, 'refresh_token')
        assert hasattr(auth, '_generate_signature')
        
        # Test inherited methods work
        assert auth.validate_credentials() is True
        assert auth.refresh_token() is True
        assert auth.get_bearer_token() is None