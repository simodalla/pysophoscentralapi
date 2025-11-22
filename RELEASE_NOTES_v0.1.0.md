# Release Notes - PySophosCentralApi v0.1.0

**Release Date:** 2025-11-22  
**Status:** Initial Public Release

---

## 🎉 Overview

PySophosCentralApi v0.1.0 is the initial release of a professional-grade Python library and CLI application for interacting with Sophos Central APIs. This release provides comprehensive support for Sophos Central Endpoint API and Common API v1.

---

## ✨ Features

### Core Library
- **Async-First Architecture**: Built on modern async Python with `httpx`
- **Dual Interface**: Both asynchronous and synchronous APIs available
- **Type-Safe**: Complete type hints throughout the codebase
- **OAuth2 Authentication**: Secure client credentials flow with token caching
- **Smart Pagination**: Automatic handling of cursor-based pagination
- **Error Handling**: Comprehensive exception hierarchy with detailed error messages

### API Coverage

#### Endpoint API (v1)
- ✅ List, get, update, and delete endpoints
- ✅ Endpoint scanning operations
- ✅ Endpoint isolation/un-isolation
- ✅ Tamper protection management
- ✅ Advanced filtering and search
- ✅ Health status monitoring

#### Common API (v1)
- ✅ Alert management (list, get, perform actions)
- ✅ Tenant operations (requires Partner credentials)
- ✅ Admin management (requires Partner credentials)
- ✅ Role management (requires Partner credentials)

### CLI Application
- **Intuitive Commands**: Well-organized command structure
- **Multiple Output Formats**: Table (Rich), JSON, CSV
- **Configuration Management**: TOML-based config with environment variable support
- **Helpful Error Messages**: Context-aware error handling with actionable tips
- **Credential Detection**: Automatic detection of Partner vs Organization API credentials

### Advanced Features
- **Export System**: Professional JSON and CSV exporters with progress indicators
- **Filter Builders**: Fluent interface for constructing complex queries
- **Query Builders**: Unified query building with filters, sorting, and pagination
- **Sort Utilities**: Multi-field sorting with direction control
- **Search Builders**: Text search query construction

---

## 📊 Technical Metrics

- **Tests**: 323 passing (5 skipped)
- **Code Coverage**: 75%
- **Type Checking**: 100% with mypy
- **Code Quality**: All ruff checks passing
- **Python Support**: 3.10, 3.11, 3.12, 3.13
- **Dependencies**: Minimal, well-maintained packages only

---

## 🚀 Getting Started

### Installation

```bash
pip install pysophoscentralapi
```

### Quick Start

**CLI Usage:**
```bash
# Initialize configuration
pysophos config init

# List endpoints
pysophos endpoint list

# List alerts
pysophos alerts list --severity high

# Export to CSV
pysophos endpoint list --output csv --output-file endpoints.csv
```

**Library Usage:**
```python
# Async API (recommended)
from pysophoscentralapi import EndpointAPI
from pysophoscentralapi.core import Config, HTTPClient, OAuth2ClientCredentials

config = Config.from_file()
auth = OAuth2ClientCredentials(config.auth)

async with HTTPClient(base_url, auth_provider=auth) as client:
    api = EndpointAPI(client)
    endpoints = await api.list_endpoints()
    for endpoint in endpoints.items:
        print(f"{endpoint.hostname}: {endpoint.health.overall}")

# Sync API (wrapper)
from pysophoscentralapi.sync import EndpointAPISync, HTTPClientSync

with HTTPClientSync(base_url, auth_provider=auth) as client:
    api = EndpointAPISync(client)
    endpoints = api.list_endpoints()  # No await needed
    for endpoint in endpoints.items:
        print(f"{endpoint.hostname}: {endpoint.health.overall}")
```

---

## 🔐 API Credentials

### Organization vs Partner Credentials

This release includes automatic detection and helpful guidance for two credential types:

- **Organization-Level**: Access to own organization's endpoints and alerts
- **Partner-Level**: Full access including tenant/admin/role management

The CLI will automatically detect your credential type and provide helpful messages if you try to access Partner-only endpoints with Organization credentials.

---

## 📚 Documentation

- **Getting Started**: `docs/getting-started.md`
- **CLI Guide**: `docs/guides/cli-guide.md`
- **API Reference**: `docs/api/index.md`
- **Examples**: `docs/examples/index.md`
- **API Credentials Guide**: `docs/api-credentials.md`

---

## 🐛 Known Issues

### Limitations
1. **Settings API**: Not yet implemented (planned for v0.2.0)
2. **Integration Tests**: Basic integration tests deferred
3. **Performance Benchmarks**: Not included in this release

### Workarounds
- Use the `--debug` flag for verbose error output
- Check credential type with `pysophos config test`

---

## 🔄 Breaking Changes

N/A (Initial release)

---

## 📝 Changelog

See [CHANGELOG.md](change-log.md) for detailed changelog.

### Added
- Complete Endpoint API v1 implementation
- Complete Common API v1 implementation (alerts, tenants, admins, roles)
- Professional CLI with Click framework
- Async-first architecture with sync wrappers
- Comprehensive filter and query building system
- Export system (JSON, CSV) with progress indicators
- OAuth2 authentication with token caching
- Configuration management (TOML, environment variables)
- Rich terminal output with colored tables
- Comprehensive documentation

### Fixed
- Alert model validation for flexible API responses
- Endpoint model optional fields for API compatibility
- Partner vs Organization credential detection
- Helpful error messages throughout

---

## 🙏 Acknowledgments

Built with:
- [httpx](https://www.python-httpx.org/) - Modern HTTP client
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [pytest](https://docs.pytest.org/) - Testing framework

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🔗 Links

- **Homepage**: https://github.com/yourusername/pysophoscentralapi
- **Documentation**: https://pysophoscentralapi.readthedocs.io
- **Issues**: https://github.com/yourusername/pysophoscentralapi/issues
- **Sophos Developer**: https://developer.sophos.com/

---

## 🚧 Roadmap

### v0.2.0 (Planned)
- Settings API implementation
- Integration tests
- Performance optimizations
- Additional export formats

### v1.0.0 (Future)
- 90%+ code coverage
- Complete E2E test suite
- Performance benchmarks
- Plugin system

---

**Thank you for using PySophosCentralApi!**

For questions, issues, or contributions, please visit our GitHub repository.


