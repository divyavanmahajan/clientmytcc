//! Data models for the MyTotalConnectComfort API.

use serde::{Deserialize, Deserializer, Serialize};
use crate::types::SetPointStatus;

/// Helper to deserialize null or missing lists as empty vectors
fn deserialize_null_as_empty<'de, D, T>(deserializer: D) -> Result<Vec<T>, D::Error>
where
    D: Deserializer<'de>,
    T: Deserialize<'de>,
{
    let opt = Option::deserialize(deserializer)?;
    Ok(opt.unwrap_or_default())
}

/// Represents a heating zone (room) in the system.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Zone {
    /// Zone ID
    pub id: String,
    
    /// Zone name (e.g., "Livingroom")
    pub name: Option<String>,
    
    /// Current temperature in Celsius
    pub temperature: f64,
    
    /// Target temperature setpoint
    pub target_heat_temperature: f64,
    
    /// Minimum allowed temperature
    pub min_heat_setpoint: f64,
    
    /// Maximum allowed temperature
    pub max_heat_setpoint: f64,
    
    /// Whether the zone is online
    pub is_alive: bool,
    
    /// Device ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub device_id: Option<i64>,
    
    /// MAC address of the thermostat
    #[serde(skip_serializing_if = "Option::is_none")]
    pub mac_id: Option<String>,
    
    /// Thermostat model type
    #[serde(skip_serializing_if = "Option::is_none")]
    pub thermostat_model_type: Option<String>,
    
    /// Whether there are active alerts
    #[serde(default)]
    pub has_alerts: bool,
    
    /// Communication lost alert
    #[serde(default)]
    pub has_comm_lost_alert: bool,
    
    /// Battery low alert
    #[serde(default)]
    pub has_battery_low_alert: bool,
    
    /// Sensor failure alert
    #[serde(default)]
    pub has_sensor_failure_alert: bool,
    
    /// Whether manual override is active
    #[serde(default)]
    pub override_active: bool,
    
    /// Whether temperature is held permanently
    #[serde(default)]
    pub hold_temperature_permanently: bool,
    
    /// Setpoint status (0=schedule, 2=override)
    #[serde(default)]
    pub set_point_status: u8,
    
    /// Temperature units
    #[serde(default)]
    pub thermostat_units: Option<String>,
    
    /// Thermostat version
    #[serde(skip_serializing_if = "Option::is_none")]
    pub thermostat_version: Option<String>,
}

impl Zone {
    /// Get the setpoint status as an enum.
    pub fn status(&self) -> SetPointStatus {
        self.set_point_status.into()
    }
    
    /// Check if zone is following schedule.
    pub fn is_following_schedule(&self) -> bool {
        self.status() == SetPointStatus::FollowingSchedule
    }
}

/// Represents a gateway device.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Gateway {
    /// Gateway ID
    pub id: String,
    
    /// MAC address
    pub mac_id: Option<String>,
    
    /// CRC
    pub crc: Option<String>,
}

/// Represents a location (home) with heating zones.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct Location {
    /// Location ID
    pub id: String,
    
    /// Location name
    pub name: Option<String>,
    
    /// City
    #[serde(skip_serializing_if = "Option::is_none")]
    pub city: Option<String>,
    
    /// Country
    #[serde(skip_serializing_if = "Option::is_none")]
    pub country: Option<String>,
    
    /// Postal code
    #[serde(skip_serializing_if = "Option::is_none")]
    pub postcode: Option<String>,
    
    /// Street address
    #[serde(skip_serializing_if = "Option::is_none")]
    pub street_address: Option<String>,
    
    /// Owner name
    #[serde(skip_serializing_if = "Option::is_none")]
    pub owner_name: Option<String>,
    
    /// Time zone ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_zone_id: Option<String>,
    
    /// Time zone display name
    #[serde(skip_serializing_if = "Option::is_none")]
    pub time_zone_display_name: Option<String>,
    
    /// Heating system type (1=Evohome)
    #[serde(default = "default_heating_system_type")]
    pub heating_system_type: u8,
    
    /// List of zones
    #[serde(default, deserialize_with = "deserialize_null_as_empty")]
    pub zones: Vec<Zone>,
    
    /// List of gateways
    #[serde(default, deserialize_with = "deserialize_null_as_empty")]
    pub gateways: Vec<Gateway>,
    
    /// Notification emails
    #[serde(default, deserialize_with = "deserialize_null_as_empty")]
    pub notification_emails: Vec<String>,
}

fn default_heating_system_type() -> u8 {
    1
}

impl Location {
    /// Find a zone by ID.
    pub fn get_zone_by_id(&self, zone_id: &str) -> Option<&Zone> {
        self.zones.iter().find(|z| z.id == zone_id)
    }
    
    /// Find a zone by name (case-insensitive).
    pub fn get_zone_by_name(&self, name: &str) -> Option<&Zone> {
        let name_lower = name.to_lowercase();
        self.zones.iter().find(|z| z.name.as_deref().map(|n| n.to_lowercase()) == Some(name_lower.clone()))
    }
}

/// Represents user account information.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct UserInfo {
    /// Username (email)
    pub username: String,
    
    /// First name
    pub first_name: Option<String>,
    
    /// Last name
    pub last_name: Option<String>,
    
    /// Street address
    #[serde(skip_serializing_if = "Option::is_none")]
    pub street_address: Option<String>,
    
    /// City
    #[serde(skip_serializing_if = "Option::is_none")]
    pub city: Option<String>,
    
    /// Postal code
    #[serde(skip_serializing_if = "Option::is_none")]
    pub postcode: Option<String>,
    
    /// Country ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub country_id: Option<i32>,
    
    /// Country name
    #[serde(skip_serializing_if = "Option::is_none")]
    pub country_name: Option<String>,
    
    /// User language
    #[serde(skip_serializing_if = "Option::is_none")]
    pub user_language: Option<i32>,
}

/// API response wrapper.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct ApiResponse<T> {
    pub content: Option<T>,
    pub errors: Option<Vec<ApiError>>,
}

/// API error response.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct ApiError {
    pub message: String,
}

/// Login request payload.
#[derive(Debug, Serialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct LoginRequest {
    pub email_address: String,
    pub password: String,
    pub is_service_status_returned: bool,
    pub api_active: bool,
    pub api_down: bool,
    pub redirect_url: String,
    pub events: Vec<String>,
    pub form_errors: Vec<String>,
}

/// Login response content.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub struct LoginResponse {
    pub user_id: String,
    pub display_name: Option<String>,
    pub user_name: Option<String>,
}

/// Locations response content.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct LocationsContent {
    pub locations: Vec<Location>,
}

/// Location detail response content.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct LocationDetailContent {
    pub location: Location,
    #[serde(default, deserialize_with = "deserialize_null_as_empty")]
    pub gateways: Vec<Gateway>,
    #[serde(default, deserialize_with = "deserialize_null_as_empty")]
    pub notification_emails: Vec<String>,
}

/// Location system response content.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct LocationSystemContent {
    pub location_model: Location,
}

/// Account information response content.
#[derive(Debug, Deserialize)]
#[serde(rename_all = "PascalCase")]
pub(crate) struct AccountInfoContent {
    pub user_info: UserInfo,
}

/// Set temperature request payload.
#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct SetTemperatureRequest {
    pub zone_id: String,
    pub heat_temperature: String,
    pub hot_water_state_is_on: bool,
    pub is_permanent: bool,
    pub set_until_hours: String,
    pub set_until_minutes: String,
    pub location_time_offset_minutes: i32,
    pub is_following_schedule: bool,
}
