# AGENT.md - evohome_rs (Rust Package)

## Package Overview

**evohome_rs** is an async Rust client library for the International Honeywell Evohome heating system API. It provides both a library crate and a standalone CLI binary, with Python bindings via Maturin.

### Key Information

- **Package Name**: `evohome_rs`
- **Crates.io**: https://crates.io/crates/evohome_rs
- **PyPI**: https://pypi.org/p/evohome_rs (Python bindings)
- **Current Version**: 0.2.2
- **Rust Edition**: 2021
- **MSRV**: 1.70
- **CLI Binary**: `evohome_rs`

## Project Structure

```
rust/
├── src/
│   ├── lib.rs               # Library entry point, re-exports
│   ├── client.rs            # Async API client implementation
│   ├── models.rs            # Data models (Zone, Location, etc.)
│   ├── error.rs             # Error types with thiserror
│   ├── types.rs             # Common types and constants
│   └── bin/
│       └── evohome_rs.rs    # CLI binary implementation
├── tests/                   # Integration tests
│   ├── integration_test.rs
│   └── common/              # Test utilities
├── examples/                # Usage examples
│   ├── basic_usage.rs
│   └── async_example.rs
├── docs/                    # Documentation
├── Cargo.toml               # Rust package manifest
├── pyproject.toml           # Python bindings (Maturin)
└── README.md                # Package documentation
```

## Development Setup

### Initial Setup

```bash
cd rust
cargo build
cargo test
```

### Running the CLI

```bash
# Development
cargo run --bin evohome_rs -- --help

# Release build
cargo build --release
./target/release/evohome_rs --help
```

### Running Tests

```bash
# Unit tests
cargo test

# Integration tests (requires credentials)
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
cargo test --ignored

# With output
cargo test -- --nocapture
```

### Code Quality

```bash
# Linting
cargo clippy

# Formatting
cargo fmt

# Documentation
cargo doc --open
```

## Key Components

### 1. Client (`client.rs`)

Async API client built on `reqwest` and `tokio`.

**Key Methods**:
- `new()`: Create new client
- `login(email, password)`: Authenticate (async)
- `get_locations()`: Retrieve all locations (async)
- `get_location_system(location_id)`: Get zones and system status (async)
- `set_zone_temperature(...)`: Control zone temperature (async)
- `get_account_info()`: Get user account details (async)

**Session Management**:
- Uses `reqwest::Client` with cookie store
- Automatically handles CSRF tokens
- Thread-safe with `Arc<Mutex<...>>` for shared state

### 2. Models (`models.rs`)

Serde-compatible data structures.

**Main Models**:
- `Zone`: Heating zone with temperature, status, alerts
- `Location`: Home location with zones and gateways
- `UserInfo`: User account information
- `Gateway`: Gateway device information
- `LoginResponse`: Authentication response

**Design Pattern**: Structs with `#[derive(Serialize, Deserialize)]` for JSON handling.

### 3. Error Handling (`error.rs`)

Custom error types using `thiserror`.

```rust
#[derive(Error, Debug)]
pub enum Error {
    #[error("Authentication failed: {0}")]
    Authentication(String),
    
    #[error("API error: {0}")]
    Api(String),
    
    #[error("Zone not found: {0}")]
    ZoneNotFound(String),
    
    #[error("Location not found: {0}")]
    LocationNotFound(String),
    
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
}
```

### 4. CLI Binary (`bin/evohome_rs.rs`)

Command-line interface built with `clap`.

**Command Structure**:
```
evohome_rs
├── login         # Authenticate and save session
├── logout        # Clear session
├── locations     # List all locations
├── account       # Show account info
├── monitor       # Monitor zone temperatures (alias: zones)
├── set           # Set zone temperature
├── boost         # Boost all zones
├── eco           # Enable eco mode
├── vacation      # Enable vacation mode
├── schedule      # Reset to schedule
└── config        # Manage configuration
```

**Session Storage**: 
- `~/.config/evohome_rs/session.json` (session cookies)
- Credentials stored in OS keyring via `keyring` crate

## Common Development Tasks

### Adding a New API Endpoint

1. **Add method to `Client` struct** (`client.rs`):
```rust
pub async fn new_endpoint(&self, param: &str) -> Result<NewModel, Error> {
    let url = format!("{}/api/new/{}", self.base_url, param);
    let response = self.client.get(&url)
        .send()
        .await?
        .json::<NewModel>()
        .await?;
    Ok(response)
}
```

2. **Add model if needed** (`models.rs`):
```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct NewModel {
    pub field1: String,
    pub field2: i32,
}
```

3. **Add tests** (`tests/integration_test.rs`):
```rust
#[tokio::test]
async fn test_new_endpoint() {
    let client = Client::new();
    let result = client.new_endpoint("test").await;
    assert!(result.is_ok());
}
```

4. **Add CLI command** (if applicable) (`bin/evohome_rs.rs`):
```rust
#[derive(Subcommand)]
enum Commands {
    // ... existing commands
    NewCommand {
        #[arg(long)]
        param: String,
    },
}

// In main match:
Commands::NewCommand { param } => {
    let result = client.new_endpoint(&param).await?;
    println!("{:?}", result);
}
```

### Updating Version

**Files to update**:
1. `Cargo.toml` → `version = "X.Y.Z"`
2. `pyproject.toml` → `version = "X.Y.Z"`

**Also update Python package** (see `../python/AGENT.md`)

### Testing with Real API

```bash
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
cargo test --ignored -- --nocapture
```

## CLI Development

### Adding a New Command

1. **Define command in `Commands` enum**:
```rust
#[derive(Subcommand)]
enum Commands {
    NewCommand {
        /// Description of option
        #[arg(long, short)]
        option1: String,
    },
}
```

2. **Implement handler in `main()`**:
```rust
match cli.command {
    Commands::NewCommand { option1 } => {
        // Implementation
    }
}
```

3. **Test manually**:
```bash
cargo run --bin evohome_rs -- new-command --option1 value
```

### CLI Best Practices

- Use `tabled` for formatted table output
- Use `colored` for colored terminal output
- Handle errors with `?` operator and return `Result<(), Box<dyn Error>>`
- Provide helpful error messages
- Support `--help` for all commands
- Use `rpassword` for secure password input

## Testing Strategy

### Unit Tests

Test individual functions:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_model_creation() {
        let zone = Zone {
            id: "123".to_string(),
            name: "Living Room".to_string(),
            // ...
        };
        assert_eq!(zone.id, "123");
    }
}
```

### Integration Tests

Use real API (marked with `#[ignore]`):

```rust
#[tokio::test]
#[ignore]
async fn test_real_login() {
    let email = std::env::var("EVOHOME_EMAIL").unwrap();
    let password = std::env::var("EVOHOME_PASSWORD").unwrap();
    
    let mut client = Client::new();
    let result = client.login(&email, &password).await;
    assert!(result.is_ok());
}
```

### Doc Tests

Examples in documentation are tested:

```rust
/// # Example
/// ```
/// use evohome_rs::Client;
/// 
/// #[tokio::main]
/// async fn main() {
///     let client = Client::new();
///     // ...
/// }
/// ```
```

## Publishing

### Build Package

```bash
# Clean
cargo clean

# Build release
cargo build --release

# Run tests
cargo test
```

### Publish to crates.io

**Manual**:
```bash
# Dry run
cargo publish --dry-run

# Publish
cargo login
cargo publish
```

**Automated** (via GitHub Actions):
- Push tag `vX.Y.Z` triggers `.github/workflows/pypi.yml`
- Workflow builds wheels for multiple platforms
- Publishes to PyPI (not crates.io)

### Python Bindings (Maturin)

The Rust binary is packaged for Python using Maturin:

```bash
# Build Python wheel
maturin build --release

# Develop locally
maturin develop
```

**Configuration**: `pyproject.toml`
```toml
[tool.maturin]
bindings = "bin"  # Package as standalone binary
```

## Configuration Files

### `Cargo.toml`

**Key sections**:
- `[package]`: Package metadata, version, edition
- `[dependencies]`: Runtime dependencies
- `[dev-dependencies]`: Test dependencies
- `[[bin]]`: Binary target configuration
- `[lib]`: Library configuration

**Important Dependencies**:
- `reqwest`: HTTP client (with `json`, `cookies`, `rustls-tls`)
- `tokio`: Async runtime (with `full` features)
- `serde`: Serialization framework
- `serde_json`: JSON support
- `thiserror`: Error handling
- `clap`: CLI framework
- `keyring`: Secure credential storage
- `tabled`: Table formatting
- `colored`: Terminal colors

### `pyproject.toml`

Maturin configuration for Python packaging:
- `[build-system]`: Maturin as build backend
- `[project]`: Python package metadata
- `[tool.maturin]`: Bindings type (`bin`)

## Common Issues

### Async Runtime Errors

**Problem**: `thread 'main' panicked at 'there is no reactor running'`

**Solution**: Ensure `#[tokio::main]` or `tokio::runtime::Runtime` is used:
```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // async code
}
```

### Borrow Checker Issues

**Problem**: Cannot borrow `client` as mutable

**Solution**: Use interior mutability or restructure code:
```rust
// Option 1: Use Arc<Mutex<...>>
let client = Arc::new(Mutex::new(Client::new()));

// Option 2: Restructure to avoid multiple borrows
let result1 = client.method1().await?;
let result2 = client.method2().await?;
```

### Credential Storage

**Problem**: Keyring access fails on some systems

**Solution**: Fall back to environment variables:
```rust
let password = keyring::Entry::new("evohome_rs", &email)
    .and_then(|e| e.get_password())
    .or_else(|_| std::env::var("EVOHOME_PASSWORD"))?;
```

## Code Style Guidelines

### Formatting
- Use `cargo fmt` with default settings
- Follow Rust API Guidelines

### Error Handling
- Use `Result<T, Error>` for fallible operations
- Use `?` operator for error propagation
- Provide context with custom error variants

### Documentation
- Use `///` for public items
- Include examples in doc comments
- Run `cargo doc --open` to verify

### Async Best Practices
- Use `.await` for async operations
- Avoid blocking operations in async context
- Use `tokio::spawn` for concurrent tasks

## Dependencies

### Runtime Dependencies
- `reqwest = { version = "0.11", features = ["json", "cookies", "rustls-tls"] }`
- `tokio = { version = "1.0", features = ["full"] }`
- `serde = { version = "1.0", features = ["derive"] }`
- `serde_json = "1.0"`
- `thiserror = "1.0"`
- `async-trait = "0.1"`
- `clap = { version = "4.4", features = ["derive"] }`
- `tabled = "0.15"`
- `colored = "2.1"`
- `rpassword = "7.3"`
- `dirs = "5.0"`
- `keyring = "2.3.3"`
- `toml = "0.9.6"`

### Dev Dependencies
- `tokio-test = "0.4"`
- `mockito = "1.2"`
- `anyhow = "1.0"`

## Related Files

- **Root AGENT.md**: `../AGENT.md` (repository-level context)
- **Python AGENT.md**: `../python/AGENT.md` (Python package context)
- **API Docs**: `../api/API_DOCUMENTATION.md`
- **CLI Guide**: `docs/CLI_GUIDE.md` (if exists)

## Maintenance Checklist

When making changes:
- [ ] Update version in `Cargo.toml` and `pyproject.toml`
- [ ] Update Python version to match (see `../python/AGENT.md`)
- [ ] Add/update tests
- [ ] Run `cargo fmt`, `cargo clippy`
- [ ] Update documentation
- [ ] Update CHANGELOG (if exists)
- [ ] Test CLI commands manually
- [ ] Create PR with conventional commit message

## Performance Considerations

### Async Operations
- Use `tokio::try_join!` for concurrent operations
- Avoid unnecessary `.await` points
- Use connection pooling (built into `reqwest`)

### Memory Usage
- Use `&str` instead of `String` where possible
- Avoid cloning large structures
- Use `Arc` for shared ownership

### Build Optimization
- Release builds use `opt-level = 3` by default
- Consider `lto = true` for smaller binaries
- Use `strip = true` to remove debug symbols

## Platform-Specific Notes

### macOS
- Keyring uses macOS Keychain
- Binary works on both Intel and Apple Silicon (built separately)

### Windows
- Keyring uses Windows Credential Manager
- Binary built for x64 and x86

### Linux
- Keyring uses Secret Service API (requires `libsecret`)
- Binary built for x86_64 with `manylinux` compatibility
