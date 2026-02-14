//! Command-line interface for MyTotalConnectComfort.

use clap::{Parser, Subcommand};
use colored::*;
use clientmytcc::{Client, Error};
use clientmytcc::types::QuickAction;
use serde::{Deserialize, Serialize};
use serde_json;
use std::path::PathBuf;
use tabled::{Table, Tabled};

#[derive(Parser)]
#[command(name = "evohome")]
#[command(about = "MyTotalConnectComfort CLI for Evohome heating control", long_about = None)]
#[command(version)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Authenticate with MyTotalConnectComfort
    Login {
        #[arg(short, long)]
        email: Option<String>,
        #[arg(short, long)]
        password: Option<String>,
    },
    
    /// Logout and clear session
    Logout,
    
    /// List all locations
    Locations,
    
    /// Show account information
    Account,
    
    /// Set zone temperature
    Set {
        zone_id: Option<String>,
        temperature: Option<String>,
        #[arg(short, long)]
        duration: Option<u32>,
        #[arg(short, long)]
        minutes: Option<u32>,
        #[arg(short, long)]
        location_id: Option<String>,
    },
    
    /// Boost all zones in a location
    Boost {
        #[arg(short, long)]
        location_id: Option<String>,
        #[arg(default_value = "22.0")]
        temp: String,
        #[arg(short, long, default_value = "2")]
        duration: u32,
        #[arg(long)]
        override_: bool,
    },
    
    /// Set all zones to energy-saving temperature
    Eco {
        #[arg(short, long)]
        location_id: Option<String>,
        #[arg(default_value = "18.0")]
        temp: String,
        #[arg(long)]
        override_: bool,
    },
    
    /// Monitor zone temperatures (alias: zones)
    #[command(alias = "zones")]
    Monitor {
        #[arg(short, long)]
        location_id: Option<String>,
        #[arg(short, long, default_value = "table")]
        format: String,
    },
    
    /// Set all zones to frost protection (vacation mode)
    Vacation {
        #[arg(short, long)]
        location_id: Option<String>,
        #[arg(default_value = "12.0")]
        temp: String,
        #[arg(long)]
        override_: bool,
    },

    /// Reset all zones to follow their programmed schedule
    Schedule {
        #[arg(short, long)]
        location_id: Option<String>,
    },
}

#[derive(Tabled)]
struct LocationRow {
    #[tabled(rename = "ID")]
    id: String,
    #[tabled(rename = "Name")]
    name: String,
    #[tabled(rename = "City")]
    city: String,
    #[tabled(rename = "Zones")]
    zones: usize,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let start_time = std::time::Instant::now();
    let cli = Cli::parse();

    match cli.command {
        Commands::Login { email, password } => {
            let email = email
                .or_else(|| std::env::var("EVOHOME_USER").ok())
                .or_else(|| std::env::var("EVOHOME_EMAIL").ok())
                .ok_or_else(|| {
                    Error::Authentication("Email not provided and EVOHOME_USER/EVOHOME_EMAIL not set".to_string())
                })?;

            let pwd = password
                .or_else(|| std::env::var("EVOHOME_PASSWORD").ok())
                .unwrap_or_else(|| rpassword::prompt_password("Password: ").unwrap_or_default());

            if pwd.is_empty() {
                eprintln!("{} Password is required", "[ERROR]".red());
                std::process::exit(1);
            }

            let mut client = Client::new();
            match client.login(&email, &pwd).await {
                Ok((response, cookies)) => {
                    if let Err(e) = save_session(&email, cookies) {
                        eprintln!("{} Failed to save session: {}", "[WARNING]".yellow(), e);
                    }
                    println!("{} Logged in as: {}", "[OK]".green(), response.display_name.as_deref().unwrap_or("Unknown"));
                    println!("User ID: {}", response.user_id);
                }
                Err(Error::Authentication(msg)) => {
                    eprintln!("{} Authentication failed: {}", "[ERROR]".red(), msg);
                    std::process::exit(1);
                }
                Err(e) => {
                    eprintln!("{} Error: {}", "[ERROR]".red(), e);
                    std::process::exit(1);
                }
            }
        }

        Commands::Logout => {
            let config_path = get_config_path();
            if config_path.exists() {
                std::fs::remove_file(&config_path)?;
                println!("{} Logged out and session cleared", "[OK]".green());
            } else {
                println!("{} No active session found", "[INFO]".dimmed());
            }
        }

        Commands::Locations => {
            let client = get_authenticated_client().await?;
            let locations = client.get_locations().await?;

            let table = Table::new(
                locations.iter().map(|l| LocationRow {
                    id: l.id.clone(),
                    name: l.name.as_deref().unwrap_or("Unknown").to_string(),
                    city: l.city.as_deref().unwrap_or("Unknown").to_string(),
                    zones: l.zones.len(), // Note: this might be 0 if not detailed
                })
            );
            println!("{}", table);
        }

        Commands::Account => {
            let client = get_authenticated_client().await?;
            let info = client.get_account_info().await?;

            println!("{}", "Account Information".bold());
            println!("Name: {} {}", info.first_name.as_deref().unwrap_or(""), info.last_name.as_deref().unwrap_or(""));
            println!("Email: {}", info.username);
            if let (Some(city), Some(country)) = (&info.city, &info.country_name) {
                println!("Location: {}, {}", city, country);
            }
        }

        Commands::Set { zone_id, temperature, duration, minutes, location_id } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let zone_id = select_zone(&client, &location_id, zone_id).await?;
            
            let temp_str = match temperature {
                Some(t) => t,
                None => prompt("Enter temperature (e.g. 21C): ")?,
            };
            let temp = parse_temperature(&temp_str).map_err(|e| format!("Invalid temperature: {}", e))?;

            let (permanent, h, m) = match (duration, minutes) {
                (Some(h), Some(m)) => (false, h, m),
                (Some(h), None) => (false, h, 0),
                (None, Some(m)) => (false, 0, m),
                (None, None) => (true, 0, 0),
            };

            client.set_zone_temperature(&zone_id, temp, permanent, h, m, false).await?;

            if permanent {
                println!("{} Set zone {} to {}°C (permanent)", "[OK]".green(), zone_id, temp);
                println!("{} Command to skip selection: evohome set {} {}C", "[INFO]".dimmed(), zone_id, temp);
            } else {
                println!("{} Set zone {} to {}°C for {}h {}m", "[OK]".green(), zone_id, temp, h, m);
                println!("{} Command to skip selection: evohome set {} {}C -d {} -m {}", "[INFO]".dimmed(), zone_id, temp, h, m);
            }
        }

        Commands::Boost { location_id, temp, duration, override_ } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let temp = parse_temperature(&temp).map_err(|e| format!("Invalid temperature: {}", e))?;
            
            let system = client.get_location_system(&location_id).await
                .map_err(|e| format!("Failed to get location system (initial): {}", e))?;

            let mut count = 0;
            let mut skipped = 0;
            for zone in &system.zones {
                if zone.is_alive {
                    // Skip if target is 5.0 (off/frost protect) unless override is set
                    if (zone.target_heat_temperature - 5.0).abs() < 0.1 && !override_ {
                        println!("{} Skipped {} (Target is 5.0°C). Use --override to force.", "[INFO]".blue(), zone.name.as_deref().unwrap_or("Unknown"));
                        skipped += 1;
                        continue;
                    }

                    client.set_zone_temperature(&zone.id, temp, false, duration, 0, false).await
                        .map_err(|e| format!("Failed to set temperature for zone {}: {}", zone.name.as_deref().unwrap_or("Unknown"), e))?;
                    count += 1;
                    println!("{} Boosted {} to {}°C for {}h", "[OK]".green(), zone.name.as_deref().unwrap_or("Unknown"), temp, duration);
                }
            }

            println!("\n{} Boosted {} zones ({} skipped)", "[OK]".green().bold(), count, skipped);
            
            // Refresh system status to show changes
            println!();
            let system = client.get_location_system(&location_id).await
                .map_err(|e| format!("Failed to get location system (refresh): {}", e))?;
            print_status_table(&system);
        }

        Commands::Eco { location_id, temp, override_ } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let temp = parse_temperature(&temp).map_err(|e| format!("Invalid temperature: {}", e))?;
            
            let system = client.get_location_system(&location_id).await?;

            let mut count = 0;
            let mut skipped = 0;
            for zone in &system.zones {
                if zone.is_alive && zone.target_heat_temperature > temp {
                    // Skip if target is 5.0 (off/frost protect) unless override is set
                    if (zone.target_heat_temperature - 5.0).abs() < 0.1 && !override_ {
                        println!("{} Skipped {} (Target is 5.0°C). Use --override to force.", "[INFO]".blue(), zone.name.as_deref().unwrap_or("Unknown"));
                        skipped += 1;
                        continue;
                    }

                    client.set_zone_temperature(&zone.id, temp, true, 0, 0, false).await?;
                    count += 1;
                    println!("{} Set {} to eco mode", "[OK]".green(), zone.name.as_deref().unwrap_or("Unknown"));
                }
            }

            println!("\n{} Set {} zones to eco mode ({} skipped)", "[OK]".green().bold(), count, skipped);
            
            // Refresh system status to show changes
            println!();
            let system = client.get_location_system(&location_id).await?;
            print_status_table(&system);
        }

        Commands::Monitor { location_id, format } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let system = client.get_location_system(&location_id).await?;

            if format == "json" {
                println!("{}", serde_json::to_string_pretty(&system).unwrap());
            } else {
                // Show Quick Action status if active
                if let Some(status) = &system.system_mode_status {
                    let action = status.action();
                    if action != QuickAction::Auto {
                        let perm_str = if status.is_permanent { "Permanent" } else { "Temporary" };
                        println!("{} Active System Mode: {} ({})", "[INFO]".blue(), action, perm_str);
                        println!();
                    }
                }

                loop {
                    // In a real monitor we'd refresh, but for now just show once or loop?
                    // The original code just showed it once. Let's keep it simple.
                    for zone in &system.zones {
                        println!("{}", format_zone_monitor_row(zone));
                    }
                    break; // Just run once for now
                }
            }
        }

        Commands::Vacation { location_id, temp, override_ } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let temp = parse_temperature(&temp).map_err(|e| format!("Invalid temperature: {}", e))?;
            
            let system = client.get_location_system(&location_id).await?;

            let mut count = 0;
            let mut skipped = 0;
            for zone in &system.zones {
                if zone.is_alive {
                    // Skip if target is 5.0 (off/frost protect) unless override is set
                    if (zone.target_heat_temperature - 5.0).abs() < 0.1 && !override_ {
                        println!("{} Skipped {} (Target is 5.0°C). Use --override to force.", "[INFO]".blue(), zone.name.as_deref().unwrap_or("Unknown"));
                        skipped += 1;
                        continue;
                    }

                    client.set_zone_temperature(&zone.id, temp, true, 0, 0, false).await?;
                    count += 1;
                }
            }

            println!(
                "{} Vacation mode activated ({}°C)",
                "[OK]".green(),
                temp
            );
            println!("Set {} zones to frost protection ({} skipped)", count, skipped);
            
            // Refresh system status to show changes
            println!();
            let system = client.get_location_system(&location_id).await?;
            print_status_table(&system);
        }

        Commands::Schedule { location_id } => {
            let client = get_authenticated_client().await?;
            let location_id = select_location(&client, location_id).await?;
            let system = client.get_location_system(&location_id).await?;

            let mut count = 0;
            for zone in &system.zones {
                if zone.is_alive {
                    // Set to follow schedule by setting permanent=False with 0 duration
                    // and is_following_schedule=True
                    client.set_zone_temperature(
                        &zone.id, 
                        0.0,   // Temperature ignored when following schedule
                        false, // permanent
                        0,     // duration_hours
                        0,     // duration_minutes
                        true   // is_following_schedule
                    ).await?;
                    count += 1;
                    println!("{} {} now following schedule", "[OK]".green(), zone.name.as_deref().unwrap_or("Unknown"));
                }
            }

            println!("\n{} Reset {} zones to follow schedule", "[OK]".green().bold(), count);
        }
    }

    let duration = start_time.elapsed();
    println!("\nDone in {:.2}s", duration.as_secs_f64());
    Ok(())
}



#[derive(Serialize, Deserialize)]
struct Session {
    email: String,
    cookies: Vec<String>,
}

fn get_config_path() -> PathBuf {
    let mut path = dirs::home_dir().expect("Could not find home directory");
    path.push(".config");
    path.push("clientmytcc");
    std::fs::create_dir_all(&path).ok();
    path.push("session.json");
    path
}

fn save_session(email: &str, cookies: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    let session = Session {
        email: email.to_string(),
        cookies,
    };
    let path = get_config_path();
    let file = std::fs::File::create(path)?;
    serde_json::to_writer(file, &session)?;
    Ok(())
}

fn load_session() -> Option<Session> {
    let path = get_config_path();
    if !path.exists() {
        return None;
    }
    let file = std::fs::File::open(path).ok()?;
    serde_json::from_reader(file).ok()
}

async fn get_authenticated_client() -> Result<Client, Box<dyn std::error::Error>> {
    // Helper to try login with env vars
    async fn try_env_login() -> Result<Client, Box<dyn std::error::Error>> {
        let email = std::env::var("EVOHOME_USER")
            .or_else(|_| std::env::var("EVOHOME_EMAIL"))
            .map_err(|_| "Env vars not set")?;
        let password = std::env::var("EVOHOME_PASSWORD").map_err(|_| "Env vars not set")?;

        let mut client = Client::new();
        let (_, cookies) = client.login(&email, &password).await?;
        save_session(&email, cookies)?;
        Ok(client)
    }

    // 1. Try loading session
    if let Some(session) = load_session() {
        let client = Client::with_cookies(session.cookies);
        
        // 2. Validate session (lightweight check)
        match client.get_account_info().await {
            Ok(_) => return Ok(client),
            Err(Error::Authentication(_)) | Err(Error::Api(_)) => {
                eprintln!("{} Session expired, attempting auto-login...", "[WARNING]".yellow());
            }
            Err(e) => return Err(Box::new(e)),
        }
    }

    // 3. Fallback to env vars
    match try_env_login().await {
        Ok(client) => {
            eprintln!("{} Auto-logged in using environment variables", "[OK]".green());
            Ok(client)
        }
        Err(_) => {
            eprintln!(
                "{} Not authenticated. Please run 'evohome login' or set EVOHOME_USER/EVOHOME_PASSWORD.",
                "[ERROR]".red()
            );
            std::process::exit(1);
        }
    }
}

// --- Helpers ---

fn parse_temperature(s: &str) -> Result<f64, String> {
    let s = s.trim().to_uppercase();
    if s.ends_with('F') {
        let val = s[..s.len() - 1].parse::<f64>().map_err(|_| "Invalid number")?;
        Ok((val - 32.0) * 5.0 / 9.0)
    } else if s.ends_with('C') {
        let val = s[..s.len() - 1].parse::<f64>().map_err(|_| "Invalid number")?;
        Ok(val)
    } else {
        s.parse::<f64>().map_err(|_| "Invalid number".to_string())
    }
}

fn format_zone_status_row(zone: &clientmytcc::Zone) -> String {
    let diff = zone.target_heat_temperature - zone.temperature;
    let status = if zone.target_heat_temperature == 5.0 { "Off" } else if diff > 0.5 { "Heating" } else { "Stable" };
    let _online_str = if zone.is_alive { "Online".green() } else { "Offline".red() };
    
    let temp_str = if zone.temperature >= 128.0 {
        "--".to_string()
    } else {
        format!("{:>5.1}°C", zone.temperature)
    };

    let diff_str = if zone.temperature >= 128.0 {
        "--".to_string()
    } else {
        format!("{:>+6.1}°C", diff)
    };
    
    format!(
        "{:<20} ({} -> {:>5.1}°C) {} {:<8} {:>8}",
        zone.name.as_deref().unwrap_or("Unknown").bold(),
        temp_str,
        zone.target_heat_temperature,
        diff_str,
        status.yellow(),
        zone.id
    )
}

fn format_zone_monitor_row(zone: &clientmytcc::Zone) -> String {
    let diff = zone.target_heat_temperature - zone.temperature;
    let status = if zone.target_heat_temperature == 5.0 { "Off" } else if diff > 0.5 { "Heating" } else { "Stable" };
    let online_str = if zone.is_alive { "Online".green() } else { "Offline".red() };
    
    let temp_str = if zone.temperature >= 128.0 {
        "--".to_string()
    } else {
        format!("{:>5.1}°C", zone.temperature)
    };

    let diff_str = if zone.temperature >= 128.0 {
        "--".to_string()
    } else {
        format!("{:>+6.1}°C", diff)
    };
    
    format!(
        "{:<20} ({} -> {:>5.1}°C) {} {:<8} {:<8} {:>8}",
        zone.name.as_deref().unwrap_or("Unknown").bold(),
        temp_str,
        zone.target_heat_temperature,
        diff_str,
        status.yellow(),
        online_str,
        zone.id
    )
}

fn print_status_table(system: &clientmytcc::Location) {
    for zone in &system.zones {
        println!("{}", format_zone_status_row(zone));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use clientmytcc::Zone;

    #[test]
    fn test_format_zone_status_row() {
        let zone = Zone {
            id: "12345".to_string(),
            name: Some("Living Room".to_string()),
            temperature: 20.0,
            target_heat_temperature: 22.0,
            is_alive: true,
            has_alerts: false,
            has_battery_low_alert: false,
            has_comm_lost_alert: false,
            has_sensor_failure_alert: false,
            min_heat_setpoint: 5.0,
            max_heat_setpoint: 35.0,
            override_active: false,
            hold_temperature_permanently: false,
            device_id: None,
            mac_id: None,
            thermostat_model_type: None,
            set_point_status: 0,
            thermostat_units: None,
            thermostat_version: None,
        };

        let output = format_zone_status_row(&zone);
        assert!(output.contains("Living Room"));
        assert!(output.contains("20.0°C"));
        assert!(output.contains("22.0°C"));
        assert!(output.contains("+2.0°C"));
        assert!(output.contains("Heating"));
        assert!(output.contains("12345"));
    }

    #[test]
    fn test_format_zone_monitor_row() {
        let zone = Zone {
            id: "67890".to_string(),
            name: Some("Bedroom".to_string()),
            temperature: 19.0,
            target_heat_temperature: 19.0,
            is_alive: false,
            has_alerts: false,
            has_battery_low_alert: false,
            has_comm_lost_alert: false,
            has_sensor_failure_alert: false,
            min_heat_setpoint: 5.0,
            max_heat_setpoint: 35.0,
            override_active: false,
            hold_temperature_permanently: false,
            device_id: None,
            mac_id: None,
            thermostat_model_type: None,
            set_point_status: 0,
            thermostat_units: None,
            thermostat_version: None,
        };

        let output = format_zone_monitor_row(&zone);
        assert!(output.contains("Bedroom"));
        assert!(output.contains("19.0°C"));
        assert!(output.contains("+0.0°C"));
        assert!(output.contains("Stable"));
        assert!(output.contains("Offline"));
        assert!(output.contains("67890"));
    }
}

fn prompt(message: &str) -> Result<String, Box<dyn std::error::Error>> {
    use std::io::{self, Write};
    print!("{}", message);
    io::stdout().flush()?;
    let mut input = String::new();
    io::stdin().read_line(&mut input)?;
    Ok(input.trim().to_string())
}

async fn select_location(client: &Client, id: Option<String>) -> Result<String, Box<dyn std::error::Error>> {
    if let Some(id) = id {
        return Ok(id);
    }

    // Check config for default (not implemented yet, skipping)

    let locations = client.get_locations().await?;
    if locations.is_empty() {
        return Err("No locations found".into());
    }

    if locations.len() == 1 {
        let loc = &locations[0];
        println!("{} Using location: {}", "[INFO]".dimmed(), loc.name.as_deref().unwrap_or("Unknown"));
        return Ok(loc.id.clone());
    }

    println!("{}", "Select a location:".bold());
    for (i, loc) in locations.iter().enumerate() {
        println!("{}. {} ({})", i + 1, loc.name.as_deref().unwrap_or("Unknown"), loc.city.as_deref().unwrap_or("Unknown"));
    }

    loop {
        let input = prompt("Enter number: ")?;
        if let Ok(idx) = input.parse::<usize>() {
            if idx > 0 && idx <= locations.len() {
                let loc = &locations[idx - 1];
                println!("{} Selected: {}", "[OK]".green(), loc.name.as_deref().unwrap_or("Unknown"));
                return Ok(loc.id.clone());
            }
        }
        println!("{}", "Invalid selection".red());
    }
}

async fn select_zone(client: &Client, location_id: &str, id: Option<String>) -> Result<String, Box<dyn std::error::Error>> {
    if let Some(id) = id {
        // If it looks like an ID (numeric), use it
        if id.chars().all(char::is_numeric) {
            return Ok(id);
        }
        
        // Otherwise try to match by name
        let system = client.get_location_system(location_id).await?;
        let search = id.to_lowercase();
        let matches: Vec<_> = system.zones.iter()
            .filter(|z| z.name.as_deref().unwrap_or("").to_lowercase().starts_with(&search))
            .collect();

        if matches.is_empty() {
            return Err(format!("No zone found matching '{}'", id).into());
        } else if matches.len() == 1 {
            let zone = matches[0];
            println!("{} Using zone: {}", "[INFO]".dimmed(), zone.name.as_deref().unwrap_or("Unknown"));
            return Ok(zone.id.clone());
        } else {
            println!("{}", format!("Multiple zones match '{}':", id).yellow());
            for (i, zone) in matches.iter().enumerate() {
                let temp_str = if zone.temperature >= 128.0 { "--".to_string() } else { format!("{:>5.1}°C", zone.temperature) };
                println!(
                    "{:>2}.  {:>8}: ({} --> {:>5.1}°C) {:<20}", 
                    i + 1, 
                    zone.id,
                    temp_str,
                    zone.target_heat_temperature,
                    zone.name.as_deref().unwrap_or("Unknown")
                );
            }
            // Fall through to prompt logic below, but restricted to matches? 
            // For simplicity, just let user pick from matches
             loop {
                let input = prompt("Enter number: ")?;
                if let Ok(idx) = input.parse::<usize>() {
                    if idx > 0 && idx <= matches.len() {
                        let zone = matches[idx - 1];
                        println!("{} Selected: {}", "[OK]".green(), zone.name.as_deref().unwrap_or("Unknown"));
                        return Ok(zone.id.clone());
                    }
                }
                println!("{}", "Invalid selection".red());
            }
        }
    }

    // No ID provided, list all zones
    let system = client.get_location_system(location_id).await?;
    if system.zones.is_empty() {
        return Err("No zones found".into());
    }

    if system.zones.len() == 1 {
        let zone = &system.zones[0];
        println!("{} Using zone: {}", "[INFO]".dimmed(), zone.name.as_deref().unwrap_or("Unknown"));
        return Ok(zone.id.clone());
    }

    println!("{}", format!("Select a zone in {}:", system.name.as_deref().unwrap_or("Unknown")).bold());
    for (i, zone) in system.zones.iter().enumerate() {
        let temp_str = if zone.temperature >= 128.0 { "--".to_string() } else { format!("{:>5.1}°C", zone.temperature) };
        println!(
            "{:>2}.  {:>8}: ({} --> {:>5.1}°C) {:<20}", 
            i + 1, 
            zone.id,
            temp_str,
            zone.target_heat_temperature,
            zone.name.as_deref().unwrap_or("Unknown")
        );
    }

    loop {
        let input = prompt("Enter number: ")?;
        if let Ok(idx) = input.parse::<usize>() {
            if idx > 0 && idx <= system.zones.len() {
                let zone = &system.zones[idx - 1];
                println!("{} Selected: {}", "[OK]".green(), zone.name.as_deref().unwrap_or("Unknown"));
                return Ok(zone.id.clone());
            }
        }
        println!("{}", "Invalid selection".red());
    }
}
