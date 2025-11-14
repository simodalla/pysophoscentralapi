"""Authentication and token management for Sophos Central APIs.

This module handles OAuth2 authentication, token acquisition, refresh,
and caching for Sophos Central APIs.
"""

import asyncio
from abc import ABC, abstractmethod

import httpx

from pysophoscentralapi.core.config import AuthConfig
from pysophoscentralapi.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    TokenExpiredError,
    TokenRefreshError,
)
from pysophoscentralapi.core.models import Token, TokenResponse, WhoAmIResponse


class AuthProvider(ABC):
    """Abstract base class for authentication providers.

    This defines the interface that all authentication providers must implement.
    """

    @abstractmethod
    async def get_token(self) -> Token:
        """Get a valid access token.

        Returns:
            Token instance

        Raises:
            AuthenticationError: If authentication fails
        """

    @abstractmethod
    async def get_authorization_header(self) -> dict[str, str]:
        """Get authorization header for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            AuthenticationError: If token acquisition fails
        """

    @abstractmethod
    async def whoami(self) -> WhoAmIResponse:
        """Get organization/partner information and data region.

        Returns:
            WhoAmI response with API URLs

        Raises:
            AuthenticationError: If request fails
        """


class OAuth2ClientCredentials(AuthProvider):
    """OAuth2 client credentials authentication provider.

    This provider implements the OAuth2 client credentials flow for
    Sophos Central APIs. It handles token acquisition, caching, and
    automatic refresh.

    Attributes:
        config: Authentication configuration
        token_endpoint: OAuth2 token endpoint URL
        whoami_endpoint: Whoami endpoint URL
        timeout: Request timeout in seconds
    """

    TOKEN_ENDPOINT = "https://id.sophos.com/api/v2/oauth2/token"
    WHOAMI_ENDPOINT = "https://api.central.sophos.com/whoami/v1"

    def __init__(
        self,
        config: AuthConfig,
        timeout: int = 30,
    ) -> None:
        """Initialize the authentication provider.

        Args:
            config: Authentication configuration
            timeout: Request timeout in seconds
        """
        self.config = config
        self.timeout = timeout
        self._token: Token | None = None
        self._token_lock = asyncio.Lock()
        self._whoami_cache: WhoAmIResponse | None = None

    async def get_token(self) -> Token:
        """Get a valid access token.

        This method returns a cached token if available and valid,
        otherwise acquires a new token from the OAuth2 endpoint.

        Returns:
            Valid Token instance

        Raises:
            InvalidCredentialsError: If credentials are invalid
            TokenRefreshError: If token acquisition fails
        """
        async with self._token_lock:
            # Return cached token if valid
            if self._token and not self._token.expires_soon():
                return self._token

            # Acquire new token
            self._token = await self._acquire_token()
            return self._token

    async def _acquire_token(self) -> Token:
        """Acquire a new access token from OAuth2 endpoint.

        Returns:
            New Token instance

        Raises:
            InvalidCredentialsError: If credentials are invalid
            TokenRefreshError: If token acquisition fails
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.TOKEN_ENDPOINT,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "scope": "token",
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code == 401:
                    msg = "Invalid client credentials"
                    raise InvalidCredentialsError(
                        msg,
                        status_code=response.status_code,
                    )

                if response.status_code != 200:
                    msg = f"Token acquisition failed: {response.text}"
                    raise TokenRefreshError(
                        msg,
                        status_code=response.status_code,
                    )

                token_data = response.json()
                token_response = TokenResponse(**token_data)
                return Token.from_response(token_response)

            except httpx.HTTPError as e:
                msg = f"Token acquisition failed: {e}"
                raise TokenRefreshError(msg) from e

    async def get_authorization_header(self) -> dict[str, str]:
        """Get authorization header for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            AuthenticationError: If token acquisition fails
        """
        token = await self.get_token()
        return token.get_authorization_header()

    async def refresh_token(self) -> Token:
        """Force refresh of the access token.

        Returns:
            New Token instance

        Raises:
            TokenRefreshError: If token refresh fails
        """
        async with self._token_lock:
            self._token = await self._acquire_token()
            return self._token

    async def whoami(self) -> WhoAmIResponse:
        """Get organization/partner information and data region.

        This method calls the whoami endpoint to determine the appropriate
        data region API URL. Results are cached.

        Returns:
            WhoAmI response with API URLs

        Raises:
            AuthenticationError: If request fails
        """
        # Return cached response if available
        if self._whoami_cache:
            return self._whoami_cache

        headers = await self.get_authorization_header()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    self.WHOAMI_ENDPOINT,
                    headers=headers,
                )

                if response.status_code == 401:
                    msg = "Authentication failed for whoami"
                    raise TokenExpiredError(
                        msg,
                        status_code=response.status_code,
                    )

                if response.status_code != 200:
                    msg = f"Whoami request failed: {response.text}"
                    raise AuthenticationError(
                        msg,
                        status_code=response.status_code,
                    )

                data = response.json()
                # Parse nested structure
                whoami_response = WhoAmIResponse(
                    id=data["id"],
                    idType=data["idType"],
                    **{
                        "apiHosts.global": data["apiHosts"]["global"],
                        "apiHosts.dataRegion": data["apiHosts"]["dataRegion"],
                    },
                )

                self._whoami_cache = whoami_response
                return whoami_response

            except httpx.HTTPError as e:
                msg = f"Whoami request failed: {e}"
                raise AuthenticationError(msg) from e

    def clear_cache(self) -> None:
        """Clear cached token and whoami response.

        Useful for testing or when credentials change.
        """
        self._token = None
        self._whoami_cache = None
