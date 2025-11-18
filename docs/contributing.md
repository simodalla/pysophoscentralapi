# Contributing to PySophosCentralApi

Thank you for considering contributing to PySophosCentralApi! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- uv (recommended) or pip

### Development Setup

1. **Fork the Repository**

   Fork the repository on GitHub and clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/pysophoscentralapi.git
   cd pysophoscentralapi
   ```

2. **Add Upstream Remote**

   ```bash
   git remote add upstream https://github.com/original/pysophoscentralapi.git
   ```

3. **Create Virtual Environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install Dependencies**

   ```bash
   # Using uv (recommended)
   pip install uv
   uv pip install -r requirements.piptools
   uv pip install -r requirements-development.piptools

   # Or using pip
   pip install -r requirements.piptools
   pip install -r requirements-development.piptools
   ```

5. **Install in Editable Mode**

   ```bash
   pip install -e .
   ```

6. **Verify Setup**

   ```bash
   # Run tests
   pytest

   # Check linting
   ruff check .

   # Check formatting
   ruff format --check .
   ```

## Development Workflow

### 1. Create a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Your Changes

- Write clear, concise code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/unit/test_core/test_client.py

# Run with verbose output
pytest -v
```

### 4. Format and Lint

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Fix linting issues automatically
ruff check --fix .

# Type checking (if mypy is configured)
mypy src
```

### 5. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add endpoint filtering by OS type"
```

Commit message format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(endpoint): add support for Windows Server filtering

Add new filter option to EndpointFilters for Windows Server
operating systems. Includes tests and documentation updates.

Closes #123
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

We follow PEP 8 with some modifications enforced by Ruff:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Organized by standard library, third-party, local

### Type Hints

All public functions must have type hints:

```python
def process_endpoint(endpoint_id: str, config: Config) -> Endpoint:
    """Process an endpoint.
    
    Args:
        endpoint_id: The endpoint ID
        config: Configuration object
        
    Returns:
        Processed endpoint
        
    Raises:
        ResourceNotFoundError: If endpoint not found
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def calculate_risk_score(
    endpoint: Endpoint,
    alerts: list[Alert],
    threshold: float = 0.5
) -> float:
    """Calculate risk score for an endpoint.
    
    The risk score is calculated based on the endpoint's health status
    and associated alerts. Higher scores indicate greater risk.
    
    Args:
        endpoint: The endpoint to analyze
        alerts: List of alerts for the endpoint
        threshold: Risk threshold (0.0 to 1.0, default: 0.5)
        
    Returns:
        Risk score between 0.0 and 1.0
        
    Raises:
        ValueError: If threshold is not between 0.0 and 1.0
        
    Examples:
        >>> endpoint = Endpoint(id="123", health=HealthStatus.BAD)
        >>> alerts = [Alert(severity=Severity.HIGH)]
        >>> score = calculate_risk_score(endpoint, alerts)
        >>> print(f"Risk score: {score}")
    """
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")
    ...
```

### Import Organization

Imports should be organized in three groups:

```python
# Standard library
import asyncio
from datetime import datetime
from pathlib import Path

# Third-party
import httpx
from pydantic import BaseModel

# Local/project
from pysophoscentralapi.core import Config
from pysophoscentralapi.core.exceptions import SophosAPIException
```

### Project Import Style

**Functions**: Use namespace imports
```python
from pysophoscentralapi.services import discord_service
result = discord_service.load_config()
```

**Classes/Exceptions**: Use direct imports
```python
from pysophoscentralapi.core.exceptions import AuthenticationError
raise AuthenticationError('Invalid credentials')
```

## Testing

### Writing Tests

- Place tests in `tests/unit/` or `tests/integration/`
- Mirror the structure of `src/pysophoscentralapi/`
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert

Example:

```python
import pytest
from pysophoscentralapi.core.config import Config, AuthConfig

class TestConfig:
    """Tests for Config class."""
    
    def test_from_file_loads_valid_config(self, tmp_path):
        """Test loading configuration from valid file."""
        # Arrange
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
        [auth]
        client_id = "test-id"
        client_secret = "test-secret"
        """)
        
        # Act
        config = Config.from_file(config_file)
        
        # Assert
        assert config.auth.client_id == "test-id"
        assert config.auth.client_secret == "test-secret"
    
    def test_from_file_raises_on_missing_file(self):
        """Test that missing file raises appropriate error."""
        # Arrange
        missing_file = Path("/nonexistent/config.toml")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            Config.from_file(missing_file)
```

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/unit/test_core/

# Specific test
pytest tests/unit/test_core/test_config.py::TestConfig::test_from_file

# With coverage
pytest --cov=src/pysophoscentralapi --cov-report=html

# Fast fail (stop on first failure)
pytest -x

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Test Coverage

We aim for >90% test coverage. Check coverage:

```bash
pytest --cov=src/pysophoscentralapi --cov-report=term-missing
```

## Documentation

### Docstring Style

- Use Google-style docstrings
- Document all public APIs
- Include examples where helpful
- Document exceptions

### Documentation Files

Update relevant documentation:

- `README.md` - High-level overview
- `docs/` - Detailed guides
- `CHANGELOG.md` - Keep updated
- Code comments - For complex logic

### Building Documentation

```bash
# Generate API docs (if using mkdocs)
mkdocs build

# Serve locally
mkdocs serve
```

## Pull Request Process

### Before Submitting

1. ✅ All tests pass (`pytest`)
2. ✅ Code is formatted (`ruff format .`)
3. ✅ No linting errors (`ruff check .`)
4. ✅ Documentation is updated
5. ✅ CHANGELOG.md is updated
6. ✅ Commits are clean and descriptive

### PR Template

When creating a PR, include:

**Description**
- What does this PR do?
- Why is this change needed?

**Type of Change**
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

**Testing**
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing performed

**Checklist**
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge

### After Merge

1. Delete your branch
2. Update your fork:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Development Tips

### Debugging

Use `--debug` flag for verbose output:

```bash
pysophos --debug endpoint list
```

In code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### IDE Setup

**VS Code** - Recommended settings (`.vscode/settings.json`):

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": true,
      "source.organizeImports": true
    }
  },
  "python.testing.pytestEnabled": true
}
```

### Common Tasks

```bash
# Update dependencies
uv pip-compile requirements.piptools -o requirements.txt
uv pip-compile requirements-development.piptools -o requirements-dev.txt

# Clean build artifacts
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .coverage htmlcov

# Run specific test pattern
pytest -k "test_endpoint"
```

## Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/yourusername/pysophoscentralapi/discussions)
- **Bugs**: Open an [Issue](https://github.com/yourusername/pysophoscentralapi/issues)
- **Chat**: Join our community (link TBD)

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation

Thank you for contributing! 🎉

---

**Questions?** Open a discussion or reach out to the maintainers.

