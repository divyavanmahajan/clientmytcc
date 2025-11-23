# Architecture Documentation

## Overview

The MyTotalConnectComfort Python client library provides a clean, type-safe interface to the MyTotalConnectComfort API for the **International Honeywell Evohome** heating system. This system is provided by **Resideo**, who licensed the Honeywell brand from Honeywell International. The library is designed with simplicity, maintainability, and developer experience in mind.

> **Important**: This library targets the international version of the Evohome system (`international.clientmytcc.com`). North American Honeywell systems may use different APIs.

## Design Principles

1. **Simplicity First** - Easy to use with minimal configuration
2. **Type Safety** - Full type hints for IDE support and error prevention
3. **Error Handling** - Clear, actionable error messages
4. **Session Management** - Automatic cookie and CSRF token handling
5. **Pythonic API** - Follows Python conventions and best practices

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Application                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Client (client.py)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  • Authentication (login)                              │ │
│  │  • Session Management (cookies, CSRF tokens)           │ │
│  │  • API Methods (get_locations, set_temperature, etc.)  │ │
│  │  • Error Handling & Retry Logic                        │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
┌───────────────────────┐   ┌──────────────────────┐
│   Models (models.py)  │   │ Exceptions           │
│  • Zone               │   │  (exceptions.py)     │
│  • Location           │   │  • AuthenticationErr │
│  • UserInfo           │   │  • APIError          │
│  • Gateway            │   │  • ZoneNotFoundErr   │
└───────────────────────┘   └──────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    requests.Session                         │
│              (HTTP Client with Cookie Jar)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           MyTotalConnectComfort API (HTTPS)                 │
│        https://international.clientmytcc.com      │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### `client.py` - Main Client

**Responsibilities:**
- API communication via `requests.Session`
- Authentication and session lifecycle
- CSRF token extraction and injection
- Request/response handling
- Error translation to custom exceptions

**Key Components:**

```python
class Client:
    - session: requests.Session          # HTTP session with cookies
    - _csrf_token: str                   # CSRF protection token
    - _anti_forgery_token: str           # Anti-forgery token for POST
    - _authenticated: bool               # Authentication state
```

**Design Patterns:**
- **Session Pattern** - Maintains stateful HTTP connection
- **Facade Pattern** - Simplifies complex API interactions
- **Error Translation** - Converts HTTP errors to domain exceptions

### `models.py` - Data Models

**Responsibilities:**
- Type-safe data structures
- API response parsing
- Data validation
- Helper methods for data access

**Key Models:**

```python
@dataclass
class Zone:
    """Heating zone with temperature control"""
    - Temperature data (current, target, min, max)
    - Status flags (is_alive, has_alerts, override_active)
    - Device information (id, mac_id, model)
    
@dataclass
class Location:
    """Home location with multiple zones"""
    - Address information
    - List of zones
    - Gateway devices
    - Helper methods (get_zone_by_id, get_zone_by_name)
    
@dataclass
class UserInfo:
    """User account information"""
    - Personal details
    - Address information
```

**Design Patterns:**
- **Data Transfer Object (DTO)** - Immutable data containers
- **Factory Method** - `from_dict()` constructors
- **Composite Pattern** - Location contains Zones

### `exceptions.py` - Error Handling

**Exception Hierarchy:**

```
MyTotalConnectComfortError (base)
├── AuthenticationError
├── APIError
│   ├── status_code: int
│   └── response: dict
├── ZoneNotFoundError
├── LocationNotFoundError
└── SessionExpiredError
```

**Design Patterns:**
- **Exception Hierarchy** - Allows granular error handling
- **Rich Exceptions** - Include context (status code, response)

## Authentication Flow

```
1. User calls client.login(email, password)
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
6. Store cookies in session (automatic via requests.Session)
   │
   ▼
7. All subsequent requests include cookies automatically
```

## API Request Flow

```
1. User calls API method (e.g., get_locations())
   │
   ▼
2. _ensure_authenticated() checks login state
   │
   ▼
3. _make_request() prepares HTTP request
   │
   ├─ Add CSRF token for POST requests
   ├─ Set Content-Type headers
   └─ Include session cookies (automatic)
   │
   ▼
4. requests.Session.request() executes HTTP call
   │
   ▼
5. Response validation
   │
   ├─ Check HTTP status (401 → SessionExpiredError)
   ├─ Parse JSON response
   └─ Check for API errors in response
   │
   ▼
6. Return parsed data or raise exception
   │
   ▼
7. Convert to model objects (Zone, Location, etc.)
```

## Session Management

**Cookie Lifecycle:**
- `SessionCookie` - Valid for 1 hour
- `RefreshCookie` - Valid for 6 months
- Cookies stored in `requests.Session.cookies`
- Automatic inclusion in all requests

**CSRF Protection:**
- `__RequestVerificationToken` cookie
- `antiForgeryToken` header for POST requests
- Extracted from initial login page
- Included in all state-changing operations

## Error Handling Strategy

**Three-Layer Error Handling:**

1. **HTTP Layer** - `requests` exceptions
   - Connection errors
   - Timeout errors
   - HTTP status codes

2. **API Layer** - API response errors
   - Authentication failures (401)
   - Invalid requests (400)
   - Server errors (500)

3. **Domain Layer** - Business logic errors
   - Zone not found
   - Location not found
   - Invalid temperature range

**Error Translation:**
```python
HTTP 401 → AuthenticationError or SessionExpiredError
HTTP 404 → ZoneNotFoundError or LocationNotFoundError
HTTP 4xx/5xx → APIError with status code and response
```

## Type Safety

**Type Hints Throughout:**
- All public methods have type annotations
- Return types specified for IDE autocomplete
- Optional types for nullable fields
- Generic types for collections (List[Zone])

**Benefits:**
- IDE autocomplete and IntelliSense
- Static type checking with mypy
- Self-documenting code
- Catch errors before runtime

## Extensibility Points

**Adding New Endpoints:**
1. Add method to `Client` class
2. Use `_make_request()` helper
3. Parse response to model objects
4. Add appropriate error handling

**Adding New Models:**
1. Create `@dataclass` in `models.py`
2. Add `from_dict()` class method
3. Include type hints for all fields
4. Add helper methods as needed

**Custom Error Handling:**
1. Subclass `MyTotalConnectComfortError`
2. Add to exception hierarchy
3. Raise in appropriate contexts

## Performance Considerations

**Session Reuse:**
- Single `requests.Session` instance
- Connection pooling (automatic)
- Cookie persistence across requests

**Lazy Loading:**
- Models created on-demand
- No unnecessary API calls
- Explicit data fetching

**Minimal Dependencies:**
- Only `requests` library required
- No heavy frameworks
- Fast import and initialization

## Security Considerations

**Credential Handling:**
- No credential storage in library
- User responsible for secure storage
- Credentials only in memory during login

**Session Security:**
- HTTPS only (enforced by base URL)
- Secure cookies (httpOnly, secure flags)
- CSRF protection on all POST requests

**Error Messages:**
- No credential leakage in errors
- Sanitized error messages
- Debug info in exception objects

## Testing Strategy

**Unit Tests:**
- Mock HTTP responses
- Test error handling
- Validate model parsing
- Check type conversions

**Integration Tests:**
- Real API calls (optional)
- End-to-end workflows
- Session management

**Test Coverage:**
- Target: >80% coverage
- Focus on critical paths
- Edge cases and error conditions

## Future Enhancements

**Potential Additions:**
- Async/await support (aiohttp)
- Caching layer for frequently accessed data
- WebSocket support for real-time updates
- Retry logic with exponential backoff
- Rate limiting protection
- Logging and debugging support
- Configuration file support
