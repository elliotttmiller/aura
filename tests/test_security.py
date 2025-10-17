"""
Tests for security module
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.security import (
    SecurityConfig,
    RateLimiter,
    InputValidator,
)


class TestSecurityConfig:
    """Test SecurityConfig class"""
    
    def test_generate_api_key(self):
        """Test API key generation"""
        key1 = SecurityConfig.generate_api_key()
        key2 = SecurityConfig.generate_api_key()
        
        assert len(key1) > 20
        assert len(key2) > 20
        assert key1 != key2  # Should be unique
    
    def test_hash_api_key(self):
        """Test API key hashing"""
        key = "test_api_key_123"
        hash1 = SecurityConfig.hash_api_key(key)
        hash2 = SecurityConfig.hash_api_key(key)
        
        assert hash1 == hash2  # Same input = same hash
        assert len(hash1) == 64  # SHA-256 produces 64 hex characters
    
    def test_validate_prompt_length(self):
        """Test prompt length validation"""
        short_prompt = "create a ring"
        valid, error = SecurityConfig.validate_prompt(short_prompt)
        assert valid is True
        assert error is None
        
        long_prompt = "x" * (SecurityConfig.MAX_PROMPT_LENGTH + 1)
        valid, error = SecurityConfig.validate_prompt(long_prompt)
        assert valid is False
        assert error is not None
    
    def test_validate_prompt_dangerous_content(self):
        """Test detection of dangerous content in prompts"""
        dangerous_prompts = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "onerror=alert(1)",
            "onclick=alert(1)"
        ]
        
        for prompt in dangerous_prompts:
            valid, error = SecurityConfig.validate_prompt(prompt)
            assert valid is False
            assert "dangerous" in error.lower()
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        # Path traversal attempts
        assert SecurityConfig.sanitize_filename("../../etc/passwd") == "etcpasswd"
        assert SecurityConfig.sanitize_filename("test/../file.txt") == "test_file.txt"
        
        # Normal filenames should be unchanged
        assert SecurityConfig.sanitize_filename("normal_file.glb") == "normal_file.glb"


class TestRateLimiter:
    """Test RateLimiter class"""
    
    def test_rate_limiter_basic(self):
        """Test basic rate limiting"""
        limiter = RateLimiter(requests_per_minute=5)
        client_id = "test_client_1"
        
        # First 5 requests should pass
        for _ in range(5):
            assert limiter.is_rate_limited(client_id) is False
        
        # 6th request should be rate limited
        assert limiter.is_rate_limited(client_id) is True
    
    def test_rate_limiter_different_clients(self):
        """Test that different clients have independent limits"""
        limiter = RateLimiter(requests_per_minute=5)
        
        # Client 1 makes 5 requests
        for _ in range(5):
            assert limiter.is_rate_limited("client_1") is False
        
        # Client 2 should still be able to make requests
        assert limiter.is_rate_limited("client_2") is False
    
    def test_get_remaining_requests(self):
        """Test getting remaining request count"""
        limiter = RateLimiter(requests_per_minute=5)
        client_id = "test_client"
        
        # Initially should have full quota
        assert limiter.get_remaining_requests(client_id) == 5
        
        # After 3 requests, should have 2 remaining
        for _ in range(3):
            limiter.is_rate_limited(client_id)
        
        assert limiter.get_remaining_requests(client_id) == 2


class TestInputValidator:
    """Test InputValidator class"""
    
    def test_validate_session_id(self):
        """Test session ID validation"""
        # Valid IDs
        assert InputValidator.validate_session_id("abc123") is True
        assert InputValidator.validate_session_id("test-session_123") is True
        
        # Invalid IDs
        assert InputValidator.validate_session_id("") is False
        assert InputValidator.validate_session_id("../../../etc") is False
        assert InputValidator.validate_session_id("test session") is False  # spaces
        assert InputValidator.validate_session_id("x" * 101) is False  # too long
    
    def test_validate_object_id(self):
        """Test object ID validation"""
        assert InputValidator.validate_object_id("obj-123") is True
        assert InputValidator.validate_object_id("") is False
    
    def test_validate_material_data(self):
        """Test material data validation"""
        # Valid material data
        valid_material = {
            "roughness": 0.5,
            "metallic": 1.0
        }
        valid, error = InputValidator.validate_material_data(valid_material)
        assert valid is True
        assert error is None
        
        # Invalid roughness (out of range)
        invalid_material = {
            "roughness": 1.5  # Should be 0-1
        }
        valid, error = InputValidator.validate_material_data(invalid_material)
        assert valid is False
        assert error is not None
        
        # Invalid type
        invalid_material = {
            "roughness": "high"  # Should be number
        }
        valid, error = InputValidator.validate_material_data(invalid_material)
        assert valid is False
        assert error is not None
    
    def test_validate_transform_data(self):
        """Test transform data validation"""
        # Valid transform data
        valid_transform = {
            "position": [0.0, 1.0, 2.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0]
        }
        valid, error = InputValidator.validate_transform_data(valid_transform)
        assert valid is True
        assert error is None
        
        # Invalid array length
        invalid_transform = {
            "position": [0.0, 1.0]  # Should have 3 values
        }
        valid, error = InputValidator.validate_transform_data(invalid_transform)
        assert valid is False
        assert error is not None
        
        # Invalid value type
        invalid_transform = {
            "position": ["x", "y", "z"]  # Should be numbers
        }
        valid, error = InputValidator.validate_transform_data(invalid_transform)
        assert valid is False
        assert error is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
