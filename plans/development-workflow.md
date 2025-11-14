# PySophosCentralApi - Development Workflow & Best Practices

## 1. Git Workflow Strategy

### 1.1 Branch Strategy (GitHub Flow)

**Main Branches:**
- `main`: Production-ready code, always deployable
- `develop`: Integration branch for features (optional, can work directly with main)

**Feature Branches:**
- Naming: `feature/<short-description>`
- Examples: `feature/endpoint-api`, `feature/cli-commands`, `feature/export-csv`
- Branch from: `main`
- Merge to: `main` via Pull Request

**Bug Fix Branches:**
- Naming: `fix/<issue-description>`
- Examples: `fix/auth-token-refresh`, `fix/pagination-edge-case`
- Branch from: `main`
- Merge to: `main` via Pull Request

**Documentation Branches:**
- Naming: `docs/<description>`
- Examples: `docs/api-reference`, `docs/getting-started`

### 1.2 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semi-colons, etc.)
- `refactor`: Code refactoring without functionality change
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependency updates, build config, etc.)
- `perf`: Performance improvements

**Examples:**
```
feat(endpoint): add endpoint listing with filtering

Implement list_endpoints method with support for all filter parameters
including health status, type, hostname, and date ranges.

Closes #123

---

fix(auth): handle token expiration edge case

Token refresh was failing when token expired exactly at request time.
Added buffer time to refresh tokens before they expire.

Fixes #456

---

docs(cli): add examples for common use cases

Added comprehensive examples showing:
- Basic endpoint listing
- Filtering and sorting
- Exporting to CSV/JSON
- Alert management workflows
```

### 1.3 Pull Request Process

**PR Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines (ruff)
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings
- [ ] Changelog updated

## Related Issues
Closes #issue_number
```

**Review Requirements:**
- At least 1 approval for feature branches
- All CI checks must pass
- No merge conflicts
- Code coverage maintained or improved

### 1.4 Version Tagging

**Semantic Versioning:**
- Format: `v<MAJOR>.<MINOR>.<PATCH>`
- Examples: `v1.0.0`, `v1.2.3`, `v2.0.0-beta.1`

**Tag Creation:**
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

**Pre-release Tags:**
- Alpha: `v1.0.0-alpha.1`
- Beta: `v1.0.0-beta.1`
- RC: `v1.0.0-rc.1`

---

## 2. Development Environment Setup

### 2.1 Initial Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pysophoscentralapi.git
cd pysophoscentralapi

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install uv for dependency management
pip install uv

# Install dependencies
uv pip install -r requirements.piptools
uv pip install -r requirements-development.piptools

# Install package in editable mode
uv pip install -e .

# Install pre-commit hooks
pre-commit install
```

### 2.2 Development Dependencies

**requirements-development.piptools:**
```
# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
faker>=22.0.0

# Linting & Formatting
ruff>=0.2.0

# Type Checking
mypy>=1.8.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.5.0
mkdocstrings[python]>=0.24.0

# Development Tools
ipython>=8.20.0
httpx[http2]>=0.26.0

# Pre-commit
pre-commit>=3.6.0
```

**requirements.piptools:**
```
# Core
httpx>=0.26.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# CLI
click>=8.1.0
rich>=13.7.0
colorama>=0.4.6

# Data Export
pandas>=2.1.0  # Optional, for CSV export

# Configuration
toml>=0.10.2
python-dotenv>=1.0.0
```

### 2.3 IDE Configuration

**VS Code Settings (.vscode/settings.json):**
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ],
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true,
    ".mypy_cache": true,
    ".ruff_cache": true
  }
}
```

**PyCharm Settings:**
- Enable ruff as external tool
- Configure pytest as default test runner
- Enable type checking with mypy
- Set import optimizer to follow project style

---

## 3. Code Quality Standards

### 3.1 Ruff Configuration (ruff.toml)

```toml
[lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "T10", # flake8-debugger
    "EM",  # flake8-errmsg
    "ISC", # flake8-implicit-str-concat
    "ICN", # flake8-import-conventions
    "PIE", # flake8-pie
    "PT",  # flake8-pytest-style
    "Q",   # flake8-quotes
    "RET", # flake8-return
    "SIM", # flake8-simplify
    "PTH", # flake8-use-pathlib
    "PL",  # pylint
    "RUF", # ruff-specific rules
]

ignore = [
    "E501",    # line too long (handled by formatter)
    "PLR0913", # too many arguments
    "PLR2004", # magic value comparison
]

[lint.per-file-ignores]
"tests/**/*.py" = [
    "PLR2004", # Magic value comparisons are OK in tests
    "S101",    # Use of assert is OK in tests
]

[format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[lint.isort]
known-first-party = ["pysophoscentralapi"]
force-single-line = false
lines-after-imports = 2

[lint.pylint]
max-args = 8
max-branches = 15
max-returns = 8
max-statements = 60
```

### 3.2 Type Checking Configuration (mypy.ini or pyproject.toml)

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict_equality = True
strict_concatenate = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-httpx.*]
ignore_missing_imports = True

[mypy-rich.*]
ignore_missing_imports = True
```

### 3.3 Pre-commit Configuration (.pre-commit-config.yaml)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.2.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, httpx, click]
        args: [--strict, --ignore-missing-imports]
```

### 3.4 Code Review Checklist

**For Author:**
- [ ] Code follows project style guide
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated (docstrings, README, etc.)
- [ ] Type hints added for all functions
- [ ] Error handling is appropriate
- [ ] No hardcoded values (use config/constants)
- [ ] Logging added where appropriate
- [ ] Security considerations addressed
- [ ] Performance implications considered

**For Reviewer:**
- [ ] Code is readable and maintainable
- [ ] Logic is correct and efficient
- [ ] Edge cases are handled
- [ ] Tests are comprehensive
- [ ] API is intuitive and consistent
- [ ] Documentation is clear
- [ ] No security vulnerabilities
- [ ] No breaking changes (or properly documented)
- [ ] Follows DRY principle
- [ ] Error messages are helpful

---

## 4. Testing Strategy

### 4.1 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── unit/                          # Unit tests (fast, isolated)
│   ├── test_core/
│   │   ├── test_auth.py
│   │   ├── test_client.py
│   │   ├── test_config.py
│   │   ├── test_exceptions.py
│   │   └── test_pagination.py
│   ├── test_api/
│   │   ├── test_endpoint/
│   │   │   ├── test_endpoints.py
│   │   │   ├── test_scans.py
│   │   │   └── test_tamper.py
│   │   └── test_common/
│   │       ├── test_alerts.py
│   │       ├── test_tenants.py
│   │       └── test_admins.py
│   ├── test_exporters/
│   │   ├── test_json_exporter.py
│   │   └── test_csv_exporter.py
│   └── test_cli/
│       ├── test_main.py
│       ├── test_endpoint_cmds.py
│       └── test_common_cmds.py
├── integration/                   # Integration tests (slower)
│   ├── test_endpoint_api.py
│   ├── test_common_api.py
│   └── test_cli_integration.py
└── fixtures/                      # Test data
    ├── responses/
    │   ├── endpoints.json
    │   ├── alerts.json
    │   └── tenants.json
    └── config/
        └── test_config.toml
```

### 4.2 Pytest Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --strict-markers
    --cov=pysophoscentralapi
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-branch
    --asyncio-mode=auto
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (slower, may need credentials)
    slow: Slow tests
    skip_ci: Skip in CI environment
asyncio_mode = auto
```

### 4.3 Test Coverage Goals

**Coverage Targets:**
- Overall: >90%
- Core modules: >95%
- API modules: >90%
- CLI modules: >85%
- Exporters: >95%

**Commands:**
```bash
# Run all tests with coverage
pytest

# Run only unit tests
pytest -m unit

# Run specific test file
pytest tests/unit/test_core/test_auth.py

# Run with verbose output
pytest -v

# Run and open coverage report
pytest && open htmlcov/index.html
```

### 4.4 Test Fixtures Best Practices

**conftest.py Example:**
```python
import pytest
from unittest.mock import Mock, AsyncMock
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.core.auth import AuthProvider


@pytest.fixture
def mock_auth_provider():
    """Mock auth provider"""
    auth = AsyncMock(spec=AuthProvider)
    auth.get_authorization_header.return_value = {
        "Authorization": "Bearer mock-token"
    }
    return auth


@pytest.fixture
def mock_http_client(mock_auth_provider):
    """Mock HTTP client"""
    client = AsyncMock(spec=HTTPClient)
    return client


@pytest.fixture
def sample_endpoint_response():
    """Sample endpoint API response"""
    return {
        "items": [
            {
                "id": "endpoint-123",
                "type": "computer",
                "hostname": "DESKTOP-TEST",
                "health": {"overall": "good"},
                "os": {
                    "isServer": False,
                    "platform": "windows",
                    "name": "Windows 10 Pro",
                    "majorVersion": 10,
                    "minorVersion": 0,
                    "build": 19045
                },
                "ipv4Addresses": ["192.168.1.100"],
                "macAddresses": ["00:11:22:33:44:55"],
                "tamperProtectionEnabled": True,
                "assignedProducts": [],
                "lastSeenAt": "2025-11-14T10:00:00.000Z"
            }
        ],
        "pages": {
            "current": 1,
            "size": 1,
            "total": 1,
            "maxSize": 1000
        }
    }


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file"""
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[auth]
client_id = "test-client-id"
client_secret = "test-client-secret"

[api]
region = "us"
""")
    return config_file
```

### 4.5 Mocking External Services

**HTTP Response Mocking:**
```python
import pytest
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_list_endpoints_success(mock_http_client, sample_endpoint_response):
    """Test successful endpoint listing"""
    # Setup mock
    mock_http_client.get.return_value = sample_endpoint_response
    
    # Create API client
    from pysophoscentralapi.api.endpoint.endpoints import EndpointAPI
    api = EndpointAPI(mock_http_client)
    
    # Call method
    result = await api.list_endpoints()
    
    # Assertions
    assert len(result.items) == 1
    assert result.items[0].id == "endpoint-123"
    mock_http_client.get.assert_called_once_with(
        "/endpoints",
        params={}
    )


@pytest.mark.asyncio
async def test_list_endpoints_with_filters(mock_http_client, sample_endpoint_response):
    """Test endpoint listing with filters"""
    mock_http_client.get.return_value = sample_endpoint_response
    
    from pysophoscentralapi.api.endpoint.endpoints import EndpointAPI
    from pysophoscentralapi.api.endpoint.models import HealthStatus
    api = EndpointAPI(mock_http_client)
    
    # Call with filters
    result = await api.list_endpoints(
        health_status=HealthStatus.GOOD,
        hostname_contains="DESKTOP"
    )
    
    # Check filters were passed
    call_args = mock_http_client.get.call_args
    assert call_args[1]["params"]["healthStatus"] == "good"
    assert call_args[1]["params"]["hostnameContains"] == "DESKTOP"
```

---

## 5. Documentation Standards

### 5.1 Docstring Format (Google Style)

**Module Docstring:**
```python
"""Endpoint API client module.

This module provides the EndpointAPI class for interacting with the
Sophos Central Endpoint API v1. It supports all endpoint management
operations including listing, filtering, scanning, and isolation.

Example:
    Basic usage::

        async with SophosClient(config) as client:
            endpoints = await client.endpoint.list_endpoints(
                health_status=HealthStatus.GOOD
            )

Attributes:
    DEFAULT_PAGE_SIZE (int): Default number of items per page
    MAX_PAGE_SIZE (int): Maximum allowed page size
"""
```

**Function/Method Docstring:**
```python
async def list_endpoints(
    self,
    page_size: int = 50,
    page_from_key: Optional[str] = None,
    health_status: Optional[HealthStatus] = None,
    endpoint_type: Optional[EndpointType] = None,
    hostname_contains: Optional[str] = None,
) -> PaginatedResponse[Endpoint]:
    """List endpoints with optional filtering.

    Retrieve a paginated list of endpoints from the Sophos Central API.
    Supports various filters to narrow down results.

    Args:
        page_size: Number of items per page (1-1000). Defaults to 50.
        page_from_key: Pagination cursor for fetching next page.
        health_status: Filter by endpoint health status.
        endpoint_type: Filter by endpoint type (computer, server, etc.).
        hostname_contains: Filter by hostname substring (case-insensitive).

    Returns:
        PaginatedResponse containing list of endpoints and pagination info.

    Raises:
        ValidationError: If parameters are invalid.
        RateLimitError: If API rate limit is exceeded.
        APIError: If API returns an error response.

    Example:
        >>> api = EndpointAPI(client)
        >>> result = await api.list_endpoints(
        ...     health_status=HealthStatus.BAD,
        ...     page_size=100
        ... )
        >>> for endpoint in result.items:
        ...     print(f"{endpoint.hostname}: {endpoint.health.overall}")
    """
```

**Class Docstring:**
```python
class EndpointAPI:
    """Sophos Central Endpoint API client.

    Provides methods for managing endpoints including listing, scanning,
    isolation, and tamper protection operations.

    This class handles all communication with the Endpoint API v1 endpoints
    and automatically manages pagination, error handling, and retry logic.

    Attributes:
        http_client: HTTP client for making API requests.
        base_path: Base URL path for endpoint API ("/endpoint/v1").

    Example:
        >>> async with SophosClient(config) as client:
        ...     endpoint_api = client.endpoint
        ...     endpoints = await endpoint_api.list_endpoints()
        ...     await endpoint_api.scan_endpoint("endpoint-id")
    """
```

### 5.2 README Structure

```markdown
# PySophosCentralApi

Brief project description (1-2 sentences)

[![PyPI version](badge-url)](link)
[![Python versions](badge-url)](link)
[![License](badge-url)](link)
[![Tests](badge-url)](link)
[![Coverage](badge-url)](link)

## Features

- Feature 1
- Feature 2
- Feature 3

## Installation

```bash
pip install pysophoscentralapi
```

## Quick Start

```python
# Quick example code
```

## Documentation

[Full documentation](link-to-docs)

## Usage Examples

### Example 1
### Example 2

## CLI Usage

```bash
# CLI examples
```

## Contributing

See [CONTRIBUTING.md](link)

## License

This project is licensed under the MIT License - see [LICENSE](link)

## Acknowledgments

- Credits
- Links
```

### 5.3 Changelog Format (change-log.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- New features in development

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes

## [1.1.0] - 2025-12-01

### Added
- CSV export with nested object flattening
- Alert filtering by severity
- Retry logic for rate-limited requests

### Fixed
- Token refresh edge case when token expires during request
- Pagination issue with empty result sets

## [1.0.0] - 2025-11-14

### Added
- Initial release
- Endpoint API support
- Common API support
- CLI interface
- JSON and CSV export
- Comprehensive documentation

[Unreleased]: https://github.com/user/repo/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/user/repo/releases/tag/v1.0.0
```

---

## 6. Continuous Integration (CI/CD)

### 6.1 GitHub Actions Workflow (.github/workflows/test.yml)

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv pip install -r requirements.piptools
        uv pip install -r requirements-development.piptools
        uv pip install -e .

    - name: Lint with ruff
      run: |
        ruff check .
        ruff format --check .

    - name: Type check with mypy
      run: |
        mypy src/pysophoscentralapi

    - name: Test with pytest
      run: |
        pytest --cov=pysophoscentralapi --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### 6.2 Release Workflow (.github/workflows/release.yml)

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine

    - name: Build package
      run: python -m build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
      run: twine upload dist/*

    - name: Create GitHub Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        draft: false
        prerelease: false
```

---

## 7. Performance Monitoring

### 7.1 Benchmarking

Create benchmarks to track performance over time:

```python
# tests/benchmarks/test_performance.py
import pytest
import asyncio
from pysophoscentralapi import SophosClient


@pytest.mark.benchmark
def test_list_endpoints_performance(benchmark, mock_http_client):
    """Benchmark endpoint listing"""
    async def run():
        api = EndpointAPI(mock_http_client)
        return await api.list_endpoints(page_size=100)
    
    result = benchmark(asyncio.run, run())
    assert len(result.items) > 0


@pytest.mark.benchmark
def test_pagination_performance(benchmark, mock_http_client):
    """Benchmark pagination through multiple pages"""
    async def run():
        api = EndpointAPI(mock_http_client)
        paginator = api.paginate_endpoints(page_size=50)
        items = []
        async for item in paginator.iter_items():
            items.append(item)
        return items
    
    result = benchmark(asyncio.run, run())
    assert len(result) > 0
```

### 7.2 Memory Profiling

```python
# tests/profiling/test_memory.py
import pytest
from memory_profiler import profile


@profile
def test_large_export_memory():
    """Profile memory usage during large export"""
    # Test code here
    pass
```

---

## 8. Release Checklist

### 8.1 Pre-Release

- [ ] All tests passing on all platforms
- [ ] Code coverage ≥90%
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped in `__version__.py`
- [ ] Version bumped in `pyproject.toml`
- [ ] No TODO or FIXME comments in main code
- [ ] All PRs merged to main
- [ ] Dependencies are up to date
- [ ] Security audit passed

### 8.2 Release

- [ ] Create release branch
- [ ] Final testing on release branch
- [ ] Create and push version tag
- [ ] CI/CD builds and tests pass
- [ ] Package published to PyPI
- [ ] GitHub release created
- [ ] Documentation deployed
- [ ] Release announcement prepared

### 8.3 Post-Release

- [ ] Verify package installation from PyPI
- [ ] Test basic functionality with installed package
- [ ] Update project website/docs
- [ ] Announce release (Twitter, Reddit, etc.)
- [ ] Monitor for issues
- [ ] Respond to user feedback

---

## 9. Common Development Tasks

### 9.1 Adding a New API Endpoint

1. **Update models** (if needed):
   ```python
   # src/pysophoscentralapi/api/endpoint/models.py
   class NewFeature(BaseModel):
       # Define model
   ```

2. **Add API method**:
   ```python
   # src/pysophoscentralapi/api/endpoint/endpoints.py
   async def new_feature(self, param: str) -> NewFeature:
       """Docstring"""
       response = await self.http_client.get(f"/new-endpoint/{param}")
       return NewFeature(**response)
   ```

3. **Add tests**:
   ```python
   # tests/unit/test_api/test_endpoint/test_endpoints.py
   @pytest.mark.asyncio
   async def test_new_feature():
       # Test implementation
   ```

4. **Update documentation**:
   - Add docstring
   - Update API reference
   - Add example to docs

5. **Run quality checks**:
   ```bash
   ruff format .
   ruff check --fix .
   pytest
   ```

### 9.2 Adding a New CLI Command

1. **Add command**:
   ```python
   # src/pysophoscentralapi/cli/endpoint_cmds.py
   @endpoint.command("new-command")
   @click.option("--option", help="Description")
   @click.pass_context
   async def new_command(ctx, option):
       """Command description"""
       # Implementation
   ```

2. **Add tests**:
   ```python
   # tests/unit/test_cli/test_endpoint_cmds.py
   def test_new_command(cli_runner):
       result = cli_runner.invoke(cli, ["endpoint", "new-command"])
       assert result.exit_code == 0
   ```

3. **Update documentation**:
   - Add to CLI reference
   - Add usage example

### 9.3 Updating Dependencies

```bash
# Update development dependencies
uv pip-compile requirements-development.piptools

# Update runtime dependencies
uv pip-compile requirements.piptools

# Reinstall all dependencies
uv pip install -r requirements.piptools
uv pip install -r requirements-development.piptools

# Run tests to ensure compatibility
pytest
```

---

## 10. Troubleshooting Common Issues

### 10.1 Import Errors

**Problem**: Module not found errors
**Solution**:
```bash
# Ensure package is installed in editable mode
pip install -e .

# Verify PYTHONPATH
echo $PYTHONPATH

# Reinstall dependencies
uv pip install -r requirements.piptools
```

### 10.2 Test Failures

**Problem**: Tests fail locally but pass in CI
**Solution**:
```bash
# Clean cache and artifacts
rm -rf .pytest_cache __pycache__ .ruff_cache
find . -type d -name "*.egg-info" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall package
pip uninstall pysophoscentralapi
pip install -e .

# Run tests with verbose output
pytest -vv
```

### 10.3 Linting Issues

**Problem**: Ruff formatting conflicts
**Solution**:
```bash
# Format all files
ruff format .

# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .
```

---

This development workflow document provides comprehensive guidance for maintaining high code quality, consistent practices, and smooth collaboration throughout the project lifecycle.

