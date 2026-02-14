# User Guide

## Introduction

Welcome to the MyTotalConnectComfort Rust Client Library! This guide will help you get started with controlling your **International Honeywell Evohome** heating system programmatically using async Rust.

> **About the System**: The Evohome system is provided by **Resideo**, who licensed the Honeywell brand from Honeywell International. This library is specifically designed for the international version accessible via `international.mytotalconnectcomfort.com`. If you have a North American Honeywell system, it may use different endpoints.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Working with Locations](#working-with-locations)
5. [Working with Zones](#working-with-zones)
6. [Temperature Control](#temperature-control)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Common Use Cases](#common-use-cases)
10. [Troubleshooting](#troubleshooting)

## Installation

### From crates.io

```toml
[dependencies]
evohome_rs = "0.1"
tokio = { version = "1", features = ["full"] }
```

### From Source

```bash
git clone https://github.com/divyavanmahajan/clientmytcc.git
cd clientmytcc/rust
cargo build --release
```

### Verify Installation

```bash
cargo add evohome_rs
cargo check
```

## Quick Start

Here's a complete example to get you started:

```rust
use evohome_rs::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create and authenticate
    let mut client = Client::new();
    client.login("your-email@example.com", "your-password").await?;

    // Get your locations
    let locations = client.get_locations().await?;
    println!("You have {} location(s)", locations.len());

    // Get zones for first location
    let location = &locations[0];
    let system = client.get_location_system(&location.id).await?;

    // Display current temperatures
    for zone in &system.zones {
        println!("{}: {}°C → {}°C", 
            zone.name, zone.temperature, zone.target_heat_temperature);
    }

    // Set a temperature
    client.set_zone_temperature(
        &system.zones[0].id,
        21.0,
        true,  // permanent
        0,     // hours
        0,     // minutes
    ).await?;

    Ok(())
}
```

## Authentication

### Basic Login

```rust
use evohome_rs::{Client, Error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::new();

    match client.login("user@example.com", "password").await {
        Ok(response) => println!("[OK] Login successful: {}", response.display_name),
        Err(Error::Authentication(msg)) => {
            eprintln!("[ERROR] Login failed: {}", msg);
        }
        Err(e) => eprintln!("[ERROR] {}", e),
    }

    Ok(())
}
```

### Session Persistence

The client maintains your session automatically using cookies. You don't need to login again for subsequent requests:

```rust
let mut client = Client::new();
client.login("user@example.com", "password").await?;

// All these work without re-authenticating
let locations = client.get_locations().await?;
let account = client.get_account_info().await?;
let system = client.get_location_system(&locations[0].id).await?;
```

### Session Expiry

Sessions expire after 1 hour. If you get a `SessionExpired` error, simply login again:

```rust
use evohome_rs::Error;

let locations = match client.get_locations().await {
    Ok(locs) => locs,
    Err(Error::SessionExpired) => {
        client.login("user@example.com", "password").await?;
        client.get_locations().await?
    }
    Err(e) => return Err(e.into()),
};
```

## Working with Locations

### List All Locations

```rust
let locations = client.get_locations().await?;

for location in &locations {
    println!("Location: {}", location.name);
    println!("  ID: {}", location.id);
    if let Some(address) = &location.street_address {
        println!("  Address: {}", address);
    }
    if let (Some(city), Some(country)) = (&location.city, &location.country) {
        println!("  City: {}, {}", city, country);
    }
    println!("  Zones: {}", location.zones.len());
}
```

### Get Location Details

```rust
let location_id = "1232176";
let location = client.get_location(location_id).await?;

if let Some(owner) = &location.owner_name {
    println!("Owner: {}", owner);
}
if let Some(postcode) = &location.postcode {
    println!("Postcode: {}", postcode);
}
if let Some(tz) = &location.time_zone_display_name {
    println!("Time Zone: {}", tz);
}
println!("Notification Emails: {}", location.notification_emails.join(", "));
```

### Get Location System (with Zones)

```rust
let system = client.get_location_system(location_id).await?;

println!("System Device ID: {}", system.id);
println!("Number of Zones: {}", system.zones.len());
```

## Working with Zones

### List All Zones

```rust
let system = client.get_location_system(location_id).await?;

for zone in &system.zones {
    let status = if zone.is_alive { "[Online]" } else { "[Offline]" };
    println!("{} {}", zone.name, status);
    println!("  Current: {}°C", zone.temperature);
    println!("  Target: {}°C", zone.target_heat_temperature);
}
```

### Get Zone by ID

```rust
use evohome_rs::Error;

match client.get_zone("1232176", "5211675").await {
    Ok(zone) => println!("Found zone: {}", zone.name),
    Err(Error::ZoneNotFound(id)) => eprintln!("Zone not found: {}", id),
    Err(e) => eprintln!("Error: {}", e),
}
```

### Get Zone by Name

```rust
let zone = client.get_zone_by_name("1232176", "Livingroom").await?;
println!("Zone ID: {}", zone.id);
println!("Temperature: {}°C", zone.temperature);
```

### Check Zone Status

```rust
let zone = client.get_zone(location_id, zone_id).await?;

// Check if zone is online
if !zone.is_alive {
    println!("[WARNING] {} is offline!", zone.name);
}

// Check for alerts
if zone.has_alerts {
    println!("[WARNING] {} has alerts", zone.name);
    if zone.has_battery_low_alert {
        println!("  - Battery low");
    }
    if zone.has_comm_lost_alert {
        println!("  - Communication lost");
    }
    if zone.has_sensor_failure_alert {
        println!("  - Sensor failure");
    }
}

// Check override status
if zone.override_active {
    if zone.hold_temperature_permanently {
        println!("  Temperature held permanently at {}°C", zone.target_heat_temperature);
    } else {
        println!("  Temporary override active");
    }
}
```

## Temperature Control

### Set Temperature (Permanent)

```rust
// Set temperature permanently (until manually changed)
client.set_zone_temperature(
    "5211675",
    21.5,
    true,  // permanent
    0,     // hours (ignored when permanent)
    0,     // minutes (ignored when permanent)
).await?;
```

### Set Temperature (Temporary)

```rust
// Set temperature for 2 hours, then return to schedule
client.set_zone_temperature(
    "5211675",
    22.0,
    false,  // not permanent
    2,      // 2 hours
    0,      // 0 minutes
).await?;
```

### Set Temperature for 30 Minutes

```rust
client.set_zone_temperature(
    "5211675",
    23.0,
    false,  // not permanent
    0,      // 0 hours
    30,     // 30 minutes
).await?;
```

### Validate Temperature Range

```rust
let zone = client.get_zone(location_id, zone_id).await?;
let desired_temp = 25.0;

if desired_temp < zone.min_heat_setpoint {
    eprintln!("Temperature too low! Minimum is {}°C", zone.min_heat_setpoint);
} else if desired_temp > zone.max_heat_setpoint {
    eprintln!("Temperature too high! Maximum is {}°C", zone.max_heat_setpoint);
} else {
    client.set_zone_temperature(&zone.id, desired_temp, true, 0, 0).await?;
}
```

## Error Handling

### Comprehensive Error Handling

```rust
use evohome_rs::{Client, Error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::new();

    // Login
    if let Err(e) = client.login("user@example.com", "password").await {
        match e {
            Error::Authentication(msg) => {
                eprintln!("Authentication failed: {}", msg);
                eprintln!("Please check your email and password");
                return Ok(());
            }
            _ => return Err(e.into()),
        }
    }

    // Get locations
    let locations = match client.get_locations().await {
        Ok(locs) => locs,
        Err(Error::SessionExpired) => {
            eprintln!("Session expired, please login again");
            return Ok(());
        }
        Err(Error::Api(msg)) => {
            eprintln!("API error: {}", msg);
            return Ok(());
        }
        Err(e) => return Err(e.into()),
    };

    // Set temperature
    if let Err(e) = client.set_zone_temperature("5211675", 21.0, true, 0, 0).await {
        match e {
            Error::ZoneNotFound(id) => {
                eprintln!("Zone not found: {}", id);
                eprintln!("Please check the zone ID");
            }
            Error::Api(msg) => {
                eprintln!("API error: {}", msg);
            }
            _ => eprintln!("Unexpected error: {}", e),
        }
    }

    Ok(())
}
```

## Best Practices

### 1. Reuse Client Instance

```rust
// Good: Reuse client
let mut client = Client::new();
client.login(&email, &password).await?;
let locations = client.get_locations().await?;
let account = client.get_account_info().await?;

// Avoid: Creating multiple clients
let mut client1 = Client::new();
client1.login(&email, &password).await?;
let mut client2 = Client::new();  // Unnecessary
client2.login(&email, &password).await?;
```

### 2. Cache Location and Zone Data

```rust
use std::collections::HashMap;

// Cache location data to avoid repeated API calls
let locations = client.get_locations().await?;
let location_id = &locations[0].id;

// Cache system data
let system = client.get_location_system(location_id).await?;
let zones: HashMap<String, &Zone> = system.zones
    .iter()
    .map(|z| (z.name.clone(), z))
    .collect();

// Use cached data
if let Some(livingroom) = zones.get("Livingroom") {
    println!("Current temp: {}°C", livingroom.temperature);
}
```

### 3. Use Result Type Properly

```rust
async fn safe_set_temperature(
    client: &Client,
    zone: &Zone,
    temperature: f64,
) -> Result<(), Box<dyn std::error::Error>> {
    if !zone.is_alive {
        return Err(format!("Zone {} is offline", zone.name).into());
    }

    if temperature < zone.min_heat_setpoint || temperature > zone.max_heat_setpoint {
        return Err(format!(
            "Temperature {}°C out of range ({}°C - {}°C)",
            temperature, zone.min_heat_setpoint, zone.max_heat_setpoint
        ).into());
    }

    client.set_zone_temperature(&zone.id, temperature, true, 0, 0).await?;
    Ok(())
}
```

## Common Use Cases

### 1. Morning Boost

```rust
async fn morning_boost(
    client: &Client,
    location_id: &str,
    target_temp: f64,
    duration_hours: u32,
) -> Result<(), Box<dyn std::error::Error>> {
    let system = client.get_location_system(location_id).await?;

    for zone in &system.zones {
        if zone.is_alive {
            client.set_zone_temperature(
                &zone.id,
                target_temp,
                false,
                duration_hours,
                0,
            ).await?;
            println!("[OK] Boosted {} to {}°C for {}h", zone.name, target_temp, duration_hours);
        }
    }

    Ok(())
}
```

### 2. Energy Saving Mode

```rust
async fn energy_saving_mode(
    client: &Client,
    location_id: &str,
    eco_temp: f64,
) -> Result<(), Box<dyn std::error::Error>> {
    let system = client.get_location_system(location_id).await?;

    for zone in &system.zones {
        if zone.is_alive && zone.temperature > eco_temp {
            client.set_zone_temperature(&zone.id, eco_temp, true, 0, 0).await?;
            println!("[OK] Set {} to eco mode ({}°C)", zone.name, eco_temp);
        }
    }

    Ok(())
}
```

### 3. Temperature Monitoring

```rust
use serde::Serialize;

#[derive(Serialize)]
struct ZoneReport {
    name: String,
    current: f64,
    target: f64,
    status: String,
    online: bool,
}

async fn monitor_temperatures(
    client: &Client,
    location_id: &str,
) -> Result<Vec<ZoneReport>, Box<dyn std::error::Error>> {
    let system = client.get_location_system(location_id).await?;

    let report: Vec<ZoneReport> = system.zones
        .iter()
        .map(|zone| {
            let diff = zone.target_heat_temperature - zone.temperature;
            let status = if diff > 0.5 { "heating" } else { "stable" };

            ZoneReport {
                name: zone.name.clone(),
                current: zone.temperature,
                target: zone.target_heat_temperature,
                status: status.to_string(),
                online: zone.is_alive,
            }
        })
        .collect();

    Ok(report)
}
```

### 4. Vacation Mode

```rust
async fn vacation_mode(
    client: &Client,
    location_id: &str,
    frost_protect_temp: f64,
) -> Result<(), Box<dyn std::error::Error>> {
    let system = client.get_location_system(location_id).await?;

    for zone in &system.zones {
        if zone.is_alive {
            client.set_zone_temperature(&zone.id, frost_protect_temp, true, 0, 0).await?;
        }
    }

    println!("[OK] Vacation mode activated ({}°C)", frost_protect_temp);
    Ok(())
}
```

## Concurrent Operations

### Fetch Multiple Things Concurrently

```rust
use tokio::try_join;

let locations = client.get_locations().await?;
let location_id = &locations[0].id;

// Fetch system and account info concurrently
let (system, account) = try_join!(
    client.get_location_system(location_id),
    client.get_account_info()
)?;

println!("Account: {} {}", account.first_name, account.last_name);
println!("Zones: {}", system.zones.len());
```

### Update Multiple Zones Concurrently

```rust
use tokio::try_join;

let zone1_id = &system.zones[0].id;
let zone2_id = &system.zones[1].id;

// Set temperatures concurrently
try_join!(
    client.set_zone_temperature(zone1_id, 21.0, true, 0, 0),
    client.set_zone_temperature(zone2_id, 20.0, true, 0, 0)
)?;

println!("[OK] Updated 2 zones concurrently");
```

## Troubleshooting

### Problem: Login Fails

**Solution:**
- Verify email and password are correct
- Check if you can login via the web interface
- Ensure you're using the correct regional server (international)

### Problem: Session Expired

**Solution:**
```rust
async fn api_call_with_retry<F, T>(
    client: &mut Client,
    email: &str,
    password: &str,
    func: F,
) -> Result<T, Box<dyn std::error::Error>>
where
    F: Fn(&Client) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, Error>> + '_>>,
{
    match func(client).await {
        Ok(result) => Ok(result),
        Err(Error::SessionExpired) => {
            client.login(email, password).await?;
            Ok(func(client).await?)
        }
        Err(e) => Err(e.into()),
    }
}
```

### Problem: Zone Not Found

**Solution:**
```rust
// List all zones to find correct ID
let system = client.get_location_system(location_id).await?;
for zone in &system.zones {
    println!("{}: {}", zone.name, zone.id);
}
```

### Problem: Temperature Not Changing

**Possible causes:**
1. Zone is offline (`zone.is_alive == false`)
2. Temperature out of range
3. System in away mode
4. Hardware issue

**Debug:**
```rust
let zone = client.get_zone(location_id, zone_id).await?;
println!("Online: {}", zone.is_alive);
println!("Range: {}°C - {}°C", zone.min_heat_setpoint, zone.max_heat_setpoint);
println!("Override active: {}", zone.override_active);
```

## Getting Help

- [API Documentation](../../api/API_DOCUMENTATION.md)
- [Architecture](ARCHITECTURE.md)
- [Rust API Docs](https://docs.rs/evohome_rs)
- [Issue Tracker](https://github.com/divyavanmahajan/clientmytcc/issues)
