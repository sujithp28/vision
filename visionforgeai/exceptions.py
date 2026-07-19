"""Custom application exceptions."""

from typing import Any, Dict, Optional


class VisionForgeError(Exception):
    """Base exception for VisionForge AI application."""

    def __init__(
        self,
        message: str,
        error_code: str = "InternalServerError",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(VisionForgeError):
    """Exception for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="ValidationError",
            status_code=422,
            details=details,
        )


class AuthenticationError(VisionForgeError):
    """Exception for authentication errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AuthenticationError",
            status_code=401,
            details=details,
        )


class AuthorizationError(VisionForgeError):
    """Exception for authorization errors."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AuthorizationError",
            status_code=403,
            details=details,
        )


class NotFoundError(VisionForgeError):
    """Exception for resource not found errors."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="NotFoundError",
            status_code=404,
            details=details,
        )


class ServiceUnavailableError(VisionForgeError):
    """Exception for service unavailable errors."""

    def __init__(
        self,
        message: str = "Service unavailable",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="ServiceUnavailableError",
            status_code=503,
            details=details,
        )


class ProviderError(VisionForgeError):
    """Exception for LLM provider errors."""

    def __init__(
        self,
        message: str = "LLM provider error",
        provider: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="ProviderError",
            status_code=502,
            details={"provider": provider, **(details or {})},
        )
