# Development Guidelines

> **About**: This library provides access to the **International Honeywell Evohome** system, which is provided by **Resideo** (who licensed the Honeywell brand). It targets the international API at `international.clientmytcc.com`.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip and virtualenv

### Development Setup

```bash
# Clone the repository
git clone https://github.com/divyavanmahajan/clientmytcc.git
cd clientmytcc/python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

## Code Style

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Code Formatting

Use **Black** for automatic code formatting:

```bash
# Format all code
black clientmytcc/

# Check formatting without changes
black --check clientmytcc/
```

### Type Hints

All public functions and methods must have type hints:

```python
# Good
def get_zone(self, location_id: str, zone_id: str) -> Zone:
    """Get a specific zone by ID."""
    pass

# Bad
def get_zone(self, location_id, zone_id):
    """Get a specific zone by ID."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def set_zone_temperature(
    self,
    zone_id: str,
    temperature: float,
    permanent: bool = True,
) -> None:
    """
    Set the target temperature for a heating zone.
    
    Args:
        zone_id: The zone ID
        temperature: Target temperature in Celsius
        permanent: Whether to hold temperature permanently
        
    Raises:
        ZoneNotFoundError: If the zone is not found
        APIError: If the API returns an error
        
    Example:
        >>> client.set_zone_temperature("5211675", 21.0, permanent=True)
    """
    pass
```

## Code Quality Tools

### Linting with Flake8

```bash
# Run linter
flake8 clientmytcc/

# With specific rules
flake8 --max-line-length=100 clientmytcc/
```

### Type Checking with mypy

```bash
# Run type checker
mypy clientmytcc/

# Strict mode
mypy --strict clientmytcc/
```

### Running All Checks

```bash
# Format, lint, and type check
black clientmytcc/ && \
flake8 clientmytcc/ && \
mypy clientmytcc/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=clientmytcc --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::test_login_success

# Run with verbose output
pytest -v
```

### Writing Tests

#### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_client.py           # Client tests
├── test_models.py           # Model tests
└── test_exceptions.py       # Exception tests
```

#### Test Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

```python
# Good
def test_login_success():
    pass

def test_login_invalid_credentials():
    pass

# Bad
def login_test():
    pass
```

#### Using Fixtures

```python
import pytest
from clientmytcc import Client

@pytest.fixture
def client():
    """Create a client instance."""
    return Client()

@pytest.fixture
def mock_response():
    """Create a mock API response."""
    return {
        "Content": {
            "Locations": [
                {"Id": "123", "Name": "Home"}
            ]
        }
    }

def test_get_locations(client, mock_response, requests_mock):
    """Test getting locations."""
    requests_mock.get(
        "https://international.clientmytcc.com/api/locationsapi/getlocations",
        json=mock_response
    )
    
    locations = client.get_locations()
    assert len(locations) == 1
    assert locations[0].name == "Home"
```

#### Mocking HTTP Requests

Use `requests-mock` for mocking HTTP calls:

```python
def test_login(client, requests_mock):
    """Test login functionality."""
    # Mock login page
    requests_mock.get(
        "https://international.clientmytcc.com/Account/Login",
        text="<html></html>"
    )
    
    # Mock login API
    requests_mock.post(
        "https://international.clientmytcc.com/api/accountApi/login",
        json={"Content": {"UserId": "123"}}
    )
    
    result = client.login("user@example.com", "password")
    assert result["UserId"] == "123"
```

### Test Coverage

Target: **>80% coverage**

```bash
# Generate coverage report
pytest --cov=clientmytcc --cov-report=term-missing

# Generate HTML report
pytest --cov=clientmytcc --cov-report=html
open htmlcov/index.html
```

## Git Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactor: `refactor/description`

```bash
# Good
git checkout -b feature/add-async-support
git checkout -b fix/session-timeout
git checkout -b docs/update-readme

# Bad
git checkout -b new-feature
git checkout -b bugfix
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**

```bash
# Good
git commit -m "feat(client): add async support for API calls"
git commit -m "fix(auth): handle session expiry correctly"
git commit -m "docs(readme): update installation instructions"

# Bad
git commit -m "updated code"
git commit -m "fixes"
```

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Run tests and checks**
   ```bash
   pytest
   black clientmytcc/
   flake8 clientmytcc/
   mypy clientmytcc/
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

5. **PR checklist:**
   - [ ] Tests pass
   - [ ] Code formatted with Black
   - [ ] Type hints added
   - [ ] Docstrings updated
   - [ ] CHANGELOG updated (if applicable)

## Project Structure

```
python/
├── clientmytcc/      # Main package
│   ├── __init__.py            # Package exports
│   ├── client.py              # API client
│   ├── models.py              # Data models
│   └── exceptions.py          # Custom exceptions
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Shared fixtures
│   ├── test_client.py        # Client tests
│   ├── test_models.py        # Model tests
│   └── test_exceptions.py    # Exception tests
├── examples/                  # Usage examples
│   └── basic_usage.py
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPMENT.md
│   └── WALKTHROUGH.md
├── pyproject.toml            # Package configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Dev dependencies
├── .gitignore               # Git ignore patterns
├── LICENSE                  # MIT License
└── README.md                # Main documentation
```

## Adding New Features

### 1. Add New API Endpoint

```python
# In client.py
def new_endpoint(self, param: str) -> ReturnType:
    """
    Description of what this endpoint does.
    
    Args:
        param: Parameter description
        
    Returns:
        Description of return value
        
    Raises:
        APIError: If the API returns an error
    """
    data = self._make_request("GET", "/api/path", params={"param": param})
    return ReturnType.from_dict(data)
```

### 2. Add New Model

```python
# In models.py
@dataclass
class NewModel:
    """Description of the model."""
    
    id: str
    name: str
    value: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "NewModel":
        """Create instance from API response."""
        return cls(
            id=data.get("Id", ""),
            name=data.get("Name", ""),
            value=data.get("Value"),
        )
```

### 3. Add Tests

```python
# In tests/test_client.py
def test_new_endpoint(client, requests_mock):
    """Test new endpoint."""
    requests_mock.get(
        "https://international.clientmytcc.com/api/path",
        json={"Content": {"Id": "123", "Name": "Test"}}
    )
    
    result = client.new_endpoint("param")
    assert result.id == "123"
    assert result.name == "Test"
```

### 4. Update Documentation

- Add to README.md API Reference
- Add example to USER_GUIDE.md
- Update CHANGELOG.md

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (2.0.0)
- **MINOR**: New features, backward compatible (1.1.0)
- **PATCH**: Bug fixes (1.0.1)

### Updating Version

Update in both files:

1. `pyproject.toml`:
   ```toml
   [project]
   version = "0.2.0"
   ```

2. `clientmytcc/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

## Release Process

### 1. Prepare Release

```bash
# Update version
# Update CHANGELOG.md
# Commit changes
git add .
git commit -m "chore: bump version to 0.2.0"
git tag v0.2.0
```

### 2. Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

### 3. Test on TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ clientmytcc
```

### 4. Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Push tags
git push origin main --tags
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Your code here
```

### Inspect HTTP Requests

```python
import requests

# Enable HTTP debugging
import http.client as http_client
http_client.HTTPConnection.debuglevel = 1

# Your code here
```

### Use Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()
```

## Common Issues

### Import Errors

```bash
# Reinstall in development mode
pip install -e .
```

### Test Failures

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv
```

### Type Check Errors

```bash
# Ignore specific errors
# type: ignore

# Or add to pyproject.toml
[tool.mypy]
ignore_missing_imports = true
```

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 8 Style Guide](https://pep8.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [mypy Type Checker](https://mypy.readthedocs.io/)

## Getting Help

- [User Guide](USER_GUIDE.md)
- [Architecture](ARCHITECTURE.md)
- [Issue Tracker](https://github.com/divyavanmahajan/clientmytcc/issues)
- [Discussions](https://github.com/divyavanmahajan/clientmytcc/discussions)
