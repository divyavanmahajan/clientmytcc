# MyTotalConnectComfort API Client

A comprehensive Python client library and API documentation for the **International Honeywell Evohome** heating system, provided by **Resideo** (who licensed the Honeywell brand).

> **Note**: This is for the international version accessible via `international.mytotalconnectcomfort.com`. North American systems may use different endpoints.

## Repository Contents

### Python Client Library (`python/`)

A production-ready Python package for controlling your Evohome heating system programmatically.

**Features:**
- Simple authentication with email and password
- Location and zone management
- Temperature control (permanent and temporary)
- Real-time status monitoring
- Type-safe with full type hints
- Comprehensive error handling

**Quick Start:**
```python
from mytotalconnectcomfort import Client

client = Client()
client.login("your-email@example.com", "your-password")

locations = client.get_locations()
for location in locations:
    system = client.get_location_system(location.id)
    for zone in system.zones:
        print(f"{zone.name}: {zone.temperature}°C → {zone.target_temperature}°C")
```

**Documentation:**
- [Python Client README](python/README.md) - Installation and usage
- [User Guide](python/docs/USER_GUIDE.md) - Comprehensive guide with examples
- [Architecture](python/docs/ARCHITECTURE.md) - Design and technical details
- [Development Guidelines](python/docs/DEVELOPMENT.md) - Contributing and development

### API Documentation (`api/`)

Complete documentation of the MyTotalConnectComfort API endpoints.

- [API Documentation](api/API_DOCUMENTATION.md) - All endpoints with request/response examples
- [OpenAPI Specification](api/openapi-spec.yaml) - Machine-readable API spec

## Installation

### From PyPI (when published)

```bash
pip install mytotalconnectcomfort
```

### From Source

```bash
git clone https://github.com/divyavanmahajan/mytotalconnectcomfort.git
cd mytotalconnectcomfort/python
pip install -e .
```

## Requirements

- Python 3.8 or higher
- `requests` library (only dependency)

## Usage Example

```python
from mytotalconnectcomfort import Client

# Authenticate
client = Client()
client.login("user@example.com", "password")

# Get locations
locations = client.get_locations()
location = locations[0]

# Get system status
system = client.get_location_system(location.id)

# Set temperature
client.set_zone_temperature(
    zone_id=system.zones[0].id,
    temperature=21.0,
    permanent=True
)
```

## Project Structure

```
mytotalconnectcomfort/
├── api/                          # API documentation
│   ├── API_DOCUMENTATION.md      # Complete API reference
│   └── openapi-spec.yaml         # OpenAPI specification
├── python/                       # Python client library
│   ├── mytotalconnectcomfort/    # Main package
│   │   ├── __init__.py
│   │   ├── client.py             # API client
│   │   ├── models.py             # Data models
│   │   └── exceptions.py         # Custom exceptions
│   ├── tests/                    # Unit tests
│   ├── examples/                 # Usage examples
│   ├── docs/                     # Library documentation
│   ├── pyproject.toml            # Package configuration
│   └── README.md                 # Library documentation
└── README.md                     # This file
```

## Features

### Authentication
- Cookie-based session management
- Automatic CSRF token handling
- Session refresh support

### Location Management
- List all locations (homes)
- Get detailed location information
- Access gateway devices

### Zone Control
- Read current and target temperatures
- Set permanent temperature overrides
- Set temporary temperature holds
- Monitor zone status and alerts

### Error Handling
- Custom exception hierarchy
- Clear error messages
- Automatic session expiry detection

## About the System

The **Evohome** heating control system is provided by **Resideo Technologies, Inc.**, who licensed the Honeywell brand from Honeywell International Inc. This library interfaces with the international version of the MyTotalConnectComfort service.

### Supported Systems
- International Honeywell Evohome (via `international.mytotalconnectcomfort.com`)
- Evohome thermostats and zone controllers
- Multi-zone heating systems

### Not Supported
- North American Honeywell systems (different API endpoints)
- Cooling/AC systems
- Domestic hot water control (limited support)

## Development

### Setup Development Environment

```bash
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
cd python
pytest
pytest --cov=mytotalconnectcomfort --cov-report=html
```

### Code Quality

```bash
# Format code
black mytotalconnectcomfort/

# Type checking
mypy mytotalconnectcomfort/

# Linting
flake8 mytotalconnectcomfort/
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [Development Guidelines](python/docs/DEVELOPMENT.md) for detailed instructions.

## License

This project is licensed under the MIT License - see the [LICENSE](python/LICENSE) file for details.

## Disclaimer

This is an unofficial library and is not affiliated with, endorsed by, or connected to Honeywell International, Resideo Technologies, or any of their subsidiaries.

**About the Evohome System**: The Evohome heating control system is provided by Resideo Technologies, Inc., who licensed the Honeywell brand from Honeywell International Inc. This library interfaces with the international version of the MyTotalConnectComfort service.

Use this library at your own risk.

## Support

- [API Documentation](api/API_DOCUMENTATION.md)
- [Python Client Documentation](python/README.md)
- [Issue Tracker](https://github.com/divyavanmahajan/mytotalconnectcomfort/issues)
- [Discussions](https://github.com/divyavanmahajan/mytotalconnectcomfort/discussions)

## Acknowledgments

- Thanks to the MyTotalConnectComfort API for providing access to Evohome systems
- Inspired by the need for home automation and energy efficiency
- Built with Python and the `requests` library
