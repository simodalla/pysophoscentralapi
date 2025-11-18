# API Reference

Complete API reference for PySophosCentralApi library components.

## Module Overview

| Module | Description |
|--------|-------------|
| [Core](core.md) | HTTP client, authentication, configuration, exceptions |
| [Endpoint API](endpoint.md) | Endpoint management operations |
| [Common API](common.md) | Alerts, tenants, admins, roles |
| [Filters](filters.md) | Query builders, sorting, pagination |
| [Exporters](exporters.md) | JSON and CSV export utilities |
| [Sync](sync.md) | Synchronous wrappers for async APIs |

## Quick Reference

### Core Modules

```python
from pysophoscentralapi.core import (
    Config,                  # Configuration management
    HTTPClient,             # Async HTTP client
    OAuth2ClientCredentials, # Authentication
    SophosAPIException,     # Base exception
)
```

###  API Clients

```python
# Endpoint API
from pysophoscentralapi.api.endpoint import EndpointAPI
from pysophoscentralapi.api.endpoint.models import Endpoint, EndpointFilters

# Common API
from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.alerts import AlertsAPI
from pysophoscentralapi.api.common.models import Alert, AlertFilters
```

### Filters & Utilities

```python
from pysophoscentralapi.filters import (
    FilterBuilder,      # Build complex filters
    QueryBuilder,       # Unified query building
    SortBuilder,        # Multi-field sorting
    PaginationHelper,   # Pagination utilities
    SearchBuilder,      # Text search queries
)
```

### Exporters

```python
from pysophoscentralapi.exporters import (
    JSONExporter,  # JSON export with options
    CSVExporter,   # CSV export with flattening
)
```

### Sync Wrappers

```python
# Synchronous versions (no async/await)
from pysophoscentralapi.sync.endpoint import EndpointAPISync
from pysophoscentralapi.sync.common import CommonAPISync
```

## Common Patterns

### Async Pattern (Recommended)

```python
import asyncio
from pysophoscentralapi.core import Config
from pysophoscentralapi.api.endpoint import EndpointAPI

async def main():
    config = Config.from_file()
    
    async with EndpointAPI(config) as api:
        endpoints = await api.list()
        return endpoints

# Run
result = asyncio.run(main())
```

### Sync Pattern

```python
from pysophoscentralapi.core import Config
from pysophoscentralapi.sync.endpoint import EndpointAPISync

config = Config.from_file()

with EndpointAPISync(config) as api:
    endpoints = api.list()
```

### With Filtering

```python
from pysophoscentralapi.filters import FilterBuilder, QueryBuilder

# Build filter
filters = FilterBuilder()
filters.equals("status", "active").contains("name", "server")

# Or use QueryBuilder for complete queries
query = QueryBuilder()
query.filter().equals("status", "active")
query.sort_ascending("name")
query.page_size(100)

params = query.build()
```

### With Export

```python
from pysophoscentralapi.exporters import JSONExporter, CSVExporter
from pathlib import Path

# JSON export
json_exporter = JSONExporter(
    output_file=Path("output.json"),
    indent=2
)
json_exporter.export(data)

# CSV export with custom options
csv_exporter = CSVExporter(
    output_file=Path("output.csv"),
    flatten_nested=True,
    custom_headers={"id": "ID", "name": "Name"}
)
csv_exporter.export(data)
```

## Module Documentation

Click on a module below for detailed documentation:

- **[Core Modules](core.md)** - Foundation classes and utilities
- **[Endpoint API](endpoint.md)** - Endpoint management
- **[Common API](common.md)** - Alerts, tenants, admins, roles
- **[Filters](filters.md)** - Query building and filtering
- **[Exporters](exporters.md)** - Data export utilities
- **[Sync](sync.md)** - Synchronous wrappers

## Type Hints

All modules include complete type hints for better IDE support:

```python
from pysophoscentralapi.api.endpoint import EndpointAPI
from pysophoscentralapi.api.endpoint.models import Endpoint, EndpointFilters

async def get_bad_endpoints(api: EndpointAPI) -> list[Endpoint]:
    """Get endpoints with bad health status.
    
    Args:
        api: Endpoint API client
        
    Returns:
        List of endpoints with bad health
    """
    filters = EndpointFilters(health_status=["bad"])
    return await api.list(filters=filters)
```

## Error Handling

All API methods raise appropriate exceptions:

```python
from pysophoscentralapi.core.exceptions import (
    SophosAPIException,
    AuthenticationError,
    RateLimitError,
    ResourceNotFoundError,
)

try:
    async with EndpointAPI(config) as api:
        endpoint = await api.get("endpoint-id")
except AuthenticationError:
    print("Invalid credentials")
except ResourceNotFoundError:
    print("Endpoint not found")
except RateLimitError as e:
    print(f"Rate limit exceeded, retry after {e.retry_after}s")
except SophosAPIException as e:
    print(f"API error: {e}")
```

## Pagination

Handle paginated responses:

```python
# Method 1: Get first page
endpoints = await api.list(page_size=50)

# Method 2: Iterate all pages
async for endpoint in api.paginate():
    print(endpoint.hostname)

# Method 3: Manual pagination
page_token = None
while True:
    response = await api.list(page_size=100, page_token=page_token)
    # Process response.items
    if not response.next_page_token:
        break
    page_token = response.next_page_token
```

## Configuration

Multiple ways to load configuration:

```python
from pysophoscentralapi.core import Config, AuthConfig, APIConfig

# From file
config = Config.from_file()  # Uses default path
config = Config.from_file(Path("/custom/config.toml"))

# From environment variables
config = Config.from_env()

# Programmatic
config = Config(
    auth=AuthConfig(
        client_id="your-id",
        client_secret="your-secret"
    ),
    api=APIConfig(
        region="us",
        timeout=30,
        max_retries=3
    )
)
```

---

**Next:** [Core Modules Documentation](core.md)

