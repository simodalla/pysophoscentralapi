"""Tests for exception handling."""


from pysophoscentralapi.core import exceptions


class TestSophosAPIException:
    """Tests for base SophosAPIException."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = exceptions.SophosAPIException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.status_code is None

    def test_exception_with_details(self):
        """Test exception with all details."""
        exc = exceptions.SophosAPIException(
            message="Test error",
            status_code=400,
            error_code="bad_request",
            correlation_id="corr-123",
            request_id="req-456",
        )
        assert "Test error" in str(exc)
        assert "400" in str(exc)
        assert "bad_request" in str(exc)
        assert exc.correlation_id == "corr-123"


class TestAuthenticationErrors:
    """Tests for authentication-related exceptions."""

    def test_invalid_credentials_error(self):
        """Test InvalidCredentialsError."""
        exc = exceptions.InvalidCredentialsError("Bad credentials", status_code=401)
        assert isinstance(exc, exceptions.AuthenticationError)
        assert exc.status_code == 401

    def test_token_expired_error(self):
        """Test TokenExpiredError."""
        exc = exceptions.TokenExpiredError("Token expired")
        assert isinstance(exc, exceptions.AuthenticationError)


class TestAPIErrors:
    """Tests for API-related exceptions."""

    def test_rate_limit_error(self):
        """Test RateLimitError with retry_after."""
        exc = exceptions.RateLimitError("Rate limited", retry_after=60)
        assert exc.retry_after == 60
        assert isinstance(exc, exceptions.APIError)

    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        exc = exceptions.ResourceNotFoundError("Not found", status_code=404)
        assert exc.status_code == 404


class TestExceptionFactory:
    """Tests for exception factory function."""

    def test_create_validation_error(self):
        """Test creating ValidationError from 400 status."""
        exc = exceptions.create_exception_from_response(
            400,
            {"message": "Invalid input", "error": "validation_error"},
        )
        assert isinstance(exc, exceptions.ValidationError)
        assert exc.status_code == 400
        assert exc.error_code == "validation_error"

    def test_create_auth_error(self):
        """Test creating authentication error from 401 status."""
        exc = exceptions.create_exception_from_response(
            401,
            {"message": "Unauthorized", "error": "invalid_token"},
        )
        assert isinstance(exc, exceptions.TokenExpiredError)

    def test_create_not_found_error(self):
        """Test creating not found error from 404 status."""
        exc = exceptions.create_exception_from_response(404)
        assert isinstance(exc, exceptions.ResourceNotFoundError)

    def test_create_rate_limit_error(self):
        """Test creating rate limit error from 429 status."""
        exc = exceptions.create_exception_from_response(
            429,
            {"message": "Too many requests", "retry_after": 30},
        )
        assert isinstance(exc, exceptions.RateLimitError)
        assert exc.retry_after == 30

    def test_create_server_error(self):
        """Test creating server error from 500 status."""
        exc = exceptions.create_exception_from_response(500)
        assert isinstance(exc, exceptions.APIResponseError)
