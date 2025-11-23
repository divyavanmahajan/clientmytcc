//! Integration tests for CLI commands that interact with the real API.
//!
//! These tests require valid credentials set in environment variables:
//! - EVOHOME_USER or EVOHOME_EMAIL
//! - EVOHOME_PASSWORD
//!
//! Run with: cargo test --test cli_integration_test -- --ignored

use clientmytcc::Client;
use std::collections::HashMap;

/// Helper to get authenticated client from environment variables
async fn get_test_client() -> Result<Client, Box<dyn std::error::Error>> {
    let email = std::env::var("EVOHOME_USER")
        .or_else(|_| std::env::var("EVOHOME_EMAIL"))
        .expect("EVOHOME_USER or EVOHOME_EMAIL must be set");
    let password = std::env::var("EVOHOME_PASSWORD")
        .expect("EVOHOME_PASSWORD must be set");

    let mut client = Client::new();
    client.login(&email, &password).await?;
    Ok(client)
}

/// Helper to save current zone temperatures
async fn save_zone_temperatures(
    client: &Client,
    location_id: &str,
) -> Result<HashMap<String, f64>, Box<dyn std::error::Error>> {
    let system = client.get_location_system(location_id).await?;
    let mut temps = HashMap::new();
    for zone in &system.zones {
        temps.insert(zone.id.clone(), zone.target_heat_temperature);
    }
    Ok(temps)
}

/// Helper to restore zone temperatures
async fn restore_zone_temperatures(
    client: &Client,
    temps: &HashMap<String, f64>,
) -> Result<(), Box<dyn std::error::Error>> {
    for (zone_id, temp) in temps {
        client
            .set_zone_temperature(zone_id, *temp, true, 0, 0)
            .await?;
    }
    Ok(())
}
