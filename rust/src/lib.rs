//! MyTotalConnectComfort API Client
//!
//! An async Rust client library for the **International Honeywell Evohome** heating system,
//! provided by **Resideo** (who licensed the Honeywell brand).
//!
//! # Example
//!
//! ```no_run
//! use clientmytcc::Client;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), Box<dyn std::error::Error>> {
//!     let mut client = Client::new();
//!     
//!     // Authenticate
//!     client.login("user@example.com", "password").await?;
//!     
//!     // Get locations
//!     let locations = client.get_locations().await?;
//!     
//!     // Get system status
//!     let system = client.get_location_system(&locations[0].id).await?;
//!     
//!     // Set temperature
//!     client.set_zone_temperature(
//!         &system.zones[0].id,
//!         21.0,
//!         true,  // permanent
//!         0,     // hours
//!         0,     // minutes
//!     ).await?;
//!     
//!     Ok(())
//! }
//! ```
//!
//! # Features
//!
//! - Async/await API using tokio
//! - Type-safe models with serde
//! - Comprehensive error handling
//! - Session management with cookies
//! - All API endpoints implemented
//!
//! # About
//!
//! This library targets the international version of the Evohome system
//! (`international.mytotalconnectcomfort.com`). North American systems may use different APIs.

pub mod client;
pub mod error;
pub mod models;
pub mod types;

pub use client::Client;
pub use error::{Error, Result};
pub use models::{Gateway, Location, LoginResponse, UserInfo, Zone};
pub use types::{SetPointStatus, TemperatureUnit};
