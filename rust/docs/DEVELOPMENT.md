# Development Guidelines

> **About**: This library provides access to the **International Honeywell Evohome** system, which is provided by **Resideo** (who licensed the Honeywell brand). It targets the international API at `international.mytotalconnectcomfort.com`.

## Getting Started

### Prerequisites

- Rust 1.70 or higher
- Cargo (comes with Rust)
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/divyavanmahajan/mytotalconnectcomfort.git
cd mytotalconnectcomfort/rust

# Build the project
cargo build

# Run tests
cargo test
```

## Code Style

### Rust Style Guide

We follow the [Rust Style Guide](https://doc.rust-lang.org/nightly/style-guide/) and use `rustfmt` for automatic formatting.

### Code Formatting

Use **rustfmt** for automatic code formatting:

```bash
# Format all code
cargo fmt

# Check formatting without changes
cargo fmt -- --check
```

### Linting with Clippy

Use **clippy** for linting and catching common mistakes:

```bash
# Run clippy
cargo clippy

# Run clippy with warnings as errors
cargo clippy -- -D warnings

# Run clippy with all lints
cargo clippy --all-targets --all-features -- -D warnings
```

### Documentation Comments

Use rustdoc-style comments for all public items:

```rust
/// Client for the MyTotalConnectComfort API.
///
/// # Example
///
/// ```no_run
/// use mytotalconnectcomfort::Client;
///
/// #[tokio::main]
/// async fn main() -> Result<(), Box<dyn std::error::Error>> {
///     let mut client = Client::new();
///     client.login("user@example.com", "password").await?;
///     Ok(())
/// }
/// ```
pub struct Client {
    // ...
}

/// Set the target temperature for a heating zone.
///
/// # Arguments
///
/// * `zone_id` - The zone ID
/// * `temperature` - Target temperature in Celsius
/// * `permanent` - Whether to hold temperature permanently
/// * `duration_hours` - Hours to hold (if not permanent)
/// * `duration_minutes` - Minutes to hold (if not permanent)
///
/// # Errors
///
/// Returns `Error::Authentication` if not authenticated.
/// Returns `Error::Api` if the API returns an error.
///
/// # Example
///
/// ```no_run
/// # use mytotalconnectcomfort::Client;
/// # #[tokio::main]
/// # async fn main() -> Result<(), Box<dyn std::error::Error>> {
/// # let client = Client::new();
/// client.set_zone_temperature("5211675", 21.0, true, 0, 0).await?;
/// # Ok(())
/// # }
/// ```
pub async fn set_zone_temperature(
    &self,
    zone_id: &str,
    temperature: f64,
    permanent: bool,
    duration_hours: u32,
    duration_minutes: u32,
) -> Result<()> {
    // ...
}
```

## Code Quality Tools

### Running All Checks

```bash
# Format, lint, test, and check docs
cargo fmt && \
cargo clippy -- -D warnings && \
cargo test && \
cargo doc --no-deps
```

### Pre-commit Checks

Create a script to run before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

set -e

echo "Running pre-commit checks..."

echo "1. Formatting..."
cargo fmt -- --check

echo "2. Linting..."
cargo clippy -- -D warnings

echo "3. Testing..."
cargo test

echo "4. Building docs..."
cargo doc --no-deps

echo "All checks passed!"
```

## Testing

### Running Tests

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_client_creation

# Run tests in a specific file
cargo test --test integration_test

# Run ignored tests (integration tests requiring credentials)
cargo test -- --ignored

# Run all tests including ignored
cargo test -- --include-ignored
```

### Test Structure

```
rust/
├── src/
│   └── *.rs                    # Unit tests in modules
└── tests/
    └── integration_test.rs     # Integration tests
```

### Writing Tests

#### Unit Tests

Place unit tests in the same file as the code:

```rust
// In src/types.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_setpoint_status_conversion() {
        assert_eq!(SetPointStatus::from(0), SetPointStatus::FollowingSchedule);
        assert_eq!(SetPointStatus::from(2), SetPointStatus::ManualOverride);
    }
}
```

#### Integration Tests

Place integration tests in `tests/` directory:

```rust
// In tests/integration_test.rs
use mytotalconnectcomfort::{Client, Error};

#[tokio::test]
async fn test_unauthenticated_request() {
    let client = Client::new();
    let result = client.get_locations().await;
    assert!(matches!(result, Err(Error::Authentication(_))));
}

#[tokio::test]
#[ignore]  // Requires real credentials
async fn test_full_workflow() {
    let mut client = Client::new();
    let email = std::env::var("EVOHOME_EMAIL").expect("EVOHOME_EMAIL not set");
    let password = std::env::var("EVOHOME_PASSWORD").expect("EVOHOME_PASSWORD not set");
    
    client.login(&email, &password).await.unwrap();
    let locations = client.get_locations().await.unwrap();
    assert!(!locations.is_empty());
}
```

### Test Coverage

Generate coverage reports with `cargo-tarpaulin`:

```bash
# Install tarpaulin
cargo install cargo-tarpaulin

# Generate coverage
cargo tarpaulin --out Html

# Open report
open tarpaulin-report.html
```

## Git Workflow

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactor: `refactor/description`

```bash
# Good
git checkout -b feature/add-retry-logic
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
git commit -m "feat(client): add retry logic for failed requests"
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
   cargo fmt
   cargo clippy -- -D warnings
   cargo test
   cargo doc
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/my-feature
   ```

5. **PR checklist:**
   - [ ] Tests pass
   - [ ] Code formatted with rustfmt
   - [ ] No clippy warnings
   - [ ] Documentation updated
   - [ ] CHANGELOG updated (if applicable)

## Project Structure

```
rust/
├── src/
│   ├── lib.rs              # Library entry point
│   ├── client.rs           # API client
│   ├── models.rs           # Data models
│   ├── error.rs            # Error types
│   └── types.rs            # Common types
├── tests/
│   └── integration_test.rs # Integration tests
├── examples/
│   ├── basic_usage.rs      # Basic example
│   └── async_example.rs    # Async example
├── docs/
│   ├── ARCHITECTURE.md     # Architecture docs
│   ├── USER_GUIDE.md       # User guide
│   ├── DEVELOPMENT.md      # This file
│   └── WALKTHROUGH.md      # Implementation walkthrough
├── Cargo.toml              # Package manifest
├── Cargo.lock              # Dependency lock file
├── LICENSE                 # MIT License
└── README.md               # Main documentation
```

## Adding New Features

### 1. Add New API Endpoint

```rust
// In src/client.rs
impl Client {
    /// Description of what this endpoint does.
    ///
    /// # Arguments
    ///
    /// * `param` - Parameter description
    ///
    /// # Errors
    ///
    /// Returns `Error::Api` if the API returns an error.
    pub async fn new_endpoint(&self, param: &str) -> Result<ReturnType> {
        self.ensure_authenticated()?;
        
        let url = format!("{}/api/path", BASE_URL);
        let response = self.http_client
            .get(&url)
            .query(&[("param", param)])
            .send()
            .await?;
        
        let api_response: ApiResponse<ReturnType> = response.json().await?;
        self.check_errors(&api_response.errors)?;
        
        api_response.content
            .ok_or_else(|| Error::InvalidResponse("Missing content".to_string()))
    }
}
```

### 2. Add New Model

```rust
// In src/models.rs
/// Description of the model.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct NewModel {
    /// Field description
    pub id: String,
    
    /// Field description
    pub name: String,
    
    /// Optional field description
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<f64>,
}

impl NewModel {
    /// Helper method description.
    pub fn some_method(&self) -> bool {
        // Implementation
        true
    }
}
```

### 3. Add Tests

```rust
// In tests/integration_test.rs
#[tokio::test]
async fn test_new_endpoint() {
    let client = Client::new();
    let result = client.new_endpoint("param").await;
    
    // Should fail without authentication
    assert!(matches!(result, Err(Error::Authentication(_))));
}

#[tokio::test]
#[ignore]
async fn test_new_endpoint_integration() {
    let mut client = Client::new();
    let email = std::env::var("EVOHOME_EMAIL").unwrap();
    let password = std::env::var("EVOHOME_PASSWORD").unwrap();
    
    client.login(&email, &password).await.unwrap();
    let result = client.new_endpoint("param").await.unwrap();
    
    assert!(!result.id.is_empty());
}
```

### 4. Update Documentation

- Add to README.md API Reference
- Add example to USER_GUIDE.md
- Update CHANGELOG.md
- Add rustdoc comments

## Versioning

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes (2.0.0)
- **MINOR**: New features, backward compatible (0.2.0)
- **PATCH**: Bug fixes (0.1.1)

### Updating Version

Update in `Cargo.toml`:

```toml
[package]
version = "0.2.0"
```

Cargo automatically updates `Cargo.lock` when you build.

## Release Process

### 1. Prepare Release

```bash
# Update version in Cargo.toml
# Update CHANGELOG.md
# Commit changes
git add .
git commit -m "chore: bump version to 0.2.0"
git tag v0.2.0
```

### 2. Build and Test

```bash
# Clean build
cargo clean
cargo build --release

# Run all tests
cargo test
cargo test -- --ignored

# Check documentation
cargo doc --no-deps
```

### 3. Publish to crates.io

```bash
# Dry run
cargo publish --dry-run

# Login to crates.io (first time only)
cargo login

# Publish
cargo publish

# Push tags
git push origin main --tags
```

## Debugging

### Enable Debug Logging

```rust
// In your code
use tracing::{info, debug, error};
use tracing_subscriber;

#[tokio::main]
async fn main() {
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    debug!("Debug message");
    info!("Info message");
    error!("Error message");
}
```

### Use Rust Debugger

With VS Code and rust-analyzer:

1. Set breakpoints in code
2. Press F5 to start debugging
3. Use debug console to inspect variables

With LLDB:

```bash
# Build with debug symbols
cargo build

# Run with lldb
rust-lldb target/debug/mytotalconnectcomfort

# Set breakpoint
(lldb) b client.rs:100

# Run
(lldb) run
```

### Inspect HTTP Requests

Add logging to see HTTP traffic:

```rust
// Add to Cargo.toml dev-dependencies
[dev-dependencies]
env_logger = "0.10"

// In your test
#[tokio::test]
async fn test_with_logging() {
    env_logger::init();
    // Your test code
}
```

## Common Issues

### Build Errors

```bash
# Clean and rebuild
cargo clean
cargo build

# Update dependencies
cargo update
```

### Test Failures

```bash
# Run with verbose output
cargo test -- --nocapture

# Run specific test
cargo test test_name -- --nocapture
```

### Dependency Conflicts

```bash
# Check dependency tree
cargo tree

# Update specific dependency
cargo update -p reqwest
```

## Performance Profiling

### Using cargo-flamegraph

```bash
# Install flamegraph
cargo install flamegraph

# Generate flamegraph
cargo flamegraph --example basic_usage

# Open flamegraph.svg
```

### Using criterion for benchmarks

```toml
# Add to Cargo.toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false
```

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_function(c: &mut Criterion) {
    c.bench_function("my_function", |b| {
        b.iter(|| {
            // Code to benchmark
        })
    });
}

criterion_group!(benches, benchmark_function);
criterion_main!(benches);
```

## Resources

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [tokio Documentation](https://tokio.rs/)
- [reqwest Documentation](https://docs.rs/reqwest/)
- [serde Documentation](https://serde.rs/)

## Getting Help

- [User Guide](USER_GUIDE.md)
- [Architecture](ARCHITECTURE.md)
- [Rust API Docs](https://docs.rs/mytotalconnectcomfort)
- [Issue Tracker](https://github.com/divyavanmahajan/mytotalconnectcomfort/issues)
- [Rust Users Forum](https://users.rust-lang.org/)
