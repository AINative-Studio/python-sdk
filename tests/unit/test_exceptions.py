"""
Unit tests for the exceptions module.
"""

import pytest
from ainative.exceptions import (
    AINativeException,
    AuthenticationError,
    APIError,
    NetworkError,
    ValidationError,
    RateLimitError,
    ResourceNotFoundError,
    TimeoutError
)


class TestAINativeException:
    """Test base AINativeException class."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = AINativeException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.error_code is None
        assert exc.details == {}
    
    def test_exception_with_error_code(self):
        """Test exception with error code."""
        exc = AINativeException("Test error", error_code="TEST_001")
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_001"
        assert exc.details == {}
    
    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"field": "test", "value": 123}
        exc = AINativeException("Test error", details=details)
        assert exc.message == "Test error"
        assert exc.error_code is None
        assert exc.details == details
    
    def test_exception_full_params(self):
        """Test exception with all parameters."""
        details = {"key": "value", "count": 5}
        exc = AINativeException(
            "Full error",
            error_code="FULL_001",
            details=details
        )
        assert exc.message == "Full error"
        assert exc.error_code == "FULL_001"
        assert exc.details == details
    
    def test_exception_inheritance(self):
        """Test that AINativeException inherits from Exception."""
        exc = AINativeException("Test")
        assert isinstance(exc, Exception)
    
    def test_exception_raise_and_catch(self):
        """Test raising and catching the exception."""
        with pytest.raises(AINativeException) as exc_info:
            raise AINativeException("Raised error", error_code="RAISE_001")
        
        assert exc_info.value.message == "Raised error"
        assert exc_info.value.error_code == "RAISE_001"


class TestAuthenticationError:
    """Test AuthenticationError class."""
    
    def test_default_message(self):
        """Test default error message."""
        exc = AuthenticationError()
        assert exc.message == "Authentication failed"
        assert exc.error_code == "AUTH_ERROR"
    
    def test_custom_message(self):
        """Test custom error message."""
        exc = AuthenticationError("Invalid API key")
        assert exc.message == "Invalid API key"
        assert exc.error_code == "AUTH_ERROR"
    
    def test_inheritance(self):
        """Test inheritance from AINativeException."""
        exc = AuthenticationError()
        assert isinstance(exc, AINativeException)
        assert isinstance(exc, Exception)
    
    def test_raise_authentication_error(self):
        """Test raising AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Token expired")
        
        assert "Token expired" in str(exc_info.value)
        assert exc_info.value.error_code == "AUTH_ERROR"


class TestAPIError:
    """Test APIError class."""
    
    def test_basic_api_error(self):
        """Test basic API error."""
        exc = APIError("API request failed")
        assert exc.message == "API request failed"
        assert exc.error_code == "API_ERROR"
        assert exc.status_code is None
        assert exc.response_body is None
    
    def test_api_error_with_status(self):
        """Test API error with status code."""
        exc = APIError("Not found", status_code=404)
        assert exc.message == "Not found"
        assert exc.status_code == 404
        assert exc.response_body is None
    
    def test_api_error_with_response(self):
        """Test API error with response body."""
        response = '{"error": "Invalid request"}'
        exc = APIError("Bad request", status_code=400, response_body=response)
        assert exc.message == "Bad request"
        assert exc.status_code == 400
        assert exc.response_body == response
    
    def test_api_error_full_params(self):
        """Test API error with all parameters."""
        exc = APIError(
            "Server error",
            status_code=500,
            response_body='{"detail": "Internal error"}'
        )
        assert exc.message == "Server error"
        assert exc.error_code == "API_ERROR"
        assert exc.status_code == 500
        assert exc.response_body == '{"detail": "Internal error"}'
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = APIError("Test")
        assert isinstance(exc, AINativeException)


class TestNetworkError:
    """Test NetworkError class."""
    
    def test_default_message(self):
        """Test default error message."""
        exc = NetworkError()
        assert exc.message == "Network error occurred"
        assert exc.error_code == "NETWORK_ERROR"
    
    def test_custom_message(self):
        """Test custom error message."""
        exc = NetworkError("Connection timeout")
        assert exc.message == "Connection timeout"
        assert exc.error_code == "NETWORK_ERROR"
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = NetworkError()
        assert isinstance(exc, AINativeException)


class TestValidationError:
    """Test ValidationError class."""
    
    def test_basic_validation_error(self):
        """Test basic validation error."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field is None
    
    def test_validation_error_with_field(self):
        """Test validation error with field name."""
        exc = ValidationError("Required field", field="email")
        assert exc.message == "Required field"
        assert exc.field == "email"
        assert exc.error_code == "VALIDATION_ERROR"
    
    def test_field_validation_context(self):
        """Test field validation with context."""
        exc = ValidationError(
            "Invalid format",
            field="phone_number"
        )
        assert exc.message == "Invalid format"
        assert exc.field == "phone_number"
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = ValidationError("Test")
        assert isinstance(exc, AINativeException)


class TestRateLimitError:
    """Test RateLimitError class."""
    
    def test_default_message(self):
        """Test default error message."""
        exc = RateLimitError()
        assert exc.message == "Rate limit exceeded"
        assert exc.error_code == "RATE_LIMIT"
        assert exc.retry_after is None
    
    def test_custom_message(self):
        """Test custom error message."""
        exc = RateLimitError("Too many requests")
        assert exc.message == "Too many requests"
        assert exc.retry_after is None
    
    def test_with_retry_after(self):
        """Test with retry_after parameter."""
        exc = RateLimitError("Rate limited", retry_after=60)
        assert exc.message == "Rate limited"
        assert exc.retry_after == 60
        assert exc.error_code == "RATE_LIMIT"
    
    def test_retry_after_seconds(self):
        """Test various retry_after values."""
        exc1 = RateLimitError(retry_after=30)
        assert exc1.retry_after == 30
        
        exc2 = RateLimitError(retry_after=3600)
        assert exc2.retry_after == 3600
        
        exc3 = RateLimitError(retry_after=0)
        assert exc3.retry_after == 0
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = RateLimitError()
        assert isinstance(exc, AINativeException)


class TestResourceNotFoundError:
    """Test ResourceNotFoundError class."""
    
    def test_resource_not_found(self):
        """Test resource not found error."""
        exc = ResourceNotFoundError("project", "proj_123")
        assert exc.message == "project with ID proj_123 not found"
        assert exc.error_code == "NOT_FOUND"
        assert exc.resource_type == "project"
        assert exc.resource_id == "proj_123"
    
    def test_different_resource_types(self):
        """Test with different resource types."""
        exc1 = ResourceNotFoundError("user", "user_456")
        assert exc1.message == "user with ID user_456 not found"
        assert exc1.resource_type == "user"
        assert exc1.resource_id == "user_456"
        
        exc2 = ResourceNotFoundError("vector", "vec_789")
        assert exc2.message == "vector with ID vec_789 not found"
        assert exc2.resource_type == "vector"
        assert exc2.resource_id == "vec_789"
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = ResourceNotFoundError("test", "123")
        assert isinstance(exc, AINativeException)
    
    def test_raise_not_found(self):
        """Test raising ResourceNotFoundError."""
        with pytest.raises(ResourceNotFoundError) as exc_info:
            raise ResourceNotFoundError("memory", "mem_xyz")
        
        assert "memory with ID mem_xyz not found" in str(exc_info.value)
        assert exc_info.value.resource_type == "memory"
        assert exc_info.value.resource_id == "mem_xyz"


class TestTimeoutError:
    """Test TimeoutError class."""
    
    def test_default_message(self):
        """Test default error message."""
        exc = TimeoutError()
        assert exc.message == "Operation timed out"
        assert exc.error_code == "TIMEOUT"
    
    def test_custom_message(self):
        """Test custom error message."""
        exc = TimeoutError("Request timeout after 30s")
        assert exc.message == "Request timeout after 30s"
        assert exc.error_code == "TIMEOUT"
    
    def test_inheritance(self):
        """Test inheritance."""
        exc = TimeoutError()
        assert isinstance(exc, AINativeException)
    
    def test_timeout_scenarios(self):
        """Test various timeout scenarios."""
        exc1 = TimeoutError("Connection timeout")
        assert "Connection" in exc1.message
        
        exc2 = TimeoutError("Read timeout")
        assert "Read" in exc2.message
        
        exc3 = TimeoutError("Write timeout")
        assert "Write" in exc3.message


class TestExceptionHierarchy:
    """Test the exception hierarchy and relationships."""
    
    def test_all_inherit_from_base(self):
        """Test that all exceptions inherit from AINativeException."""
        exceptions = [
            AuthenticationError(),
            APIError("test"),
            NetworkError(),
            ValidationError("test"),
            RateLimitError(),
            ResourceNotFoundError("test", "123"),
            TimeoutError()
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AINativeException)
            assert isinstance(exc, Exception)
            assert hasattr(exc, 'message')
            assert hasattr(exc, 'error_code')
            assert hasattr(exc, 'details')
    
    def test_exception_catching_hierarchy(self):
        """Test catching exceptions at different levels."""
        # Can catch specific exception
        with pytest.raises(AuthenticationError):
            raise AuthenticationError()
        
        # Can catch as AINativeException
        with pytest.raises(AINativeException):
            raise APIError("test")
        
        # Can catch as Exception
        with pytest.raises(Exception):
            raise NetworkError()
    
    def test_error_codes_unique(self):
        """Test that each exception type has a unique error code."""
        error_codes = {
            AuthenticationError().error_code,
            APIError("test").error_code,
            NetworkError().error_code,
            ValidationError("test").error_code,
            RateLimitError().error_code,
            ResourceNotFoundError("test", "123").error_code,
            TimeoutError().error_code
        }
        
        # All error codes should be unique
        assert len(error_codes) == 7
        
        # All should be non-None
        assert None not in error_codes