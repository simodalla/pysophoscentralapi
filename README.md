# PySophosCentralApi

A professional-grade Python library and CLI application for interacting with Sophos Central APIs.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🔌 **Comprehensive API Coverage**: Full support for Sophos Central Endpoint API and Common API v1
- 🖥️ **CLI & Library**: Use as a command-line tool or import as a Python library
- 🎨 **Beautiful Output**: Rich colored tables, JSON, and CSV export formats
- 🔄 **Smart Pagination**: Automatic handling of paginated responses
- ⚡ **Async-First**: Built on modern async Python for optimal performance
- 🛡️ **Type-Safe**: Full type hints throughout for better IDE support
- 🔐 **Secure**: Proper credential handling with OAuth2 support
- ✅ **Well-Tested**: Comprehensive test coverage (>90%)

## Quick Start

### Installation

```bash
pip install pysophoscentralapi
```

### Configuration

Create a configuration file at `~/.config/pysophos/config.toml`:

```toml
[auth]
client_id = "your-client-id"
client_secret = "your-client-secret"

[api]
region = "us"  # or "eu", "ap", etc.
```

Or use environment variables:

```bash
export SOPHOS_CLIENT_ID="your-client-id"
export SOPHOS_CLIENT_SECRET="your-client-secret"
```

### CLI Usage

```bash
# List all endpoints
pysophos endpoint list

# Filter by health status
pysophos endpoint list --health-status good

# Export to JSON
pysophos endpoint list --output json --export-file endpoints.json

# Get alerts
pysophos alerts list --severity high

# List tenants
pysophos tenants list
```

### Library Usage

```python
import asyncio
from pysophoscentralapi.core.config import Config
from pysophoscentralapi.core.auth import OAuth2ClientCredentials
from pysophoscentralapi.core.client import HTTPClient

async def main():
    # Load configuration
    config = Config.from_file()
    
    # Create auth provider
    auth = OAuth2ClientCredentials(config.auth)
    
    # Get data region
    whoami = await auth.whoami()
    
    # Create HTTP client
    async with HTTPClient(whoami.api_host_data_region, auth) as client:
        # Make API calls
        response = await client.get("/endpoint/v1/endpoints")
        print(response)

asyncio.run(main())
```

## Development Status

This project is currently in **Phase 1: Foundation** (✅ Complete)

- [x] Project structure and configuration
- [x] Core infrastructure (HTTP client, auth, config)
- [x] Exception hierarchy
- [x] Base models and utilities
- [x] Testing framework

**Next**: Phase 2 - Endpoint API Implementation

## Requirements

- Python 3.10 or higher
- httpx
- pydantic
- click
- rich
- colorama

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pysophoscentralapi.git
cd pysophoscentralapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install uv
uv pip install -r requirements.piptools
uv pip install -r requirements-development.piptools

# Install in editable mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run only unit tests
pytest -m unit

# Run specific test file
pytest tests/unit/test_core/test_exceptions.py
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Fix linting issues
ruff check --fix .
```

## Documentation

Full documentation is available in the [`plans/`](plans/) directory:

- [Project Plan](plans/project-plan.md) - Overall project roadmap
- [Technical Specification](plans/technical-specification.md) - Implementation details
- [Development Workflow](plans/development-workflow.md) - Best practices
- [API Coverage Matrix](plans/api-coverage-matrix.md) - Endpoint tracking
- [Architecture Diagrams](plans/architecture-diagrams.md) - Visual guides

## Contributing

Contributions are welcome! Please see [plans/development-workflow.md](plans/development-workflow.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Sophos](https://www.sophos.com/) for providing the Central APIs
- Built with [httpx](https://www.python-httpx.org/), [pydantic](https://docs.pydantic.dev/), [click](https://click.palletsprojects.com/), and [rich](https://rich.readthedocs.io/)

## Support

- 📖 [Documentation](plans/)
- 🐛 [Issue Tracker](https://github.com/yourusername/pysophoscentralapi/issues)
- 💬 [Discussions](https://github.com/yourusername/pysophoscentralapi/discussions)

---

**Note**: This project is not officially affiliated with or endorsed by Sophos.

