# PySophosCentralApi

A professional-grade Python library and CLI application for interacting with Sophos Central APIs.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-219%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-72%25-green.svg)](htmlcov/)

## ✨ Features

- 🔌 **Comprehensive API Coverage**: Full support for Sophos Central Endpoint API and Common API v1
- 🖥️ **CLI & Library**: Use as a command-line tool or import as a Python library
- 🔄 **Dual Interface**: Async-first design with synchronous wrappers available
- 🎨 **Beautiful Output**: Rich colored tables, JSON, and CSV export formats
- 🔍 **Advanced Filtering**: Powerful query builders for complex searches
- 📊 **Export Capabilities**: Professional JSON and CSV exporters
- 🔄 **Smart Pagination**: Automatic handling of paginated responses
- ⚡ **High Performance**: Built on modern async Python with httpx
- 🛡️ **Type-Safe**: Complete type hints for better IDE support
- 🔐 **Secure**: OAuth2 authentication with proper credential handling
- ✅ **Well-Tested**: 219 tests passing with 72% coverage

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

### Library Usage (Async)

```python
import asyncio
from pysophoscentralapi.core import Config
from pysophoscentralapi.api.endpoint import EndpointAPI
from pysophoscentralapi.api.endpoint.models import EndpointFilters, HealthStatus

async def main():
    # Load configuration
    config = Config.from_file()
    
    # Create API client
    async with EndpointAPI(config) as api:
        # List all endpoints
        endpoints = await api.list()
        
        # Filter by health status
        filters = EndpointFilters(
            health_status=[HealthStatus.BAD, HealthStatus.SUSPICIOUS]
        )
        bad_endpoints = await api.list(filters=filters)
        
        # Scan an endpoint
        await api.scan("endpoint-id", comment="Security scan")

asyncio.run(main())
```

### Library Usage (Sync)

```python
from pysophoscentralapi.core import Config
from pysophoscentralapi.sync.endpoint import EndpointAPISync

config = Config.from_file()

# Synchronous API - No async/await needed
with EndpointAPISync(config) as api:
    endpoints = api.list()
    
    for endpoint in endpoints:
        print(f"{endpoint.hostname}: {endpoint.health}")
```

## 📊 Development Status

**Current Phase**: 7 of 10 (70% Complete)

### ✅ Completed Phases

- ✅ **Phase 1**: Foundation - Core infrastructure
- ✅ **Phase 2**: Endpoint API - Complete implementation
- ✅ **Phase 3**: Common API - Alerts, Tenants, Admins, Roles
- ✅ **Phase 4**: CLI + Sync Wrappers - Full CLI application
- ✅ **Phase 5**: Export & Formatting - JSON/CSV exporters
- ✅ **Phase 6**: Filtering & Advanced Features - Query builders
- 🚧 **Phase 7**: Documentation (In Progress)

### 📈 Project Statistics

- **Tests**: 219 passing (100% pass rate)
- **Coverage**: 72%
- **Modules**: 39 implementation + 22 test
- **Lines of Code**: ~8,700+

### 🚀 What's Working Now

The software is fully functional for both library and CLI usage:

```python
# Async API - Fully Implemented
async with EndpointAPI(config) as api:
    endpoints = await api.list()
    
# Sync API - Fully Implemented
with EndpointAPISync(config) as api:
    endpoints = api.list()

# CLI - Fully Functional with Real API Integration
pysophos endpoint list --health-status bad
pysophos alerts list --severity high
pysophos tenants list
```

**All CLI commands now use real Sophos Central APIs!** The software is production-ready for monitoring, management, and automation tasks.

## 📦 Requirements

- **Python**: 3.10 or higher
- **Dependencies**: 
  - httpx (async HTTP client)
  - pydantic (data validation)
  - click (CLI framework)
  - rich (terminal formatting)
  - colorama (colored output)

## 🎯 Key Capabilities

### For Developers

- **Async & Sync APIs**: Choose the interface that fits your project
- **Type-Safe**: Complete type hints with Pydantic models
- **Advanced Filtering**: Use `QueryBuilder` for complex queries
- **Export Tools**: Professional JSON and CSV exporters
- **Comprehensive Testing**: 219 tests ensure reliability

### For System Administrators

- **Powerful CLI**: Easy-to-use commands for all operations
- **Multiple Output Formats**: Table, JSON, CSV
- **Batch Operations**: Process multiple items efficiently
- **Configuration Management**: Simple setup with TOML or environment variables
- **Colored Output**: Clear, readable results with Rich formatting

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

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

### User Documentation
- **[Getting Started](docs/getting-started.md)** - Installation and first steps
- **[CLI Guide](docs/guides/cli-guide.md)** - Complete command reference
- **[API Reference](docs/api/index.md)** - Library API documentation
- **[Examples](docs/examples/index.md)** - Code examples and tutorials

### Developer Documentation
- [Project Plan](plans/project-plan.md) - Overall project roadmap
- [Technical Specification](plans/technical-specification.md) - Implementation details
- [Development Workflow](plans/development-workflow.md) - Best practices
- [API Coverage Matrix](plans/api-coverage-matrix.md) - Endpoint tracking
- [Architecture Diagrams](plans/architecture-diagrams.md) - Visual guides
- [Phase Status](plans/PHASE_STATUS.md) - Detailed progress tracking

## 🤝 Contributing

Contributions are welcome! We value:

- Bug reports and feature requests
- Code contributions
- Documentation improvements
- Testing and feedback

Please see our [Contributing Guide](docs/contributing.md) for:
- Development setup
- Coding standards
- Testing requirements
- Pull request process

For detailed development practices, see [Development Workflow](plans/development-workflow.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Sophos](https://www.sophos.com/) for providing the Central APIs
- Built with [httpx](https://www.python-httpx.org/), [pydantic](https://docs.pydantic.dev/), [click](https://click.palletsprojects.com/), and [rich](https://rich.readthedocs.io/)

## 💡 Examples

### Filter Endpoints by Health

```python
from pysophoscentralapi.filters import QueryBuilder

query = QueryBuilder()
query.filter().equals("health", "bad")
query.sort_ascending("hostname")
query.page_size(100)

params = query.build()
```

### Export to CSV

```python
from pysophoscentralapi.exporters import CSVExporter
from pathlib import Path

exporter = CSVExporter(
    output_file=Path("endpoints.csv"),
    flatten_nested=True
)
exporter.export(data)
```

More examples in the [Examples Documentation](docs/examples/index.md).

## 🆘 Support

- 📖 [Documentation](docs/)
- 🚀 [Getting Started Guide](docs/getting-started.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/pysophoscentralapi/issues)
- 💬 [Discussions](https://github.com/yourusername/pysophoscentralapi/discussions)

---

**Note**: This project is not officially affiliated with or endorsed by Sophos.

