# MyTotalConnectComfort Python Client

A Python client library for the **MyTotalConnectComfort** API, which provides access to the **International Honeywell Evohome** heating system. This system is provided by **Resideo**, who licensed the Honeywell brand. Control your heating zones, monitor temperatures, and manage your home heating system programmatically.

> **Note**: This library is designed for the international Evohome system accessible via `international.evohome_py.com`. North American systems may require different endpoints.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Simple Authentication** - Easy login with email and password
- **Location Management** - Retrieve and manage multiple locations (homes)
- **Zone Control** - Read temperatures and set target temperatures for heating zones
- **Real-time Status** - Monitor current temperatures, alerts, and system status
- **Session Management** - Automatic cookie-based session handling
- **Type-Safe** - Full type hints for better IDE support
- **Zero Dependencies** - Only requires `requests` library

## Installation

### From PyPI (when published)

```bash
pip install evohome_py
```

### From Source

```bash
git clone https://github.com/divyavanmahajan/clientmytcc.git
cd clientmytcc/python
pip install -e .
```

## CLI Usage
The package includes a command-line interface (CLI) for controlling your heating system directly from the terminal.

### Basic Commands
```bash
# Login (saves session to ~/.config/evohome_py/session.json)
evohome_py login --email user@example.com

# List locations
evohome_py locations

# Monitor all zones in the first location
evohome_py monitor

# Logout (clears session)
evohome_py logout
```

### Temperature Control
```bash
# Set temperature for a specific zone
evohome_py set --zone "Living Room" --temp 21.0

# Boost all zones in a location
evohome_py boost --temp 22.0 --duration 2

# Enable Eco mode (lowers temp to 18.0°C)
evohome_py eco

# Enable Vacation mode (lowers temp to 12.0°C)
evohome_py vacation --temp 12.0

# Reset all zones to follow schedule
evohome_py schedule
```

## Quick Start

```python
from evohome_py import Client

# Create a client and login
client = Client()
client.login("your-email@example.com", "your-password")

# Get all locations
locations = client.get_locations()
for location in locations:
    print(f"{location.name}: {len(location.zones)} zones")

# Get detailed system information
location_id = locations[0].id
system = client.get_location_system(location_id)

# Display zone temperatures
for zone in system.zones:
    print(f"{zone.name}: {zone.temperature}°C → {zone.target_temperature}°C")

# Set a zone temperature
client.set_zone_temperature(
    zone_id=system.zones[0].id,
    temperature=21.0,
    permanent=True
)
```

## Usage Examples

### Authentication

```python
from evohome_py import Client
from evohome_py.exceptions import AuthenticationError

client = Client()

try:
    client.login("user@example.com", "password")
    print("Login successful!")
except AuthenticationError as e:
    print(f"Login failed: {e}")
```

### List All Locations and Zones

```python
# Get all locations
locations = client.get_locations()

for location in locations:
    print(f"\nLocation: {location.name}")
    print(f"  Address: {location.street_address}, {location.city}")
    print(f"  Zones: {len(location.zones)}")
    
    for zone in location.zones:
        status = "Online" if zone.is_alive else "Offline"
        print(f"    - {zone.name}: {zone.temperature}°C ({status})")
```

### Get Zone by Name

```python
# Find a specific zone by name
zone = client.get_zone_by_name(location_id="1232176", zone_name="Livingroom")
print(f"{zone.name}: {zone.temperature}°C")
```

### Set Temperature (Permanent)

```python
# Set temperature permanently
client.set_zone_temperature(
    zone_id="5211675",
    temperature=21.5,
    permanent=True
)
```

### Set Temperature (Temporary)

```python
# Set temperature for 2 hours
client.set_zone_temperature(
    zone_id="5211675",
    temperature=22.0,
    permanent=False,
    duration_hours=2,
    duration_minutes=0
)
```

### Monitor Zone Status

```python
zone = client.get_zone(location_id="1232176", zone_id="5211675")

print(f"Zone: {zone.name}")
print(f"  Current: {zone.temperature}°C")
print(f"  Target: {zone.target_temperature}°C")
print(f"  Range: {zone.min_temperature}°C - {zone.max_temperature}°C")
print(f"  Override Active: {zone.override_active}")
print(f"  Alerts: {zone.has_alerts}")
```

### Get Account Information

```python
account = client.get_account_info()
print(f"Name: {account.first_name} {account.last_name}")
print(f"Email: {account.username}")
print(f"Location: {account.city}, {account.country_name}")
```

## API Reference

### Client Class

#### `Client()`
Initialize a new API client.

#### `login(email: str, password: str) -> Dict[str, Any]`
Authenticate with the MyTotalConnectComfort API.

**Parameters:**
- `email`: User email address
- `password`: User password

**Returns:** User information dictionary

**Raises:** `AuthenticationError` if login fails

#### `get_locations() -> List[Location]`
Get all locations associated with the account.

**Returns:** List of `Location` objects

#### `get_location(location_id: str) -> Location`
Get detailed information about a specific location.

**Parameters:**
- `location_id`: The location ID

**Returns:** `Location` object with detailed information

#### `get_location_system(location_id: str) -> Location`
Get the heating system configuration and zone status for a location.

**Parameters:**
- `location_id`: The location ID

**Returns:** `Location` object with zones and system status

#### `get_account_info() -> UserInfo`
Get account information for the authenticated user.

**Returns:** `UserInfo` object

#### `set_zone_temperature(zone_id: str, temperature: float, permanent: bool = True, ...)`
Set the target temperature for a heating zone.

**Parameters:**
- `zone_id`: The zone ID
- `temperature`: Target temperature in Celsius
- `permanent`: Whether to hold temperature permanently (default: `True`)
- `duration_hours`: Hours to hold temperature (if not permanent)
- `duration_minutes`: Minutes to hold temperature (if not permanent)
- `location_time_offset_minutes`: Time zone offset in minutes (default: 60)

#### `get_zone(location_id: str, zone_id: str) -> Zone`
Get a specific zone by ID.

**Returns:** `Zone` object

**Raises:** `ZoneNotFoundError` if zone not found

#### `get_zone_by_name(location_id: str, zone_name: str) -> Zone`
Get a specific zone by name.

**Returns:** `Zone` object

**Raises:** `ZoneNotFoundError` if zone not found

### Data Models

#### `Zone`
Represents a heating zone (room).

**Attributes:**
- `id`: Zone ID
- `name`: Zone name
- `temperature`: Current temperature (°C)
- `target_temperature`: Target temperature (°C)
- `min_temperature`: Minimum allowed temperature
- `max_temperature`: Maximum allowed temperature
- `is_alive`: Whether the zone is online
- `has_alerts`: Whether there are active alerts
- `override_active`: Whether manual override is active
- `hold_permanently`: Whether temperature is held permanently

#### `Location`
Represents a location (home) with heating zones.

**Attributes:**
- `id`: Location ID
- `name`: Location name
- `city`: City name
- `country`: Country name
- `zones`: List of `Zone` objects
- `gateways`: List of `Gateway` objects

**Methods:**
- `get_zone_by_id(zone_id: str) -> Optional[Zone]`
- `get_zone_by_name(name: str) -> Optional[Zone]`

#### `UserInfo`
Represents user account information.

**Attributes:**
- `username`: User email
- `first_name`: First name
- `last_name`: Last name
- `city`: City
- `country_name`: Country name

### Exceptions

- `MyTotalConnectComfortError`: Base exception
- `AuthenticationError`: Authentication failed
- `APIError`: API returned an error
- `ZoneNotFoundError`: Zone not found
- `LocationNotFoundError`: Location not found
- `SessionExpiredError`: Session expired

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/divyavanmahajan/evohome_py.git
cd evohome_py/python

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code with black
black evohome_py/

# Type checking with mypy
mypy evohome_py/

# Linting with flake8
flake8 evohome_py/
```

### Running Examples

```bash
# Edit examples/basic_usage.py with your credentials
cd examples
python basic_usage.py
```

## Publishing to PyPI

### Prerequisites

1. Create accounts on [PyPI](https://pypi.org/) and [TestPyPI](https://test.pypi.org/)
2. Install build tools:
   ```bash
   pip install build twine
   ```

### Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build
```

This creates two files in the `dist/` directory:
- `evohome_py-0.1.0.tar.gz` (source distribution)
- `evohome_py-0.1.0-py3-none-any.whl` (wheel distribution)

### Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ evohome_py
```

### Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

### Using API Tokens (Recommended)

Instead of username/password, use API tokens:

1. Generate an API token on PyPI (Account Settings → API tokens)
2. Create `~/.pypirc`:
   ```ini
   [pypi]
   username = __token__
   password = pypi-your-api-token-here
   
   [testpypi]
   username = __token__
   password = pypi-your-test-api-token-here
   ```

3. Upload:
   ```bash
   python -m twine upload dist/*
   ```

### Version Management

Update version in `pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

Also update in `evohome_py/__init__.py`:
```python
__version__ = "0.2.0"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is an unofficial library and is not affiliated with, endorsed by, or connected to Honeywell International, Resideo Technologies, or any of their subsidiaries. 

**About the Evohome System**: The Evohome heating control system is provided by Resideo Technologies, Inc., who licensed the Honeywell brand from Honeywell International Inc. This library interfaces with the international version of the MyTotalConnectComfort service.

Use this library at your own risk.

## Support

- [API Documentation](../api/API_DOCUMENTATION.md)
- [OpenAPI Specification](../api/openapi-spec.yaml)
- [Issue Tracker](https://github.com/divyavanmahajan/evohome_py/issues)

## Acknowledgments

- Thanks to the MyTotalConnectComfort API for providing access to Honeywell Evohome systems
- Inspired by the need for home automation and energy efficiency
