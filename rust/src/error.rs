//! Custom error types for the MyTotalConnectComfort API client.

use thiserror::Error;

/// Result type alias for this crate.
pub type Result<T> = std::result::Result<T, Error>;

/// Error types for the MyTotalConnectComfort API client.
#[derive(Error, Debug)]
pub enum Error {
    /// Authentication failed (invalid credentials or session expired).
    #[error("Authentication failed: {0}")]
    Authentication(String),

    /// API returned an error response.
    #[error("API error: {0}")]
    Api(String),

    /// Zone not found.
    #[error("Zone not found: {0}")]
    ZoneNotFound(String),

    /// Location not found.
    #[error("Location not found: {0}")]
    LocationNotFound(String),

    /// Session has expired.
    #[error("Session expired")]
    SessionExpired,

    /// HTTP request failed.
    #[error("HTTP request failed: {0}")]
    Http(#[from] reqwest::Error),

    /// JSON serialization/deserialization failed.
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),

    /// Invalid response from API.
    #[error("Invalid response: {0}")]
    InvalidResponse(String),
}
