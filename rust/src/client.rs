//! Main API client for MyTotalConnectComfort.

use reqwest::{cookie::Jar, Client as HttpClient};
use std::sync::Arc;

use crate::{
    error::{Error, Result},
    models::*,
};

const BASE_URL: &str = "https://international.mytotalconnectcomfort.com";

/// Client for the MyTotalConnectComfort API.
///
/// # Example
///
/// ```no_run
/// use mytcc_rs::Client;
///
/// #[tokio::main]
/// async fn main() -> Result<(), Box<dyn std::error::Error>> {
///     let mut client = Client::new();
///     client.login("user@example.com", "password").await?;
///     
///     let locations = client.get_locations().await?;
///     for location in locations {
///         println!("{}: {} zones", location.name.as_deref().unwrap_or("Unknown"), location.zones.len());
///     }
///     Ok(())
/// }
/// ```
pub struct Client {
    http_client: HttpClient,
    #[allow(dead_code)] // Used internally by reqwest
    cookie_jar: Arc<Jar>,
    authenticated: bool,
}

impl Client {
    /// Create a new API client.
    pub fn new() -> Self {
        let cookie_jar = Arc::new(Jar::default());
        let http_client = HttpClient::builder()
            .cookie_provider(Arc::clone(&cookie_jar))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            http_client,
            cookie_jar,
            authenticated: false,
        }
    }

    /// Authenticate with the API.
    ///
    /// # Arguments
    ///
    /// * `email` - User email address
    /// * `password` - User password
    ///
    /// # Returns
    ///
    /// Login response with user information
    ///
    /// # Errors
    ///
    /// Returns `Error::Authentication` if login fails
    /// Create a new API client with existing session cookies.
    pub fn with_cookies(cookies: Vec<String>) -> Self {
        let cookie_jar = Arc::new(Jar::default());
        let url = BASE_URL.parse().unwrap();
        
        for cookie in cookies {
            cookie_jar.add_cookie_str(&cookie, &url);
        }

        let http_client = HttpClient::builder()
            .cookie_provider(Arc::clone(&cookie_jar))
            .build()
            .expect("Failed to create HTTP client");

        Self {
            http_client,
            cookie_jar,
            authenticated: true, // Assume authenticated if cookies provided
        }
    }

    /// Authenticate with the API.
    ///
    /// # Arguments
    ///
    /// * `email` - User email address
    /// * `password` - User password
    ///
    /// # Returns
    ///
    /// Login response with user information and session cookies
    ///
    /// # Errors
    ///
    /// Returns `Error::Authentication` if login fails
    pub async fn login(&mut self, email: &str, password: &str) -> Result<(LoginResponse, Vec<String>)> {
        // First, get the login page to obtain CSRF tokens
        let login_page_url = format!("{}/Account/Login", BASE_URL);
        self.http_client.get(&login_page_url).send().await?;

        // Prepare login request
        let login_url = format!("{}/api/accountApi/login", BASE_URL);
        let request_body = LoginRequest {
            email_address: email.to_string(),
            password: password.to_string(),
            is_service_status_returned: true,
            api_active: true,
            api_down: false,
            redirect_url: String::new(),
            events: vec![],
            form_errors: vec![],
        };

        let response = self
            .http_client
            .post(&login_url)
            .header("Content-Type", "application/json;charset=utf-8")
            .header("X-Requested-With", "XMLHttpRequest")
            .json(&request_body)
            .send()
            .await?;

        if response.status() == 401 {
            return Err(Error::Authentication("Invalid email or password".to_string()));
        }

        // Capture cookies
        let cookies: Vec<String> = response
            .headers()
            .get_all("set-cookie")
            .iter()
            .filter_map(|h| h.to_str().ok().map(|s| s.to_string()))
            .collect();

        let api_response: ApiResponse<LoginResponse> = response.json().await?;

        if let Some(errors) = api_response.errors {
            let error_msg = errors
                .iter()
                .map(|e| e.message.as_str())
                .collect::<Vec<_>>()
                .join("; ");
            return Err(Error::Authentication(error_msg));
        }

        self.authenticated = true;
        let user_data = api_response
            .content
            .ok_or_else(|| Error::InvalidResponse("Missing login response content".to_string()))?;
            
        Ok((user_data, cookies))
    }

    /// Logout from the API.
    ///
    /// This invalidates the current session.
    pub async fn logout(&self) -> Result<()> {
        let url = format!("{}/Account/Logout?message=logout", BASE_URL);
        let _response = self.http_client.get(&url).send().await?;
        Ok(())
    }

    /// Get all locations associated with the account.
    ///
    /// # Returns
    ///
    /// Vector of locations
    ///
    /// # Errors
    ///
    /// Returns `Error::Authentication` if not authenticated
    pub async fn get_locations(&self) -> Result<Vec<Location>> {
        self.ensure_authenticated()?;

        let url = format!("{}/api/locationsapi/getlocations", BASE_URL);
        let response = self.http_client.get(&url).send().await?;

        let api_response: ApiResponse<LocationsContent> = response.json().await?;
        self.check_errors(&api_response.errors)?;

        Ok(api_response
            .content
            .map(|c| c.locations)
            .unwrap_or_default())
    }

    /// Get detailed information about a specific location.
    ///
    /// # Arguments
    ///
    /// * `location_id` - The location ID
    ///
    /// # Returns
    ///
    /// Location with detailed information
    pub async fn get_location(&self, location_id: &str) -> Result<Location> {
        self.ensure_authenticated()?;

        let url = format!("{}/Api/LocationsApi/GetLocation", BASE_URL);
        let response = self
            .http_client
            .get(&url)
            .query(&[("id", location_id)])
            .send()
            .await?;

        let api_response: ApiResponse<LocationDetailContent> = response.json().await?;
        self.check_errors(&api_response.errors)?;

        let content = api_response
            .content
            .ok_or_else(|| Error::LocationNotFound(location_id.to_string()))?;

        let mut location = content.location;
        location.gateways = content.gateways;
        location.notification_emails = content.notification_emails;

        Ok(location)
    }

    /// Get the heating system configuration and zone status for a location.
    ///
    /// # Arguments
    ///
    /// * `location_id` - The location ID
    ///
    /// # Returns
    ///
    /// Location with zones and system status
    pub async fn get_location_system(&self, location_id: &str) -> Result<Location> {
        self.ensure_authenticated()?;

        let url = format!("{}/Api/LocationsApi/GetLocationSystem", BASE_URL);
        let response = self
            .http_client
            .get(&url)
            .query(&[("id", location_id)])
            .send()
            .await?;

        let api_response: ApiResponse<LocationSystemContent> = response.json().await?;
        self.check_errors(&api_response.errors)?;

        api_response
            .content
            .map(|c| c.location_model)
            .ok_or_else(|| Error::LocationNotFound(location_id.to_string()))
    }

    /// Get account information for the authenticated user.
    ///
    /// # Returns
    ///
    /// User account information
    pub async fn get_account_info(&self) -> Result<UserInfo> {
        self.ensure_authenticated()?;

        let url = format!("{}/api/accountApi/getAccountInformation", BASE_URL);
        let response = self.http_client.get(&url).send().await?;

        let api_response: ApiResponse<AccountInfoContent> = response.json().await?;
        self.check_errors(&api_response.errors)?;

        api_response
            .content
            .map(|c| c.user_info)
            .ok_or_else(|| Error::InvalidResponse("Missing account info".to_string()))
    }

    /// Set the target temperature for a heating zone.
    ///
    /// # Arguments
    ///
    /// * `zone_id` - The zone ID
    /// * `temperature` - Target temperature in Celsius
    /// * `permanent` - Whether to hold temperature permanently
    /// * `duration_hours` - Hours to hold temperature (if not permanent)
    /// * `duration_minutes` - Minutes to hold temperature (if not permanent)
    pub async fn set_zone_temperature(
        &self,
        zone_id: &str,
        temperature: f64,
        permanent: bool,
        duration_hours: u32,
        duration_minutes: u32,
        is_following_schedule: bool,
    ) -> Result<()> {
        self.ensure_authenticated()?;

        let url = format!("{}/api/ZonesApi/SetZoneTemperature", BASE_URL);
        let request_body = SetTemperatureRequest {
            zone_id: zone_id.to_string(),
            heat_temperature: temperature.to_string(),
            hot_water_state_is_on: false,
            is_permanent: permanent,
            set_until_hours: format!("{:02}", duration_hours),
            set_until_minutes: format!("{:02}", duration_minutes),
            location_time_offset_minutes: 60,
            is_following_schedule,
        };

        let response = self
            .http_client
            .post(&url)
            .header("Content-Type", "application/json;charset=utf-8")
            .header("X-Requested-With", "XMLHttpRequest")
            .json(&request_body)
            .send()
            .await?;
        let response_status = response.status();
        let text = response.text().await?;

        if !response_status.is_success() {
            return Err(Error::Api(format!("API Error {}: {}", response_status, text)));
        }
        
        // Try to parse as JSON
        let api_response: ApiResponse<()> = match serde_json::from_str(&text) {
            Ok(r) => r,
            Err(e) => {
                return Err(Error::Api(format!("Failed to decode response: {}. Status: {}. Text: '{}'", e, response_status, text)));
            }
        };
        
        self.check_errors(&api_response.errors)?;

        Ok(())
    }

    /// Get a specific zone by ID.
    ///
    /// # Arguments
    ///
    /// * `location_id` - The location ID
    /// * `zone_id` - The zone ID
    ///
    /// # Returns
    ///
    /// Zone information
    pub async fn get_zone(&self, location_id: &str, zone_id: &str) -> Result<Zone> {
        let location = self.get_location_system(location_id).await?;
        location
            .get_zone_by_id(zone_id)
            .cloned()
            .ok_or_else(|| Error::ZoneNotFound(zone_id.to_string()))
    }

    /// Get a specific zone by name.
    ///
    /// # Arguments
    ///
    /// * `location_id` - The location ID
    /// * `zone_name` - The zone name
    ///
    /// # Returns
    ///
    /// Zone information
    pub async fn get_zone_by_name(&self, location_id: &str, zone_name: &str) -> Result<Zone> {
        let location = self.get_location_system(location_id).await?;
        location
            .get_zone_by_name(zone_name)
            .cloned()
            .ok_or_else(|| Error::ZoneNotFound(zone_name.to_string()))
    }

    fn ensure_authenticated(&self) -> Result<()> {
        if !self.authenticated {
            return Err(Error::Authentication(
                "Not authenticated. Please call login() first".to_string(),
            ));
        }
        Ok(())
    }

    fn check_errors(&self, errors: &Option<Vec<ApiError>>) -> Result<()> {
        if let Some(errs) = errors {
            if !errs.is_empty() {
                let error_msg = errs
                    .iter()
                    .map(|e| e.message.as_str())
                    .collect::<Vec<_>>()
                    .join("; ");
                return Err(Error::Api(error_msg));
            }
        }
        Ok(())
    }
}

impl Default for Client {
    fn default() -> Self {
        Self::new()
    }
}
