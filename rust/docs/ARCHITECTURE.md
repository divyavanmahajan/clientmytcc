# Architecture Documentation

## Overview

The MyTotalConnectComfort Rust client library provides a high-performance, type-safe async interface to the MyTotalConnectComfort API for the **International Honeywell Evohome** heating system. This system is provided by **Resideo**, who licensed the Honeywell brand from Honeywell International. The library is designed with performance, safety, and developer experience in mind.

> **Important**: This library targets the international version of the Evohome system (`international.mytotalconnectcomfort.com`). North American Honeywell systems may use different APIs.

## Design Principles

1. **Async First** - Non-blocking I/O with tokio for high performance
2. **Type Safety** - Compile-time guarantees with Rust's type system
3. **Zero Unsafe** - 100% safe Rust code
4. **Error Handling** - Explicit error types with `Result<T, Error>`
5. **Minimal Dependencies** - Only essential, well-maintained crates

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application (async)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Client (client.rs)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Async Authentication (login)                        │ │
│  │  • Session Management (cookies, CSRF tokens)           │ │
│  │  • Async API Methods (get_locations, set_temp, etc.)   │ │
│  │  • Error Handling & Type Conversion                    │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────┐   ┌──────────────────────┐
│   Models (models.rs)  │   │ Error (error.rs)     │
│  • Zone               │   │  • Error enum        │
│  • Location           │   │  • Result<T> alias   │
│  • UserInfo           │   │  • thiserror derive  │
│  • Gateway            │   └──────────────────────┘
│  (serde derive)       │               │
└───────────────────────┘               │
                            ┌───────────┴──────────┐
                            ▼                      ▼
                ┌──────────────────┐   ┌─────────────────┐
                │ Types (types.rs) │   │ Async Runtime   │
                │  • Enums         │   │    (tokio)      │
                │  • Constants     │   └─────────────────┘
                └──────────────────┘               │
                            │                      ▼
                            ▼          ┌─────────────────────────┐
┌─────────────────────────────────────────────────────────────┐
│                    reqwest::Client                          │
│         (Async HTTP Client with Cookie Store)               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           MyTotalConnectComfort API (HTTPS)                 │
│        https://international.mytotalconnectcomfort.com      │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### `lib.rs` - Library Entry Point

**Responsibilities:**
- Re-export public API
- Module organization
- Crate-level documentation
- Usage examples in docs

**Design Patterns:**
- **Facade Pattern** - Clean public API
- **Module System** - Organized code structure

### `client.rs` - Async API Client

**Responsibilities:**
- Async HTTP communication via `reqwest`
- Authentication and session lifecycle
- CSRF token management
- Request/response handling
- Error translation

**Key Components:**

```rust
pub struct Client {
    http_client: HttpClient,           // reqwest::Client
    cookie_jar: Arc<Jar>,               // Cookie storage
    authenticated: bool,                // Auth state
}
```

**Design Patterns:**
- **Builder Pattern** - Client configuration
- **Async/Await** - Non-blocking I/O
- **Error Conversion** - From reqwest/serde to domain errors

### `models.rs` - Data Models

**Responsibilities:**
- Type-safe data structures
- JSON serialization/deserialization
- Data validation via types
- Helper methods

**Key Models:**

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Zone {
    // Temperature data
    // Status flags
    // Device information
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Location {
    // Address information
    // Zones collection
    // Gateway devices
}
```

**Design Patterns:**
- **Data Transfer Object (DTO)** - Immutable data
- **Serde Integration** - Automatic JSON handling
- **Composite Pattern** - Location contains Zones

### `error.rs` - Error Handling

**Error Hierarchy:**

```rust
#[derive(Error, Debug)]
pub enum Error {
    #[error("Authentication failed: {0}")]
    Authentication(String),
    
    #[error("API error: {0}")]
    Api(String),
    
    #[error("Zone not found: {0}")]
    ZoneNotFound(String),
    
    #[error("HTTP request failed: {0}")]
    Http(#[from] reqwest::Error),
    
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    
    // ... more variants
}
```

**Design Patterns:**
- **Error Enum** - Type-safe error handling
- **thiserror** - Automatic Display/Error impl
- **From Trait** - Automatic error conversion

### `types.rs` - Common Types

**Responsibilities:**
- Shared type definitions
- Enums for status codes
- Constants

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
#[repr(u8)]
pub enum SetPointStatus {
    FollowingSchedule = 0,
    ManualOverride = 2,
}
```

## Async Architecture

### Tokio Runtime

The library uses tokio as the async runtime:

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::new();
    client.login("email", "password").await?;
    // ... async operations
    Ok(())
}
```

**Benefits:**
- Non-blocking I/O
- Concurrent operations with `try_join!`
- Efficient resource usage
- Scalable to many connections

### Async Request Flow

```
1. User calls async method (e.g., get_locations())
   │
   ▼
2. ensure_authenticated() checks login state
   │
   ▼
3. Build HTTP request with reqwest
   │
   ├─ Add CSRF token for POST
   ├─ Set headers
   └─ Cookies included automatically
   │
   ▼
4. await http_client.request().send()
   │ (yields to tokio runtime)
   │
   ▼
5. Response validation
   │
   ├─ Check HTTP status
   ├─ Parse JSON with serde
   └─ Check API errors
   │
   ▼
6. Return Result<T, Error>
   │
   ▼
7. Convert to model objects
```

## Authentication Flow

```
1. User calls client.login(email, password).await
   │
   ▼
2. GET /Account/Login (get CSRF tokens)
   │
   ▼
3. Extract __RequestVerificationToken from cookies
   │
   ▼
4. POST /api/accountApi/login with credentials
   │
   ▼
5. Receive SessionCookie and RefreshCookie
   │
   ▼
6. Store in Arc<Jar> (shared with reqwest)
   │
   ▼
7. All subsequent requests include cookies
```

## Session Management

**Cookie Lifecycle:**
- `SessionCookie` - Valid for 1 hour
- `RefreshCookie` - Valid for 6 months
- Stored in `Arc<Jar>` for thread-safe sharing
- Automatic inclusion via reqwest cookie store

**CSRF Protection:**
- `__RequestVerificationToken` cookie
- `antiForgeryToken` header for POST
- Extracted from login page
- Included in state-changing operations

## Type Safety

### Compile-Time Guarantees

```rust
// Won't compile - wrong type
client.set_zone_temperature("zone_id", "21.0", true, 0, 0).await?;
                                       ^^^^^^ expected f64

// Won't compile - missing await
let locations = client.get_locations();
               ^^^^^^^^^^^^^^^^^^^^^^^ expected `Result<...>`, found opaque type
```

### Serde Type Safety

```rust
#[derive(Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Zone {
    pub temperature: f64,  // Compile error if API returns string
    pub is_alive: bool,    // Compile error if API returns int
}
```

## Error Handling Strategy

### Three-Layer Error Handling

1. **HTTP Layer** - `reqwest::Error`
   - Connection errors
   - Timeout errors
   - HTTP status codes

2. **Serialization Layer** - `serde_json::Error`
   - JSON parsing errors
   - Type mismatches

3. **Domain Layer** - Custom `Error` enum
   - Authentication failures
   - Zone/Location not found
   - API errors

### Error Conversion

```rust
HTTP 401 → Error::Authentication
HTTP 404 → Error::ZoneNotFound / LocationNotFound
reqwest::Error → Error::Http (automatic via #[from])
serde_json::Error → Error::Json (automatic via #[from])
```

## Concurrency

### Concurrent Operations

```rust
use tokio::try_join;

// Execute multiple async operations concurrently
let (system, account) = try_join!(
    client.get_location_system(&location_id),
    client.get_account_info()
)?;
```

### Thread Safety

- `Client` is `Send + Sync`
- Can be shared across threads
- `Arc<Jar>` for shared cookie storage
- No interior mutability except for cookies

## Performance Considerations

### Connection Pooling

- `reqwest::Client` maintains connection pool
- Reuses TCP connections
- Reduces latency for subsequent requests

### Zero-Copy Deserialization

- Serde deserializes directly to structs
- No intermediate representations
- Minimal allocations

### Async Efficiency

- Non-blocking I/O
- Minimal thread overhead
- Efficient task scheduling via tokio

## Security Considerations

### Credential Handling

- No credential storage in library
- User responsible for secure storage
- Credentials only in memory during login

### Session Security

- HTTPS only (enforced by base URL)
- Secure cookie handling via reqwest
- CSRF protection on all POST requests

### Memory Safety

- No unsafe code
- Rust's ownership prevents data races
- Compile-time memory safety guarantees

## Testing Strategy

### Unit Tests

- Test error type conversions
- Test enum implementations
- Test helper methods

### Integration Tests

- Mock-free authentication tests
- Real API workflow tests (with `#[ignore]`)
- Concurrent operation tests

### Test Coverage

```bash
cargo test                    # Run all tests
cargo test --ignored          # Run integration tests
cargo tarpaulin              # Generate coverage report
```

## Extensibility Points

### Adding New Endpoints

1. Add async method to `Client`
2. Use existing HTTP client
3. Parse response with serde
4. Return `Result<T, Error>`

### Adding New Models

1. Create struct with `#[derive(Deserialize)]`
2. Add `#[serde(rename_all = "PascalCase")]`
3. Use `Option<T>` for nullable fields
4. Add helper methods as needed

### Custom Error Types

1. Add variant to `Error` enum
2. Add `#[error("...")]` attribute
3. Use in appropriate contexts

## Future Enhancements

**Potential Additions:**
- Custom base URL support for testing
- Retry logic with exponential backoff
- Rate limiting protection
- Metrics and tracing support
- WebSocket support for real-time updates
- Caching layer for frequently accessed data
- Configuration file support

## Comparison with Python Client

| Aspect | Python | Rust |
|--------|--------|------|
| **Execution** | Synchronous | Asynchronous |
| **Type Safety** | Runtime | Compile-time |
| **Memory Safety** | GC | Ownership |
| **Performance** | Good | Excellent |
| **Concurrency** | Threading/asyncio | Tokio tasks |
| **Error Handling** | Exceptions | Result types |
| **Dependencies** | requests | reqwest, serde, tokio |

## Dependency Graph

```
mytotalconnectcomfort
├── reqwest (HTTP client)
│   ├── tokio (async runtime)
│   ├── serde (serialization)
│   └── cookie_store (cookies)
├── serde (serialization framework)
│   └── serde_json (JSON support)
├── thiserror (error handling)
└── async-trait (async traits)
```

## Build and Distribution

### Cargo Configuration

```toml
[package]
name = "mytotalconnectcomfort"
version = "0.1.0"
edition = "2021"
rust-version = "1.70"

[dependencies]
reqwest = { version = "0.11", features = ["json", "cookies"] }
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
thiserror = "1.0"
```

### Publishing to crates.io

1. Ensure all tests pass
2. Update version in `Cargo.toml`
3. Run `cargo publish --dry-run`
4. Run `cargo publish`

## Documentation

### Rustdoc

All public items have documentation:

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
pub struct Client { /* ... */ }
```

Generate docs with:
```bash
cargo doc --open
```
