"""
Custom Exceptions for Aura Sentient Interactive Studio
=======================================================

Provides consistent error handling across the application with
proper HTTP status codes and detailed error messages.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class AuraException(Exception):
    """Base exception for all Aura errors"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class SessionError(AuraException):
    """Base class for session-related errors"""
    pass


class SessionNotFoundError(SessionError):
    """Raised when session ID doesn't exist"""
    
    def __init__(self, session_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Session not found: {session_id}",
            details=details or {"session_id": session_id},
            status_code=status.HTTP_404_NOT_FOUND
        )


class SessionCreationError(SessionError):
    """Raised when session creation fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to create session: {reason}",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class SessionExpiredError(SessionError):
    """Raised when session has expired"""
    
    def __init__(self, session_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Session expired: {session_id}",
            details=details or {"session_id": session_id},
            status_code=status.HTTP_410_GONE
        )


class ObjectError(AuraException):
    """Base class for object-related errors"""
    pass


class ObjectNotFoundError(ObjectError):
    """Raised when object ID doesn't exist in session"""
    
    def __init__(self, object_id: str, session_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Object not found: {object_id}",
            details=details or {"object_id": object_id, "session_id": session_id},
            status_code=status.HTTP_404_NOT_FOUND
        )


class ObjectCreationError(ObjectError):
    """Raised when object creation fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to create object: {reason}",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ObjectUpdateError(ObjectError):
    """Raised when object update fails"""
    
    def __init__(self, object_id: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to update object {object_id}: {reason}",
            details=details or {"object_id": object_id, "reason": reason},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AIServiceError(AuraException):
    """Base class for AI service errors"""
    pass


class AIConnectionError(AIServiceError):
    """Raised when AI service connection fails"""
    
    def __init__(self, service: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to connect to AI service: {service}",
            details=details or {"service": service},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class AIGenerationError(AIServiceError):
    """Raised when AI generation fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI generation failed: {reason}",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class AITimeoutError(AIServiceError):
    """Raised when AI service times out"""
    
    def __init__(self, timeout_seconds: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI service timed out after {timeout_seconds} seconds",
            details=details or {"timeout_seconds": timeout_seconds},
            status_code=status.HTTP_504_GATEWAY_TIMEOUT
        )


class ValidationError(AuraException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation failed for {field}: {reason}",
            details=details or {"field": field, "reason": reason},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AuthenticationError(AuraException):
    """Raised when authentication fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Authentication failed: {reason}",
            details=details,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(AuraException):
    """Raised when authorization fails"""
    
    def __init__(self, action: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Not authorized to perform action: {action}",
            details=details or {"action": action},
            status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitError(AuraException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int = 60, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            details=details or {"retry_after_seconds": retry_after},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class FileError(AuraException):
    """Base class for file operation errors"""
    pass


class FileNotFoundError(FileError):
    """Raised when file doesn't exist"""
    
    def __init__(self, filename: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"File not found: {filename}",
            details=details or {"filename": filename},
            status_code=status.HTTP_404_NOT_FOUND
        )


class FileValidationError(FileError):
    """Raised when file validation fails"""
    
    def __init__(self, filename: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"File validation failed for {filename}: {reason}",
            details=details or {"filename": filename, "reason": reason},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class FileTooLargeError(FileError):
    """Raised when file exceeds size limit"""
    
    def __init__(self, filename: str, size_mb: float, max_size_mb: float):
        super().__init__(
            message=f"File {filename} is too large ({size_mb:.2f}MB). Maximum size is {max_size_mb}MB.",
            details={"filename": filename, "size_mb": size_mb, "max_size_mb": max_size_mb},
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


class BlenderError(AuraException):
    """Base class for Blender-related errors"""
    pass


class BlenderNotFoundError(BlenderError):
    """Raised when Blender executable not found"""
    
    def __init__(self, path: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Blender executable not found at: {path}",
            details=details or {"blender_path": path},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BlenderExecutionError(BlenderError):
    """Raised when Blender execution fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Blender execution failed: {reason}",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class RhinoError(AuraException):
    """Base class for Rhino-related errors"""
    pass


class RhinoConnectionError(RhinoError):
    """Raised when Rhino connection fails"""
    
    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Failed to connect to Rhino engine",
            details=details,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class RhinoExecutionError(RhinoError):
    """Raised when Rhino execution fails"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Rhino execution failed: {reason}",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Exception handlers for FastAPI

async def aura_exception_handler(request, exc: AuraException) -> JSONResponse:
    """Global exception handler for AuraException"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
        headers={
            "X-Error-Type": exc.__class__.__name__
        }
    )


async def generic_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handler for unexpected exceptions"""
    import logging
    logger = logging.getLogger(__name__)
    logger.exception("Unexpected error occurred", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "details": {}
        }
    )


# Export all exceptions and handlers
__all__ = [
    # Base exceptions
    'AuraException',
    
    # Session exceptions
    'SessionError',
    'SessionNotFoundError',
    'SessionCreationError',
    'SessionExpiredError',
    
    # Object exceptions
    'ObjectError',
    'ObjectNotFoundError',
    'ObjectCreationError',
    'ObjectUpdateError',
    
    # AI exceptions
    'AIServiceError',
    'AIConnectionError',
    'AIGenerationError',
    'AITimeoutError',
    
    # Validation exceptions
    'ValidationError',
    
    # Auth exceptions
    'AuthenticationError',
    'AuthorizationError',
    'RateLimitError',
    
    # File exceptions
    'FileError',
    'FileNotFoundError',
    'FileValidationError',
    'FileTooLargeError',
    
    # External service exceptions
    'BlenderError',
    'BlenderNotFoundError',
    'BlenderExecutionError',
    'RhinoError',
    'RhinoConnectionError',
    'RhinoExecutionError',
    
    # Exception handlers
    'aura_exception_handler',
    'generic_exception_handler'
]
