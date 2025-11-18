# Getting Started with PySophosCentralApi

This guide will walk you through installing PySophosCentralApi, setting up authentication, and making your first API call.

## 📦 Installation

### Requirements

- Python 3.10 or higher
- pip or uv package manager

### Install from PyPI

```bash
pip install pysophoscentralapi
```

### Install from Source

```bash
git clone https://github.com/yourusername/pysophoscentralapi.git
cd pysophoscentralapi
pip install -e .
```

### Verify Installation

```bash
pysophos --version
```

## 🔐 Authentication Setup

PySophosCentralApi uses OAuth2 Client Credentials flow for authentication. You'll need:

1. **Client ID** - From Sophos Central API credentials
2. **Client Secret** - From Sophos Central API credentials
3. **Region** - Your data region (us, eu, ap, de, ie)

### Obtaining API Credentials

1. Log in to [Sophos Central](https://central.sophos.com/)
2. Navigate to **Global Settings** → **API Credentials**
3. Click **Add Credential**
4. Name your credential and select appropriate permissions
5. Copy the **Client ID** and **Client Secret** (save the secret securely!)

### Configuration Methods

#### Option 1: Configuration File (Recommended)

Create `~/.config/pysophos/config.toml`:

```toml
[auth]
client_id = "your-client-id-here"
client_secret = "your-client-secret-here"

[api]
region = "us"  # Change to your region: us, eu, ap, de, ie
timeout = 30
max_retries = 3

[output]
default_format = "table"
color_enabled = true
page_size = 50
```

**Using CLI to initialize:**

```bash
pysophos config init
```

This will prompt you for credentials and create the config file.

#### Option 2: Custom Configuration File Location

You can specify a custom configuration file path using:

**Command-line option:**
```bash
pysophos --config-file /path/to/my-config.toml endpoint list
```

**Environment variable:**
```bash
export SOPHOS_CONFIG_FILE=/path/to/my-config.toml
pysophos endpoint list
```

**Configuration Priority (highest to lowest):**
1. Command-line `--config-file` option
2. `SOPHOS_CONFIG_FILE` environment variable
3. `./config.toml` (current directory)
4. `~/.config/pysophos/config.toml` (default)
5. `~/.pysophos/config.toml` (alternative)
6. Environment variables (`SOPHOS_CLIENT_ID`, `SOPHOS_CLIENT_SECRET`, etc.)

#### Option 3: Environment Variables

```bash
export SOPHOS_CLIENT_ID="your-client-id"
export SOPHOS_CLIENT_SECRET="your-client-secret"
export SOPHOS_REGION="us"
```

Add these to your `~/.bashrc`, `~/.zshrc`, or equivalent for persistence.

#### Option 4: Programmatic (Library Usage)

```python
from pysophoscentralapi.core.config import Config, APIConfig, AuthConfig

config = Config(
    auth=AuthConfig(
        client_id="your-client-id",
        client_secret="your-client-secret"
    ),
    api=APIConfig(region="us")
)
```

## 🚀 Your First CLI Command

### List Endpoints

```bash
pysophos endpoint list
```

This will connect to Sophos Central APIs and display all endpoints in a formatted table with real data from your environment.

### Filter by Health Status

```bash
pysophos endpoint list --health-status bad
```

### Export to JSON

```bash
pysophos endpoint list --output json -f endpoints.json
```

### Get Alerts

```bash
pysophos alerts list --severity high --severity critical
```

### View Command Help

```bash
pysophos --help
pysophos endpoint --help
pysophos alerts list --help
```

## 📚 Your First Python Script

### Async Example (Recommended)

```python
import asyncio
from pysophoscentralapi.core import Config
from pysophoscentralapi.api.endpoint import EndpointAPI

async def main():
    # Load configuration
    config = Config.from_file()
    
    # Create API client
    async with EndpointAPI(config) as api:
        # List all endpoints
        endpoints = await api.list()
        
        print(f"Found {len(endpoints)} endpoints:")
        for endpoint in endpoints:
            print(f"  - {endpoint.hostname} ({endpoint.health})")

# Run the async function
asyncio.run(main())
```

### Sync Example

```python
from pysophoscentralapi.core import Config
from pysophoscentralapi.sync.endpoint import EndpointAPISync

# Load configuration
config = Config.from_file()

# Create sync API client
with EndpointAPISync(config) as api:
    # List all endpoints
    endpoints = api.list()
    
    print(f"Found {len(endpoints)} endpoints:")
    for endpoint in endpoints:
        print(f"  - {endpoint.hostname} ({endpoint.health})")
```

## 🎯 Common Use Cases

### 1. List Endpoints with Filtering

```python
from pysophoscentralapi.api.endpoint.models import EndpointFilters, HealthStatus

async with EndpointAPI(config) as api:
    # Create filter
    filters = EndpointFilters(
        health_status=[HealthStatus.BAD, HealthStatus.SUSPICIOUS]
    )
    
    # Get filtered endpoints
    endpoints = await api.list(filters=filters)
```

### 2. Get Alerts

```python
from pysophoscentralapi.api.common import CommonAPI
from pysophoscentralapi.api.common.models import AlertFilters, Severity

async with CommonAPI(config) as api:
    # Create filter
    filters = AlertFilters(
        severity=[Severity.HIGH, Severity.CRITICAL]
    )
    
    # Get alerts
    alerts = await api.alerts.list(filters=filters)
```

### 3. Scan an Endpoint

```python
async with EndpointAPI(config) as api:
    # Trigger scan
    await api.scan(
        endpoint_id="abc-123-def",
        comment="Routine security scan"
    )
```

### 4. Export Data

```python
from pysophoscentralapi.exporters import JSONExporter
from pathlib import Path

# Get data
async with EndpointAPI(config) as api:
    endpoints = await api.list()

# Export to JSON
exporter = JSONExporter(
    output_file=Path("endpoints.json"),
    indent=2
)
exporter.export(endpoints)
```

## 🔍 Next Steps

Now that you have PySophosCentralApi set up, explore:

- **[CLI Guide](guides/cli-guide.md)** - Complete command reference
- **[Library Guide](guides/library-guide.md)** - In-depth library usage
- **[Filter Guide](guides/filtering.md)** - Advanced filtering techniques
- **[Examples](examples/index.md)** - More code examples
- **[API Reference](api/index.md)** - Complete API documentation

## 🆘 Troubleshooting

### Authentication Errors

**Problem**: `AuthenticationError: Invalid credentials`

**Solutions**:
1. Verify your Client ID and Secret are correct
2. Check that credentials have appropriate permissions
3. Ensure credentials are not expired
4. Verify you're using the correct region

### Configuration Not Found

**Problem**: `Configuration file not found`

**Solutions**:
1. Run `pysophos config init` to create configuration
2. Set environment variables instead
3. Specify config file: `pysophos --config-file path/to/config.toml`

### Rate Limiting

**Problem**: `RateLimitError: Too many requests`

**Solutions**:
1. The library automatically retries with exponential backoff
2. Reduce concurrent requests
3. Add delays between batches
4. Check Sophos API rate limits for your plan

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'pysophoscentralapi'`

**Solutions**:
1. Verify installation: `pip list | grep pysophoscentralapi`
2. Reinstall: `pip install --force-reinstall pysophoscentralapi`
3. Check Python version: `python --version` (requires 3.10+)

## 📞 Getting Help

- **Documentation**: Browse the docs for detailed information
- **Examples**: Check `/docs/examples/` for code samples
- **Issues**: [GitHub Issues](https://github.com/yourusername/pysophoscentralapi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pysophoscentralapi/discussions)

---

**Ready to dive deeper?** → [CLI Guide](guides/cli-guide.md) | [Library Guide](guides/library-guide.md)

