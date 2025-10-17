"""
Tests for exceptions module
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi import status
from backend.exceptions import (
    AuraException,
    SessionNotFoundError,
    SessionCreationError,
    ObjectNotFoundError,
    AIConnectionError,
    ValidationError,
    RateLimitError,
)


class TestExceptions:
    """Test custom exception classes"""
    
    def test_aura_exception_base(self):
        """Test base AuraException"""
        exc = AuraException(
            message="Test error",
            details={"key": "value"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
        
        assert exc.message == "Test error"
        assert exc.details == {"key": "value"}
        assert exc.status_code == 400
        assert str(exc) == "Test error"
    
    def test_aura_exception_to_dict(self):
        """Test exception to dictionary conversion"""
        exc = AuraException(
            message="Test error",
            details={"field": "test"}
        )
        
        result = exc.to_dict()
        assert result["error"] == "AuraException"
        assert result["message"] == "Test error"
        assert result["details"]["field"] == "test"
    
    def test_session_not_found_error(self):
        """Test SessionNotFoundError"""
        exc = SessionNotFoundError("session-123")
        
        assert "session-123" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["session_id"] == "session-123"
    
    def test_session_creation_error(self):
        """Test SessionCreationError"""
        exc = SessionCreationError("database connection failed")
        
        assert "database connection failed" in exc.message
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_object_not_found_error(self):
        """Test ObjectNotFoundError"""
        exc = ObjectNotFoundError("obj-123", "session-456")
        
        assert "obj-123" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["object_id"] == "obj-123"
        assert exc.details["session_id"] == "session-456"
    
    def test_ai_connection_error(self):
        """Test AIConnectionError"""
        exc = AIConnectionError("LM Studio")
        
        assert "LM Studio" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.details["service"] == "LM Studio"
    
    def test_validation_error(self):
        """Test ValidationError"""
        exc = ValidationError("prompt", "too long")
        
        assert "prompt" in exc.message
        assert "too long" in exc.message
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.details["field"] == "prompt"
        assert exc.details["reason"] == "too long"
    
    def test_rate_limit_error(self):
        """Test RateLimitError"""
        exc = RateLimitError(retry_after=60)
        
        assert "Rate limit exceeded" in exc.message
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc.details["retry_after_seconds"] == 60
    
    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from AuraException"""
        exceptions = [
            SessionNotFoundError("test"),
            ObjectNotFoundError("obj", "session"),
            AIConnectionError("service"),
            ValidationError("field", "reason"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, AuraException)
            assert hasattr(exc, 'message')
            assert hasattr(exc, 'details')
            assert hasattr(exc, 'status_code')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
