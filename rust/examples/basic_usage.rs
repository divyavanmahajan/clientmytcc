//! Basic usage example for the MyTotalConnectComfort API client.

use mytotalconnectcomfort::{Client, Error};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Create a client instance
    let mut client = Client::new();

    // Login with your credentials
    // IMPORTANT: Replace with your actual credentials
    let email = "your-email@example.com";
    let password = "your-password";

    println!("Logging in...");
    match client.login(email, password).await {
        Ok(user_data) => {
            println!("[OK] Logged in as: {}", user_data.display_name);
        }
        Err(Error::Authentication(msg)) => {
            eprintln!("[ERROR] Authentication failed: {}", msg);
            eprintln!("Please check your email and password.");
            return Ok(());
        }
        Err(e) => return Err(e.into()),
    }

    // Get all locations
    println!("\nFetching locations...");
    let locations = client.get_locations().await?;
    println!("[OK] Found {} location(s)\n", locations.len());

    for location in &locations {
        println!("Location: {}", location.name);
        println!("  ID: {}", location.id);
        if let Some(city) = &location.city {
            if let Some(country) = &location.country {
                println!("  Address: {}, {}", city, country);
            }
        }
        println!("  Zones: {}\n", location.zones.len());

        // Get detailed system information for this location
        println!("Fetching system details for {}...", location.name);
        let system = client.get_location_system(&location.id).await?;

        // Display zone information
        for zone in &system.zones {
            let status = if zone.is_alive {
                "[Online]"
            } else {
                "[Offline]"
            };
            let override_info = if zone.override_active {
                " (Override Active)"
            } else {
                ""
            };

            println!("  Zone: {}{}{}", zone.name, status, override_info);
            println!("    Current: {}°C", zone.temperature);
            println!("    Target:  {}°C", zone.target_heat_temperature);
            println!(
                "    Range:   {}°C - {}°C",
                zone.min_heat_setpoint, zone.max_heat_setpoint
            );

            if zone.has_alerts {
                println!("    [WARNING] Has alerts!");
            }
            println!();
        }

        // Example: Set temperature for a specific zone
        if let Some(example_zone) = system.zones.first() {
            let new_temp = 21.0;

            println!(
                "Example: Setting {} to {}°C...",
                example_zone.name, new_temp
            );
            match client
                .set_zone_temperature(&example_zone.id, new_temp, true, 0, 0)
                .await
            {
                Ok(_) => println!("[OK] Temperature set successfully!"),
                Err(e) => eprintln!("[ERROR] Failed to set temperature: {}", e),
            }
            println!();
        }
    }

    // Get account information
    println!("Fetching account information...");
    let account = client.get_account_info().await?;
    println!(
        "[OK] Account: {} {}",
        account.first_name, account.last_name
    );
    println!("  Email: {}", account.username);
    if let (Some(city), Some(country)) = (&account.city, &account.country_name) {
        println!("  Location: {}, {}", city, country);
    }

    Ok(())
}
