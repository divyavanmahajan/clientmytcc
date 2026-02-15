# AGENT.md - evohome_py (Python Package)

## Package Overview

**evohome_py** is a pure Python client library for the International Honeywell Evohome heating system API. It provides both a programmatic API and a command-line interface.

### Key Information

- **Package Name**: `evohome_py`
- **PyPI**: https://pypi.org/p/evohome_py
- **Current Version**: 0.2.2
- **Python Requirement**: >=3.8
- **Dependencies**: `requests`, `click`, `rich`, `tomli`, `tomli-w`
- **CLI Commands**: `evohome` and `evohome_py`

## Project Structure

```
python/
├── evohome_py/              # Main package
│   ├── __init__.py          # Package init, exports, __version__
│   ├── client.py            # API client implementation
│   ├── models.py            # Data models (Zone, Location, UserInfo, etc.)
│   ├── exceptions.py        # Custom exceptions
│   ├── cli.py               # Click-based CLI
│   ├── config.py            # Configuration management
│   ├── session_manager.py   # Session persistence
│   └── utils.py             # Utility functions
├── tests/                   # Test suite
│   ├── test_client.py
│   ├── test_models.py
│   ├── test_cli.py
│   └── conftest.py          # Pytest fixtures
├── examples/                # Usage examples
│   └── basic_usage.py
├── docs/                    # Documentation
├── pyproject.toml           # Package configuration
├── pytest.ini               # Pytest configuration
└── README.md                # Package documentation
```

## Development Setup

### Initial Setup

```bash
cd python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=evohome_py --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black evohome_py/ tests/

# Type checking
mypy evohome_py/

# Linting
flake8 evohome_py/
```

## Key Components

### 1. Client (`client.py`)

The main API client class that handles all HTTP communication.

**Key Methods**:
- `login(email, password)`: Authenticate and create session
- `get_locations()`: Retrieve all locations
- `get_location_system(location_id)`: Get zones and system status
- `set_zone_temperature(...)`: Control zone temperature
- `get_account_info()`: Get user account details

**Session Management**:
- Uses `requests.Session` for cookie-based auth
- Automatically handles CSRF tokens
- Session can be persisted via `session_manager.py`

### 2. Models (`models.py`)

Data classes representing API entities.

**Main Models**:
- `Zone`: Heating zone with temperature, status, alerts
- `Location`: Home location with zones and gateways
- `UserInfo`: User account information
- `Gateway`: Gateway device information

**Design Pattern**: Dataclasses with `from_dict()` class methods for JSON deserialization.

### 3. CLI (`cli.py`)

Command-line interface built with Click.

**Command Structure**:
```
evohome
├── login         # Authenticate and save session
├── logout        # Clear session
├── locations     # List all locations
├── account       # Show account info
├── monitor       # Monitor zone temperatures
├── set           # Set zone temperature
├── boost         # Boost all zones
├── eco           # Enable eco mode
├── vacation      # Enable vacation mode
├── schedule      # Reset to schedule
└── config        # Manage configuration
```

**Session Storage**: `~/.config/evohome_py/session.json`

### 4. Exceptions (`exceptions.py`)

Custom exception hierarchy for error handling.

```python
MyTotalConnectComfortError (base)
├── AuthenticationError
├── APIError
├── ZoneNotFoundError
├── LocationNotFoundError
└── SessionExpiredError
```

## Common Development Tasks

### Adding a New API Endpoint

1. **Add method to `Client` class**:
```python
def new_endpoint(self, param: str) -> Dict[str, Any]:
    \"\"\"Description of endpoint.\"\"\"
    response = self.session.get(f"{self.base_url}/api/new/{param}")
    response.raise_for_status()
    return response.json()
```

2. **Add model if needed** (`models.py`):
```python
@dataclass
class NewModel:
    field1: str
    field2: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NewModel':
        return cls(
            field1=data['field1'],
            field2=data['field2']
        )
```

3. **Add tests** (`tests/test_client.py`):
```python
def test_new_endpoint(mock_client):
    result = mock_client.new_endpoint("test")
    assert result is not None
```

4. **Add CLI command** (if applicable):
```python
@cli.command()
@click.option('--param', required=True)
def new_command(param):
    \"\"\"Description.\"\"\"
    client = get_client()
    result = client.new_endpoint(param)
    console.print(result)
```

### Updating Version

**Files to update**:
1. `pyproject.toml` → `version = "X.Y.Z"`
2. `evohome_py/__init__.py` → `__version__ = "X.Y.Z"`

**Also update Rust package** (see `../rust/AGENT.md`)

### Testing with Real API

```bash
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
pytest tests/test_integration.py  # If integration tests exist
```

## CLI Development

### Adding a New Command

1. **Define command in `cli.py`**:
```python
@cli.command()
@click.option('--option1', help='Description')
@click.pass_context
def new_command(ctx, option1):
    \"\"\"Command description.\"\"\"
    client = get_client()
    # Implementation
```

2. **Add to help text**: Ensure docstring is clear

3. **Test manually**:
```bash
evohome new-command --option1 value
```

### CLI Best Practices

- Use `rich` for formatted output (tables, colors)
- Handle errors gracefully with try/except
- Provide helpful error messages
- Support `--help` for all commands
- Use `click.confirm()` for destructive operations

## Testing Strategy

### Unit Tests

Mock HTTP responses using `unittest.mock`:

```python
@patch('evohome_py.client.requests.Session.get')
def test_get_locations(mock_get):
    mock_get.return_value.json.return_value = [...]
    client = Client()
    locations = client.get_locations()
    assert len(locations) > 0
```

### Integration Tests

Use real credentials (not committed):

```python
@pytest.mark.skipif(not os.getenv('EVOHOME_EMAIL'), reason="No credentials")
def test_real_login():
    client = Client()
    client.login(os.getenv('EVOHOME_EMAIL'), os.getenv('EVOHOME_PASSWORD'))
    assert client.session.cookies
```

### Test Fixtures (`conftest.py`)

```python
@pytest.fixture
def mock_client():
    client = Client()
    client.session.cookies.set('sessionId', 'test-session')
    return client
```

## Publishing

### Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

### Test on TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ evohome_py
```

### Publish to PyPI

**Automated** (via GitHub Actions):
- Push tag `vX.Y.Z` triggers `.github/workflows/pypi.yml`
- Workflow builds and publishes automatically

**Manual**:
```bash
python -m twine upload dist/*
```

## Configuration Files

### `pyproject.toml`

**Key sections**:
- `[project]`: Package metadata, version, dependencies
- `[project.scripts]`: CLI entry points (`evohome` and `evohome_py`)
- `[project.optional-dependencies]`: Dev dependencies
- `[tool.setuptools.packages.find]`: Package discovery
- `[tool.black]`, `[tool.mypy]`: Tool configurations

### `pytest.ini`

Pytest configuration:
- Test discovery patterns
- Coverage settings
- Markers for test categories

## Common Issues

### Import Errors After Install

**Problem**: `ModuleNotFoundError: No module named 'evohome_py'`

**Solution**:
```bash
pip install --upgrade evohome_py
# Or for development:
pip install -e .
```

### CLI Command Not Found

**Problem**: `evohome: command not found`

**Solution**:
```bash
# Ensure package is installed
pip install evohome_py

# Check PATH
which evohome

# Reinstall if needed
pip uninstall evohome_py
pip install evohome_py
```

### Session Expired

**Problem**: API returns 401 after some time

**Solution**: The client should detect this and raise `SessionExpiredError`. User needs to re-login.

## Code Style Guidelines

### Formatting
- Use `black` with default settings (line length 100, see `pyproject.toml`)
- Follow PEP 8

### Type Hints
- Use type hints for all function signatures
- Import from `typing` module
- Run `mypy` to verify

### Docstrings
- Use Google-style docstrings
- Include Args, Returns, Raises sections
- Example:
```python
def set_temperature(zone_id: str, temp: float) -> None:
    \"\"\"Set the target temperature for a zone.
    
    Args:
        zone_id: The unique identifier for the zone
        temp: Target temperature in Celsius
        
    Raises:
        ZoneNotFoundError: If zone_id is invalid
        APIError: If the API request fails
    \"\"\"
```

### Error Handling
- Raise specific exceptions (not generic `Exception`)
- Provide helpful error messages
- Log errors when appropriate

## Dependencies

### Runtime Dependencies
- `requests>=2.31.0`: HTTP client
- `click>=8.1.0`: CLI framework
- `rich>=13.0.0`: Terminal formatting
- `tomli>=2.0.0`: TOML parsing (Python <3.11)
- `tomli-w>=1.0.0`: TOML writing

### Dev Dependencies
- `pytest>=7.0.0`: Testing framework
- `black>=22.0.0`: Code formatter
- `mypy>=0.990`: Type checker
- `flake8>=5.0.0`: Linter
- `build>=0.10.0`: Package builder
- `twine>=4.0.0`: PyPI uploader

## Related Files

- **Root AGENT.md**: `../AGENT.md` (repository-level context)
- **Rust AGENT.md**: `../rust/AGENT.md` (Rust package context)
- **API Docs**: `../api/API_DOCUMENTATION.md`
- **User Guide**: `docs/USER_GUIDE.md` (if exists)

## Maintenance Checklist

When making changes:
- [ ] Update version in `pyproject.toml` and `__init__.py`
- [ ] Update Rust version to match (see `../rust/AGENT.md`)
- [ ] Add/update tests
- [ ] Run `black`, `mypy`, `flake8`
- [ ] Update documentation
- [ ] Update CHANGELOG (if exists)
- [ ] Test CLI commands manually
- [ ] Create PR with conventional commit message
