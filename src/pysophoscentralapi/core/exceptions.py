"""Custom exception hierarchy for pysophoscentralapi.

This module defines all custom exceptions used throughout the library,
providing clear error handling with contextual information.
"""

from typing import Any


class SophosAPIException(Exception):
    """Base exception for all Sophos API errors.

    This is the base class for all custom exceptions in the library.
    It provides common attributes for error context.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code if applicable
        error_code: API-specific error code if available
        correlation_id: Correlation ID from API response
        request_id: Request ID from API response
        response_data: Full response data if available
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
        correlation_id: str | None = None,
        request_id: str | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            error_code: API error code
            correlation_id: Correlation ID from response
            request_id: Request ID from response
            response_data: Full response data
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.correlation_id = correlation_id
        self.request_id = request_id
        self.response_data = response_data

    def __str__(self) -> str:
        """Return string representation of the exception."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.error_code:
            parts.append(f"Code: {self.error_code}")
        if self.correlation_id:
            parts.append(f"Correlation ID: {self.correlation_id}")
        return " | ".join(parts)


# Authentication Errors
class AuthenticationError(SophosAPIException):
    """Base exception for authentication-related errors."""


class InvalidCredentialsError(AuthenticationError):
    """Exception raised when credentials are invalid."""


class TokenExpiredError(AuthenticationError):
    """Exception raised when an access token has expired."""


class TokenRefreshError(AuthenticationError):
    """Exception raised when token refresh fails."""


# API Errors
class APIError(SophosAPIException):
    """Base exception for API-related errors."""


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded.

    Attributes:
        retry_after: Number of seconds to wait before retrying
    """

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ResourceNotFoundError(APIError):
    """Exception raised when a requested resource is not found."""


class ValidationError(APIError):
    """Exception raised when request validation fails."""


class PermissionError(APIError):
    """Exception raised when user lacks required permissions."""


class APIResponseError(APIError):
    """Exception raised when API returns an unexpected response."""


# Network Errors
class NetworkError(SophosAPIException):
    """Base exception for network-related errors."""


class TimeoutError(NetworkError):
    """Exception raised when a request times out."""


class ConnectionError(NetworkError):
    """Exception raised when connection to API fails."""


# Configuration Errors
class ConfigurationError(SophosAPIException):
    """Exception raised for configuration-related errors."""


class InvalidConfigError(ConfigurationError):
    """Exception raised when configuration is invalid."""


class MissingConfigError(ConfigurationError):
    """Exception raised when required configuration is missing."""


# Export Errors
class ExportError(SophosAPIException):
    """Base exception for export-related errors."""


class InvalidFormatError(ExportError):
    """Exception raised when export format is invalid."""


class FileWriteError(ExportError):
    """Exception raised when writing export file fails."""


# Pagination Errors
class PaginationError(SophosAPIException):
    """Exception raised for pagination-related errors."""


def create_exception_from_response(
    status_code: int,
    response_data: dict[str, Any] | None = None,
) -> SophosAPIException:
    """Create appropriate exception based on HTTP status code.

    Args:
        status_code: HTTP status code
        response_data: Response data from API

    Returns:
        Appropriate exception instance for the status code

    Example:
        >>> error = create_exception_from_response(404, {"error": "not_found"})
        >>> isinstance(error, ResourceNotFoundError)
        True
    """
    error_message = "Unknown error"
    error_code = None
    correlation_id = None
    request_id = None

    if response_data:
        error_message = response_data.get("message", error_message)
        error_code = response_data.get("error", error_code)
        correlation_id = response_data.get("correlationId", correlation_id)
        request_id = response_data.get("requestId", request_id)

    exception_kwargs = {
        "message": error_message,
        "status_code": status_code,
        "error_code": error_code,
        "correlation_id": correlation_id,
        "request_id": request_id,
        "response_data": response_data,
    }

    # Map status codes to exception types
    if status_code == 400:
        return ValidationError(**exception_kwargs)
    if status_code == 401:
        if error_code in {"invalid_token", "token_expired"}:
            return TokenExpiredError(**exception_kwargs)
        return InvalidCredentialsError(**exception_kwargs)
    if status_code == 403:
        return PermissionError(**exception_kwargs)
    if status_code == 404:
        return ResourceNotFoundError(**exception_kwargs)
    if status_code == 429:
        retry_after = None
        if response_data and "retry_after" in response_data:
            retry_after = response_data["retry_after"]
        return RateLimitError(retry_after=retry_after, **exception_kwargs)
    if status_code >= 500:
        return APIResponseError(**exception_kwargs)

    # Default to generic API error
    return APIError(**exception_kwargs)
