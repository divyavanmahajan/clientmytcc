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

### Rust Client Library (`rust/`)

An async Rust client library built on tokio for high-performance applications.

**Features:**
- Async/await API using tokio
- Type-safe models with serde
- Comprehensive error handling with thiserror
- Zero unsafe code
- All API endpoints implemented

**Quick Start:**
```rust
use mytotalconnectcomfort::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::new();
    client.login("your-email@example.com", "your-password").await?;

    let locations = client.get_locations().await?;
    let system = client.get_location_system(&locations[0].id).await?;
    
    client.set_zone_temperature(&system.zones[0].id, 21.0, true, 0, 0).await?;
    Ok(())
}
```

**Documentation:**
- [Rust Client README](rust/README.md) - Installation and usage
- [API Documentation](https://docs.rs/mytotalconnectcomfort) - Full API docs
- [Examples](rust/examples/) - Working code examples

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
├── rust/                         # Rust client library
│   ├── src/
│   │   ├── lib.rs                # Library entry point
│   │   ├── client.rs             # Async API client
│   │   ├── models.rs             # Data models
│   │   ├── error.rs              # Error types
│   │   └── types.rs              # Common types
│   ├── tests/                    # Integration tests
│   ├── examples/                 # Usage examples
│   ├── docs/                     # Library documentation
│   ├── Cargo.toml                # Package manifest
│   └── README.md                 # Library documentation
└── README.md                     # This file
```

## Environment Variables

Both libraries can use the same environment variables for testing with real credentials:

- `EVOHOME_EMAIL` - Your MyTotalConnectComfort email address
- `EVOHOME_PASSWORD` - Your MyTotalConnectComfort password

**Rust** (currently implemented):
```bash
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
cd rust
cargo test --ignored  # Runs integration tests marked with #[ignore]
```

**Python** (can be added to test suite):
```bash
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
cd python
pytest  # Run tests
```

> **Security Note**: Never commit credentials to version control. Use environment variables or secure credential storage.

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

## Library Comparison

| Feature | Python | Rust |
|---------|--------|------|
| **Async** | Sync (blocking) | Async (non-blocking) |
| **Type Safety** | Runtime (type hints) | Compile-time |
| **Performance** | Good | Excellent |
| **Memory Usage** | Higher | Lower |
| **Dependencies** | `requests` only | `reqwest`, `serde`, `tokio` |
| **Error Handling** | Exceptions | `Result` types |
| **Concurrency** | Threading | Async tasks |
| **Test Coverage** | Comprehensive (25+ tests) | Comprehensive (17+ tests) |
| **Best For** | Scripts, automation | High-performance apps |
| **Installation** | `pip install` | `cargo add` |
| **Package Registry** | PyPI | crates.io |

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
