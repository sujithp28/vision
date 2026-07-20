"""Shared exception hierarchy for VisionForge"""


class VisionForgeException(Exception):
    """Base exception for all VisionForge errors"""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or "INTERNAL_ERROR"
        super().__init__(self.message)


class ConfigurationError(VisionForgeException):
    """Raised when configuration is invalid"""
    code = "CONFIG_ERROR"


class ProviderError(VisionForgeException):
    """Raised when AI provider operation fails"""
    code = "PROVIDER_ERROR"


class DatabaseError(VisionForgeException):
    """Raised when database operation fails"""
    code = "DATABASE_ERROR"


class AuthenticationError(VisionForgeException):
    """Raised when authentication fails"""
    code = "AUTH_ERROR"


class AuthorizationError(VisionForgeException):
    """Raised when authorization fails"""
    code = "AUTHZ_ERROR"


class NotFoundError(VisionForgeException):
    """Raised when resource not found"""
    code = "NOT_FOUND"


class ValidationError(VisionForgeException):
    """Raised when validation fails"""
    code = "VALIDATION_ERROR"


class RateLimitError(VisionForgeException):
    """Raised when rate limit exceeded"""
    code = "RATE_LIMIT"
