# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased - Phase 10] - 2025-11-22

### Added - Initial Release Preparation
- **Release Documentation**: Created comprehensive v0.1.0 release materials
  - `RELEASE_NOTES_v0.1.0.md` - Complete release notes with features and getting started
  - `PACKAGE_RELEASE_INSTRUCTIONS.md` - Step-by-step release process guide
  - `plans/PHASE10_SUMMARY.md` - Phase 10 status and completion summary
- **Enhanced CLI Filtering**: Added comprehensive filter parameters to `endpoint list` command
  - `--lockdown-status`: Filter by lockdown status (10 options)
  - `--tamper-protection/--no-tamper-protection`: Filter by tamper protection status
  - `--hostname-contains`: Filter by hostname substring
  - `--last-seen-before/--last-seen-after`: Filter by last seen date (ISO 8601 format)
  - `--ids`: Filter by specific endpoint IDs (comma-separated)
  - `--ip-addresses`: Filter by IP addresses (comma-separated)
  - `--mac-addresses`: Filter by MAC addresses (comma-separated)
  - `--search`: Search query across endpoint fields
  - `--view`: Detail level control (basic/summary/full)
  - Updated examples in command help text

### Fixed
- **Config Test**: Fixed `test_from_file_invalid_config` test logic *(Bug fix)*
  - Test was incorrectly testing TOML parsing errors instead of config validation errors
  - Changed from malformed TOML syntax to valid TOML with invalid config data (empty client_id)
  - Now properly tests the "Invalid configuration" error path (validation errors)
  - This ensures proper separation: `test_from_file_invalid_toml` tests parsing, `test_from_file_invalid_config` tests validation
  - All 35 config tests passing, improved code coverage for validation path
- **Datetime Filters**: Fixed `--last-seen-before` and `--last-seen-after` filters returning 400 errors
  - API requires ISO 8601 format with UTC timezone indicator ('Z' suffix)
  - Naive datetimes (without timezone) are now automatically treated as UTC and formatted correctly
  - Updated CLI help text to clarify that times are assumed to be UTC
  - Files: `src/pysophoscentralapi/api/endpoint/models.py`, `src/pysophoscentralapi/cli/endpoint_cmds.py`

### Status
- ✅ **All 35 config tests passing** with **95% config.py coverage**
- ✅ **All code quality checks passing**
- ✅ **Release documentation complete**
- ✅ **Ready for user to update metadata and release**
- 🎯 **Phase 10 is 70% complete** (awaiting user input for personal info)

## [Unreleased - Phase 9] - 2025-11-18

### Added - Polish & Release Preparation
- **Release Checklist**: Created comprehensive `RELEASE_CHECKLIST.md` with pre-release steps
- **Error Message Improvements**: Enhanced CLI error messages with actionable tips
  - Authentication errors now suggest running `pysophos config test`
  - API errors now display correlation IDs for support
  - 404 errors on tenant/admin/role endpoints explain Partner vs Organization credentials
  - Unexpected errors suggest using `--debug` flag
- **Package Configuration**: Updated `pyproject.toml` with Python 3.13 support
- **API Credentials Documentation**: Created `docs/api-credentials.md` explaining Partner vs Organization credentials

### Changed
- **Error Handling**: Enhanced `cli/utils.py` with Partner/Organization credential detection
- **Config Test**: Enhanced `pysophos config test` to display API access level (Partner vs Organization)
- **API Documentation**: Updated `tenants.py` docstrings to note Partner-level requirement
- **README**: Updated test and coverage badges (323 tests, 75% coverage)
- **Test Fixes**: Fixed CLI tests to use correct `load_config` patching

### Fixed
- **Tenant Endpoint 404**: Added helpful error message explaining Partner vs Organization credentials
- **Alert Model Validation**: Changed `category`, `severity`, and `product` fields from strict enums to strings for API compatibility
  - Sophos API returns values outside the documented enum values
  - Changed to flexible string fields to prevent validation errors
- Fixed CLI test failures by correcting mock patches (`Config.from_file` → `load_config`)
- All 323 tests now passing (up from 321)

### Status
- ✅ **323 tests passing** with **75% coverage**
- ✅ **All code quality checks passing**
- ✅ **Package ready for PyPI publication**
- ✅ **Release checklist complete**
- ✅ **Improved error messages for credential issues**

## [Unreleased - CLI Fix] - 2025-11-18

### Fixed - Critical CLI Authentication Issue
- **X-Tenant-ID Header**: Fixed missing tenant ID header in regional API requests
  - Added `tenant_id` parameter to `HTTPClient` and `HTTPClientSync`
  - Updated all CLI commands to pass tenant ID from whoami response
  - Regional endpoints now work correctly (e.g., api-eu01.central.sophos.com)
  
- **Pydantic Model Validation**:
  - Made `AssociatedPerson.id` field optional (Linux endpoints don't always provide it)
  - Made `OSInfo` version fields optional (majorVersion, minorVersion, build)
  - Made `PageInfo` current/total fields optional (cursor pagination doesn't provide them)
  
- **JSON Serialization**: 
  - Fixed datetime serialization in CLI output by using `model_dump(mode="json")`
  - Applied fix to all CLI commands (endpoint, alerts, tenants, admins, roles)

- **CLI Functionality**: Implemented `config test` command
  - Tests OAuth2 token acquisition
  - Tests whoami endpoint
  - Provides detailed diagnostic information for troubleshooting

### Changed
- **HTTPClient**: Now accepts optional `tenant_id` parameter for regional API calls
- **HTTPClientSync**: Now accepts optional `tenant_id` parameter for regional API calls
- **Core Models**: Several fields made optional to match actual API responses

### Status
- ✅ CLI is now **fully functional** with real API integration
- ✅ All 244 tests passing with 70% coverage
- ✅ Authentication working correctly for all endpoints
- ✅ JSON, CSV, and table output formats working

## [Unreleased - Phase 8] - 2025-11-18

### Added - Testing & Quality (Complete ✅)
- **Unit Tests** (+77 new tests, now 321 total):
  - Added 16 comprehensive tests for `core/auth.py` (98% coverage achieved)
  - Added 12 tests for `core/client.py` (71% coverage achieved)
  - Added 23 tests for `core/pagination.py` (100% coverage achieved)
  - Added 35 tests for `core/config.py` (95% coverage achieved)
  - Added 19 tests for `exporters/progress.py` (97% coverage achieved)
  - Fixed authentication context manager issue in CLI helpers
  - All 321 tests passing with zero failures
  
- **Coverage Improvements**:
  - Overall coverage: 70% → 74% (+4%)
  - core/pagination.py: 31% → 100% (+69%)
  - core/config.py: 53% → 95% (+42%)
  - exporters/progress.py: 0% → 97% (+97%)
  - core/auth.py: 27% → 98% (+71%)
  - core/client.py: 16% → 71% (+55%)
  - core/models.py: 92% → 98% (+6%)

### Fixed
- Fixed `expires_soon()` method bug in Token model (timestamp logic)
- Fixed CLI context manager protocol error for EndpointAPI and CommonAPI
- Created helper functions `create_endpoint_api_sync()` and `create_common_api_sync()` in `cli/utils.py`
- All CLI commands now properly initialize API clients

### Security
- Dependency audit completed - all packages up-to-date
- No known security vulnerabilities detected
- Code quality maintained with ruff formatting and linting

### Deferred
- Integration tests (would require 20-30 additional tests)
- End-to-end CLI tests (would require 15-20 additional tests)
- Performance benchmarks (would require 5-10 tests)
- Additional coverage to reach 90%+ (would require significant additional development time)

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure (Phase 1)
- Core infrastructure modules (Phase 1)
  - HTTP client with retry logic and rate limiting
  - OAuth2 authentication with token caching
  - Configuration management (TOML, env vars)
  - Exception hierarchy (15+ custom exceptions)
  - Base models and utilities (Pydantic)
  - Pagination utilities for cursor-based pagination
- Testing framework setup (Phase 1)
  - 20 core infrastructure unit tests
- **Endpoint API implementation (Phase 2)**
  - Complete data models for endpoints (15+ Pydantic models)
  - EndpointAPI client with 12 methods
  - Endpoint management (list, get, update, delete)
  - Advanced filtering with EndpointFilters
  - Endpoint actions (scan, isolate, unisolate)
  - Tamper protection operations (get, update, get password)
  - Pagination support with async iterators
  - 26 comprehensive unit tests for Endpoint API
  - Test coverage: 87-92% for Endpoint API modules
- **Common API implementation (Phase 3)**
  - Complete data models: 20+ Pydantic models (Alert, Tenant, Admin, Role, etc.)
  - AlertsAPI client with 4 methods
  - TenantsAPI client with 3 methods
  - AdminsAPI client with 5 methods (full CRUD)
  - RolesAPI client with 5 methods (full CRUD)
  - CommonAPI aggregator class for unified API access
  - Advanced filtering with AlertFilters and TenantFilters
  - Pagination support for alerts and tenants
  - 30 comprehensive unit tests for Common API
  - Test coverage: 78-100% for Common API modules
- **Phase 4: CLI Implementation + Sync Wrappers (Complete)**
  - **Synchronous Interface** (deferred from Phases 2-3)
    - HTTPClientSync with context manager support
    - PaginatorSync for blocking iteration
    - EndpointAPISync - complete sync wrapper for all 12 endpoint methods
    - CommonAPISync - complete sync wrappers for all Common API clients
    - Sync utilities (`run_async`, decorators)
    - 20 sync wrapper unit tests
  - **CLI Output System**
    - OutputFormatter class with Rich integration
    - Table formatter with colored output
    - JSON formatter with syntax highlighting
    - CSV formatter with file export
    - Success/error/warning/info message helpers
  - **CLI Utilities**
    - Error handling decorator for graceful failures
    - Output option decorators (--output, --output-file, --no-color)
    - Sync mode decorator (--sync flag support)
    - Helper functions for data conversion
  - **Complete CLI Application**
    - Main CLI entry point: `pysophos` command
    - Configuration commands: init, show, test
    - Endpoint API commands: list, get, scan, isolate, unisolate, tamper (status/update)
    - Common API commands: alerts, tenants, admins, roles (all with list/get)
    - Alert actions support
    - Rich help text and examples
    - Demo mode implementations
    - 17 comprehensive CLI tests
- **Phase 5: Export & Formatting (Complete)**
  - **Library-Level Exporters**
    - BaseExporter abstract class for extensibility
    - JSONExporter with pretty-print, compact, field filtering
    - CSVExporter with header customization, nested object flattening
    - ExportError exception for error handling
    - Batch processing support for memory efficiency
    - File output or string return capabilities
  - **Progress Indicators**
    - ExportProgressTracker with Rich progress bars
    - Time remaining estimation
    - Custom description support
    - Context manager interface
  - **Advanced Features**
    - Field inclusion/exclusion filters (JSON)
    - Custom header mapping (CSV)
    - Configurable delimiters (CSV)
    - Maximum nesting depth control (CSV)
    - Pydantic model support
    - Excel-compatible CSV output
  - **Testing**
    - 32 comprehensive exporter tests
    - 128 total tests passing
    - 67% overall code coverage
    - All linting checks passing
- **Phase 6: Filtering & Advanced Features (Complete)**
  - **Filter System**
    - FilterBase abstract class with common filter operations
    - FilterOperator enum for type-safe filter operations
    - FilterBuilder with fluent interface (equals, contains, between, in_list, etc.)
    - Filter composition and chaining support
    - Date range filters with start/end parameters
  - **Query Builder**
    - QueryBuilder for unified query construction
    - Combined filters, sorting, pagination in single interface
    - Field selection support
    - Result limit control
    - Fluent API design for ease of use
  - **Sorting Utilities**
    - SortBuilder for multi-field sorting
    - SortDirection enum (ASCENDING/DESCENDING)
    - Sort reversal functionality
    - Custom separator support
    - Conversion to API parameters
  - **Pagination Helpers**
    - PaginationHelper utility class
    - Offset and page number calculations
    - Total pages calculation
    - Page info with navigation flags (has_next, has_previous, etc.)
    - Page size recommendations based on dataset size
    - Page parameter creation and validation
  - **Search Utilities**
    - SearchBuilder for text search queries
    - Multi-term search with AND/OR logic
    - Field-specific search
    - Query string building
  - **Testing**
    - 91 comprehensive filter tests
    - 219 total tests passing (100% pass rate)
    - 98-100% coverage for filter modules
    - 72% overall code coverage
- **Phase 7: Documentation (Complete)**
  - **User Documentation**
    - Comprehensive getting started guide
    - Installation instructions
    - Authentication setup (3 methods: file, env vars, programmatic)
    - First API call examples (async and sync)
    - Troubleshooting section
  - **CLI Guide**
    - Complete command reference for all commands
    - Global options and configuration commands
    - Endpoint, Alert, Tenant, Admin, Role commands
    - Output formats (table, JSON, CSV)
    - Common workflows and tips
    - Shell integration examples
  - **API Reference**
    - Module overview and quick reference
    - Common patterns (async/sync)
    - Type hints examples
    - Error handling patterns
    - Pagination strategies
    - Configuration methods
  - **Examples & Tutorials**
    - Basic examples (list, filter, scan, export)
    - Advanced examples (complex filtering, batch processing, incident response)
    - Multi-tenant operations
    - CLI scripting examples
    - Integration examples (Pandas, Elasticsearch, Slack)
  - **Contributing Guide**
    - Development setup instructions
    - Code of conduct
    - Development workflow (branching, commits, PR)
    - Coding standards (PEP 8, type hints, docstrings)
    - Testing requirements and examples
    - Documentation standards
    - Pull request process
  - **Enhanced README**
    - Updated status badges (219 tests, 72% coverage)
    - Complete feature list
    - Development status (7/10 phases, 70% complete)
    - Async and sync usage examples
    - Project statistics
    - Clear navigation to documentation
- **CLI-API Integration (Complete)**
  - **Endpoint Commands** (7 commands)
    - Real API integration for list, get, scan, isolate, unisolate
    - Tamper protection status and update
    - Full async/sync support via --sync flag
    - Error handling with @handle_errors decorator
  - **Common API Commands** (5 commands)
    - Alerts list and get with severity filtering
    - Tenants list and get
    - Admins list
    - Roles list
  - **Configuration Loading**
    - Automatic fallback from file to environment variables
    - Clear error messages for missing config
  - **All Commands Production-Ready**
    - No more "demo mode" messages
    - Real data from Sophos Central APIs
    - Complete error handling
    - Support for all output formats (table/JSON/CSV)

### Documentation
- Comprehensive planning documents
- Technical specification with dual interface (async+sync) architecture
- Architecture diagrams
- API coverage matrix
- Sync implementation guide
- Development workflow guide

[Unreleased]: https://github.com/yourusername/pysophoscentralapi/commits/main

