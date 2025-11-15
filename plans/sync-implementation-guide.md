# Sync Wrapper Implementation Guide

This document provides detailed guidance on implementing synchronous wrappers around the async core functionality.

## Overview

PySophosCentralApi uses an **async-first, sync-wrapper** pattern:
- All core functionality is implemented asynchronously
- Synchronous wrappers provide blocking interface by calling `asyncio.run()`
- Single source of truth (async code) reduces maintenance burden

## Implementation Pattern

### Basic Wrapper Template

```python
# src/pysophoscentralapi/sync/base.py
import asyncio
from typing import TypeVar, Coroutine, Any

T = TypeVar("T")


class SyncWrapper:
    """Base class for sync wrappers around async objects."""

    def __init__(self, async_obj: Any) -> None:
        """Initialize wrapper with async object.

        Args:
            async_obj: The async object to wrap
        """
        self._async_obj = async_obj

    def _run_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Execute an async coroutine synchronously.

        Args:
            coro: Coroutine to execute

        Returns:
            Result of the coroutine

        Raises:
            Any exception raised by the coroutine
        """
        return asyncio.run(coro)
```

### HTTP Client Wrapper

```python
# src/pysophoscentralapi/sync/client.py
from typing import Any

from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.sync.base import SyncWrapper


class HTTPClientSync(SyncWrapper):
    """Synchronous wrapper for HTTPClient.

    This provides a blocking interface to the async HTTPClient.

    Example:
        >>> client = HTTPClientSync(base_url, auth_provider_sync)
        >>> response = client.get("/endpoint/v1/endpoints")  # Blocking call
    """

    def __init__(self, *args, **kwargs):
        """Initialize sync HTTP client."""
        # Create async client
        async_client = HTTPClient(*args, **kwargs)
        super().__init__(async_client)

    @property
    def _client(self) -> HTTPClient:
        """Get underlying async client."""
        return self._async_obj

    def request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous HTTP request.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            json: JSON body
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return self._run_async(
            self._client.request(method, endpoint, params, json, headers)
        )

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous GET request."""
        return self._run_async(self._client.get(endpoint, params, headers))

    def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous POST request."""
        return self._run_async(self._client.post(endpoint, json, headers))

    def patch(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous PATCH request."""
        return self._run_async(self._client.patch(endpoint, json, headers))

    def delete(
        self,
        endpoint: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a synchronous DELETE request."""
        return self._run_async(self._client.delete(endpoint, headers))

    def __enter__(self):
        """Enter context manager."""
        self._run_async(self._client.__aenter__())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self._run_async(self._client.__aexit__(exc_type, exc_val, exc_tb))

    def close(self) -> None:
        """Close the client."""
        self._run_async(self._client.close())
```

### Auth Provider Wrapper

```python
# src/pysophoscentralapi/sync/auth.py
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.config import AuthConfig
from pysophoscentralapi.core.models import Token, WhoAmIResponse
from pysophoscentralapi.sync.base import SyncWrapper


class OAuth2ClientCredentialsSync(SyncWrapper):
    """Synchronous wrapper for OAuth2ClientCredentials.

    Example:
        >>> auth = OAuth2ClientCredentialsSync(config)
        >>> token = auth.get_token()  # Blocking call
    """

    def __init__(self, config: AuthConfig, timeout: int = 30) -> None:
        """Initialize sync auth provider."""
        async_auth = OAuth2ClientCredentials(config, timeout)
        super().__init__(async_auth)

    @property
    def _auth(self) -> OAuth2ClientCredentials:
        """Get underlying async auth provider."""
        return self._async_obj

    def get_token(self) -> Token:
        """Get a valid access token synchronously."""
        return self._run_async(self._auth.get_token())

    def get_authorization_header(self) -> dict[str, str]:
        """Get authorization header synchronously."""
        return self._run_async(self._auth.get_authorization_header())

    def refresh_token(self) -> Token:
        """Force refresh the access token synchronously."""
        return self._run_async(self._auth.refresh_token())

    def whoami(self) -> WhoAmIResponse:
        """Get organization/partner info synchronously."""
        return self._run_async(self._auth.whoami())

    def clear_cache(self) -> None:
        """Clear cached token and whoami response."""
        self._auth.clear_cache()
```

### Paginator Wrapper

```python
# src/pysophoscentralapi/sync/pagination.py
from collections.abc import Iterator
from typing import TypeVar, Callable

from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.core.pagination import Paginator
from pysophoscentralapi.sync.base import SyncWrapper

T = TypeVar("T")


class PaginatorSync(SyncWrapper):
    """Synchronous wrapper for Paginator.

    Example:
        >>> paginator = PaginatorSync(fetch_fn, page_size=100)
        >>> for item in paginator.iter_items():  # Blocking iteration
        ...     print(item)
    """

    def __init__(
        self,
        fetch_page: Callable[[str | None], PaginatedResponse[T]],
        page_size: int = 50,
        max_pages: int | None = None,
    ) -> None:
        """Initialize sync paginator."""
        async_paginator = Paginator(fetch_page, page_size, max_pages)
        super().__init__(async_paginator)

    @property
    def _paginator(self) -> Paginator:
        """Get underlying async paginator."""
        return self._async_obj

    def iter_pages(self) -> Iterator[PaginatedResponse[T]]:
        """Iterate over pages synchronously.

        Yields:
            PaginatedResponse for each page
        """
        # Convert async iterator to sync iterator
        async_iter = self._paginator.iter_pages()

        while True:
            try:
                page = self._run_async(async_iter.__anext__())
                yield page
            except StopAsyncIteration:
                break

    def iter_items(self) -> Iterator[T]:
        """Iterate over individual items synchronously.

        Yields:
            Individual items from all pages
        """
        for page in self.iter_pages():
            yield from page.items

    def get_all(self, max_items: int | None = None) -> list[T]:
        """Fetch all items synchronously.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of all items
        """
        return self._run_async(self._paginator.get_all(max_items))

    def get_first_page(self) -> PaginatedResponse[T]:
        """Fetch only the first page synchronously."""
        return self._run_async(self._paginator.get_first_page())

    def reset(self) -> None:
        """Reset pagination state."""
        self._paginator.reset()
```

## Testing Strategy

### Test Async Implementation Thoroughly

```python
# tests/unit/test_core/test_client.py
@pytest.mark.asyncio
async def test_http_client_get():
    """Test async HTTP client GET request."""
    client = HTTPClient(...)
    response = await client.get("/endpoint")
    assert response["data"] == "expected"
```

### Test Sync Wrappers Lightly

```python
# tests/unit/test_sync/test_client.py
def test_http_client_sync_get():
    """Test sync HTTP client GET request."""
    client = HTTPClientSync(...)
    response = client.get("/endpoint")  # No await
    assert response["data"] == "expected"
```

Focus on:
- Context manager behavior (`with` statement)
- Error propagation
- Basic functionality parity

Don't duplicate all async tests for sync - just verify wrapper works.

## CLI Integration

### Global Sync Flag

```python
# src/pysophoscentralapi/cli/main.py
import click

@click.group()
@click.option("--sync", is_flag=True, help="Use synchronous mode")
@click.pass_context
def cli(ctx, sync):
    """PySophos - Sophos Central API CLI"""
    ctx.ensure_object(dict)
    ctx.obj["sync_mode"] = sync
```

### Command Implementation

```python
# src/pysophoscentralapi/cli/endpoint_cmds.py
@endpoint.command("list")
@click.pass_context
def list_endpoints(ctx):
    """List endpoints."""
    if ctx.obj["sync_mode"]:
        # Use sync client
        with SophosClientSync(config) as client:
            endpoints = client.endpoint.list_endpoints()
    else:
        # Use async client (default)
        import asyncio
        async def main():
            async with SophosClient(config) as client:
                return await client.endpoint.list_endpoints()
        endpoints = asyncio.run(main())
    
    # Display endpoints
    display_endpoints(endpoints)
```

## Best Practices

### DO:
✅ Implement all functionality async-first
✅ Use thin wrappers that just call `asyncio.run()`
✅ Support both context managers (`async with` and `with`)
✅ Document both usage patterns in examples
✅ Recommend async for performance-critical use cases
✅ Keep wrapper code simple and maintainable

### DON'T:
❌ Duplicate business logic in sync wrappers
❌ Make sync wrappers complex
❌ Test every async feature in sync mode
❌ Hide async nature - be transparent about it
❌ Use sync wrappers for concurrent operations
❌ Forget to handle context managers properly

## Implementation Checklist

Phase 1 (Foundation):
- [ ] Create `sync/` module structure
- [ ] Implement `SyncWrapper` base class
- [ ] Create `HTTPClientSync` wrapper
- [ ] Create `OAuth2ClientCredentialsSync` wrapper
- [ ] Create `PaginatorSync` wrapper
- [ ] Add basic tests for sync wrappers

Phase 2-3 (API Clients):
- [ ] Wrap Endpoint API client
- [ ] Wrap Common API client
- [ ] Test sync API client wrappers

Phase 4 (CLI):
- [ ] Add `--sync` global flag
- [ ] Update all commands to support sync mode
- [ ] Test CLI in both modes

## Module Structure

```
src/pysophoscentralapi/
├── core/              # Async implementations (primary)
│   ├── client.py
│   ├── auth.py
│   ├── pagination.py
│   └── ...
├── sync/              # Sync wrappers
│   ├── __init__.py
│   ├── base.py        # SyncWrapper base class
│   ├── client.py      # HTTPClientSync
│   ├── auth.py        # OAuth2ClientCredentialsSync
│   └── pagination.py  # PaginatorSync
└── api/
    ├── endpoint/      # Async API (will have sync wrapper)
    └── common/        # Async API (will have sync wrapper)
```

## Documentation Examples

Show both patterns in README and docs:

```python
# Async (recommended for scripts with concurrent operations)
import asyncio
from pysophoscentralapi import SophosClient

async def main():
    async with SophosClient(config) as client:
        endpoints = await client.endpoint.list_endpoints()
        alerts = await client.alerts.list_alerts()

asyncio.run(main())

# Sync (recommended for simple scripts and interactive use)
from pysophoscentralapi.sync import SophosClientSync

with SophosClientSync(config) as client:
    endpoints = client.endpoint.list_endpoints()
    alerts = client.alerts.list_alerts()
```

---

This guide ensures consistent, maintainable sync wrapper implementation across the project.

