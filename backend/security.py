"""
Security Configuration and Middleware
======================================

Centralized security management for Aura Sentient Interactive Studio.
Implements authentication, authorization, rate limiting, and security headers.
"""

from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# API Key Management
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


class SecurityConfig:
    """Centralized security configuration"""
    
    # Session security
    SESSION_TIMEOUT_MINUTES = 60
    MAX_SESSIONS_PER_USER = 5
    
    # Request limits
    MAX_PROMPT_LENGTH = 1000
    MAX_FILE_SIZE_MB = 50
    ALLOWED_FILE_TYPES = {'.glb', '.gltf', '.obj', '.stl', '.3dm'}
    
    # Rate limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE = 60
    RATE_LIMIT_AI_REQUESTS_PER_HOUR = 100
    
    # Content security
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure random API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def validate_prompt(prompt: str) -> tuple[bool, Optional[str]]:
        """Validate user prompt for security issues"""
        if len(prompt) > SecurityConfig.MAX_PROMPT_LENGTH:
            return False, f"Prompt exceeds maximum length of {SecurityConfig.MAX_PROMPT_LENGTH}"
        
        # Check for potentially malicious patterns
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        for pattern in dangerous_patterns:
            if pattern.lower() in prompt.lower():
                return False, "Prompt contains potentially dangerous content"
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        import os
        # Remove any path components
        filename = os.path.basename(filename)
        # Remove potentially dangerous characters
        dangerous_chars = ['..', '/', '\\', '\x00']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        return filename


class SecurityMiddleware(BaseHTTPMiddleware):
    """Custom security middleware for adding security headers"""
    
    async def dispatch(self, request: Request, call_next):
        # Add security headers to all responses
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS for HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' http://localhost:* ws://localhost:*"
        )
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_rate_limited(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return True
        
        # Record this request
        self.requests[client_id].append(now)
        return False
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get number of remaining requests for client"""
        now = time.time()
        minute_ago = now - 60
        
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        return max(0, self.requests_per_minute - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=SecurityConfig.RATE_LIMIT_REQUESTS_PER_MINUTE)


async def validate_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)) -> str:
    """
    Validate API key from request header.
    
    Note: In production, implement proper API key storage and verification.
    For now, this is a placeholder that allows development without keys.
    """
    # In development mode, allow requests without API keys
    # TODO: In production, enforce API key requirement
    if not api_key:
        logger.warning("Request without API key (allowed in development mode)")
        return "development"
    
    # Verify API key (placeholder implementation)
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    return api_key


def is_valid_api_key(key: str) -> bool:
    """
    Verify API key against stored keys.
    
    TODO: Implement proper key verification:
    - Check against database/cache
    - Verify not expired
    - Check usage limits
    - Track key usage statistics
    """
    # Placeholder implementation
    # In production, check against secure storage
    return True


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


async def check_rate_limit(request: Request) -> None:
    """Check if request should be rate limited"""
    client_ip = get_client_ip(request)
    
    if rate_limiter.is_rate_limited(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "Retry-After": "60",
                "X-RateLimit-Remaining": str(remaining)
            }
        )


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """Validate session ID format"""
        # Check length and characters
        if not session_id or len(session_id) > 100:
            return False
        
        # Only allow alphanumeric, hyphens, underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            return False
        
        return True
    
    @staticmethod
    def validate_object_id(object_id: str) -> bool:
        """Validate object ID format"""
        return InputValidator.validate_session_id(object_id)
    
    @staticmethod
    def validate_material_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate material property data"""
        if not isinstance(data, dict):
            return False, "Material data must be a dictionary"
        
        # Validate numeric ranges
        if 'roughness' in data:
            if not isinstance(data['roughness'], (int, float)):
                return False, "Roughness must be a number"
            if not 0 <= data['roughness'] <= 1:
                return False, "Roughness must be between 0 and 1"
        
        if 'metallic' in data:
            if not isinstance(data['metallic'], (int, float)):
                return False, "Metallic must be a number"
            if not 0 <= data['metallic'] <= 1:
                return False, "Metallic must be between 0 and 1"
        
        return True, None
    
    @staticmethod
    def validate_transform_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate transform property data"""
        if not isinstance(data, dict):
            return False, "Transform data must be a dictionary"
        
        # Validate arrays
        for key in ['position', 'rotation', 'scale']:
            if key in data:
                if not isinstance(data[key], list):
                    return False, f"{key} must be an array"
                if len(data[key]) != 3:
                    return False, f"{key} must have exactly 3 values"
                if not all(isinstance(v, (int, float)) for v in data[key]):
                    return False, f"All {key} values must be numbers"
        
        return True, None


# Export commonly used functions
__all__ = [
    'SecurityConfig',
    'SecurityMiddleware',
    'RateLimiter',
    'rate_limiter',
    'validate_api_key',
    'check_rate_limit',
    'get_client_ip',
    'InputValidator'
]
