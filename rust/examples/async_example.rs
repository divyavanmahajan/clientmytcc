//! Async example showing concurrent operations.

use mytotalconnectcomfort::Client;
use tokio::try_join;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut client = Client::new();

    // Login
    println!("Logging in...");
    client
        .login("your-email@example.com", "your-password")
        .await?;
    println!("[OK] Logged in\n");

    // Get locations
    let locations = client.get_locations().await?;
    let location_id = &locations[0].id;

    // Fetch multiple things concurrently
    println!("Fetching data concurrently...");
    let (system, account) = try_join!(
        client.get_location_system(location_id),
        client.get_account_info()
    )?;

    println!("[OK] Fetched system and account info\n");

    // Display results
    println!("Account: {} {}", account.first_name, account.last_name);
    println!("Zones in {}: {}", system.name, system.zones.len());

    // Update multiple zones concurrently
    if system.zones.len() >= 2 {
        println!("\nUpdating multiple zones concurrently...");
        
        let zone1_id = &system.zones[0].id;
        let zone2_id = &system.zones[1].id;
        
        try_join!(
            client.set_zone_temperature(zone1_id, 21.0, true, 0, 0),
            client.set_zone_temperature(zone2_id, 20.0, true, 0, 0)
        )?;

        println!("[OK] Updated {} zones", 2);
    }

    Ok(())
}
