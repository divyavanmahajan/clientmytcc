# MyTotalConnectComfort Rust Client

An async Rust client library for the **International Honeywell Evohome** heating system, provided by **Resideo** (who licensed the Honeywell brand).

> **Note**: This library is designed for the international Evohome system accessible via `international.clientmytcc.com`. North American systems may require different endpoints.

[![Crates.io](https://img.shields.io/crates/v/mytcc_rs.svg)](https://crates.io/crates/mytcc_rs)
[![Documentation](https://docs.rs/mytcc_rs/badge.svg)](https://docs.rs/mytcc_rs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Async/Await** - Built on tokio for high-performance async I/O
- **Type-Safe** - Strongly typed models with serde
- **Error Handling** - Comprehensive error types with thiserror
- **Session Management** - Automatic cookie-based authentication
- **All Endpoints** - Complete API coverage
- **Zero Unsafe** - 100% safe Rust code

## Installation

Add this to your `Cargo.toml`:

```toml
[dependencies]
mytcc_rs = "0.1"
tokio = { version = "1", features = ["full"] }
```

## CLI Usage
The project includes a binary `mytcc_rs` for controlling your heating system from the command line. Please refer to the [CLI Documentation](https://github.com/divyavanmahajan/clientmytcc/blob/main/rust/docs/CLI_GUIDE.md).

### Basic Commands
```bash
# Login (saves session to ~/.config/clientmytcc/session.json)
mytcc_rs login --email user@example.com

# List locations
mytcc_rs locations

# Monitor all zones
mytcc_rs monitor

# Logout (clears session)
mytcc_rs logout
```

### Authentication
You can authenticate interactively, use secure storage, or set environment variables:

1. **Secure Storage (Recommended)**
   ```bash
   mytcc_rs config set-credentials --email user@example.com
   ```

2. **Environment Variables**
   - **`EVOHOME_USER`** (or `EVOHOME_EMAIL`): Your email address
   - **`EVOHOME_PASSWORD`**: Your password

```bash
export EVOHOME_USER="user@example.com"
export EVOHOME_PASSWORD="secure_password"
mytcc_rs locations  # Works without explicit login
```


### Temperature Control
```bash
# Set temperature for a specific zone
mytcc_rs set --zone-id "Living Room" --temperature 21.0

# Boost all zones
mytcc_rs boost --temp 22.0 --duration 2

# Enable Eco mode
mytcc_rs eco

# Enable Vacation mode
mytcc_rs vacation --temp 12.0

# Reset all zones to follow schedule
mytcc_rs schedule
```

Please refer to the [CLI Documentation](https://github.com/divyavanmahajan/clientmytcc/blob/main/rust/docs/CLI_GUIDE.md).

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Comprehensive usage guide
- [Architecture](docs/ARCHITECTURE.md) - Design and implementation details
- [Development](docs/DEVELOPMENT.md) - Contributing and development guide
- [API Documentation](https://docs.rs/clientmytcc) - Full API docs

## Developing with this library

```rust
use mytcc_rs::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create and authenticate
    let mut client = Client::new();
    client.login("your-email@example.com", "your-password").await?;

    // Get locations
    let locations = client.get_locations().await?;
    println!("Found {} locations", locations.len());

    // Get system status
    let system = client.get_location_system(&locations[0].id).await?;
    for zone in &system.zones {
        println!("{}: {}°C → {}°C", 
            zone.name, zone.temperature, zone.target_heat_temperature);
    }

    // Set temperature
    client.set_zone_temperature(
        &system.zones[0].id,
        21.0,    // temperature
        true,    // permanent
        0,       // hours
        0,       // minutes
        false,   // is_following_schedule
    ).await?;

    Ok(())
}
```

## Usage Examples

### Authentication

```rust
use mytcc_rs::{Client, Error};

let mut client = Client::new();

match client.login("user@example.com", "password").await {
    Ok(response) => println!("Logged in as: {}", response.display_name),
    Err(Error::Authentication(msg)) => eprintln!("Login failed: {}", msg),
    Err(e) => eprintln!("Error: {}", e),
}
```

### List Locations and Zones

```rust
let locations = client.get_locations().await?;

for location in locations {
    println!("Location: {}", location.name);
    
    let system = client.get_location_system(&location.id).await?;
    for zone in system.zones {
        let status = if zone.is_alive { "Online" } else { "Offline" };
        println!("  {}: {}°C ({})", zone.name, zone.temperature, status);
    }
}
```

### Set Temperature (Permanent)

```rust
client.set_zone_temperature(
    "5211675",  // zone_id
    21.5,       // temperature in Celsius
    true,       // permanent
    0,          // hours (ignored when permanent)
    0,          // minutes (ignored when permanent)
    false,      // is_following_schedule
).await?;
```

### Set Temperature (Temporary)

```rust
// Set temperature for 2 hours
client.set_zone_temperature(
    "5211675",
    22.0,
    false,  // not permanent
    2,      // 2 hours
    0,      // 0 minutes
    false,  // is_following_schedule
).await?;
```

### Find Zone by Name

```rust
let zone = client.get_zone_by_name("1232176", "Livingroom").await?;
println!("Current: {}°C, Target: {}°C", 
    zone.temperature, zone.target_heat_temperature);
```

### Concurrent Operations

```rust
use tokio::try_join;

let (system, account) = try_join!(
    client.get_location_system(&location_id),
    client.get_account_info()
)?;

println!("Account: {} {}", account.first_name, account.last_name);
println!("Zones: {}", system.zones.len());
```

## API Reference

### Client

- `new()` - Create a new client
- `login(email, password)` - Authenticate
- `get_locations()` - Get all locations
- `get_location(id)` - Get location details
- `get_location_system(id)` - Get zones and system status
- `get_account_info()` - Get user account info
- `set_zone_temperature(...)` - Set zone temperature
- `get_zone(location_id, zone_id)` - Get specific zone
- `get_zone_by_name(location_id, name)` - Find zone by name

### Data Models

- `Zone` - Heating zone with temperature and status
- `Location` - Home location with zones
- `UserInfo` - User account information
- `Gateway` - Gateway device information

### Error Types

- `Error::Authentication` - Login or session errors
- `Error::Api` - API returned an error
- `Error::ZoneNotFound` - Zone not found
- `Error::LocationNotFound` - Location not found
- `Error::Http` - HTTP request failed
- `Error::Json` - JSON parsing failed

## Examples

See the `examples/` directory for complete working examples:

- `basic_usage.rs` - Basic authentication and operations
- `async_example.rs` - Concurrent operations with tokio

Run examples with:

```bash
cargo run --example basic_usage
```

## Development

### Setup

```bash
git clone https://github.com/divyavanmahajan/clientmytcc.git
cd clientmytcc/rust
cargo build
```

### Testing

```bash
cargo test
cargo test --ignored  # Run integration tests (requires credentials)
```

### Code Quality

```bash
cargo clippy
cargo fmt
cargo doc --open
```

## Publishing

### Build and Test

```bash
cargo build --release
cargo test
cargo doc
```

### Publish to crates.io

```bash
# Dry run
cargo publish --dry-run

# Publish
cargo login
cargo publish
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial library and is not affiliated with, endorsed by, or connected to Honeywell International, Resideo Technologies, or any of their subsidiaries.

**About the Evohome System**: The Evohome heating control system is provided by Resideo Technologies, Inc., who licensed the Honeywell brand from Honeywell International Inc. This library interfaces with the international version of the MyTotalConnectComfort service.

Use this library at your own risk.

## Support

For a full list of commands, API details, and Rust library usage, please refer to the main [Rust README.md](https://github.com/divyavanmahajan/clientmytcc/blob/main/rust/README.md) or the [API Documentation](https://docs.rs/mytcc_rs).

- [Issue Tracker](https://github.com/divyavanmahajan/clientmytcc/issues)

## Acknowledgments

- Built with Rust, tokio, reqwest, and serde
- Inspired by the need for home automation and energy efficiency
