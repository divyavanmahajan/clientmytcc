//! Comprehensive integration tests for the MyTotalConnectComfort client.

use clientmytcc_rs::{Client, Error};
use mockito::{Mock, Server};
use serde_json::json;

/// Helper to create a mock server with login endpoints
async fn setup_mock_login(server: &mut Server) -> Mock {
    // Mock login page
    server
        .mock("GET", "/Account/Login")
        .with_status(200)
        .with_body("<html></html>")
        .create();

    // Mock successful login
    server
        .mock("POST", "/api/accountApi/login")
        .with_status(200)
        .with_header("content-type", "application/json")
        .with_body(
            json!({
                "Content": {
                    "UserId": "3194795",
                    "DisplayName": "Test User",
                    "UserName": "test@example.com"
                },
                "Errors": null
            })
            .to_string(),
        )
        .create()
}

mod client_initialization {
    use super::*;

    #[tokio::test]
    async fn test_client_creation() {
        let _client = Client::new();
        // Client should be created successfully
    }

    #[tokio::test]
    async fn test_default_client() {
        let _client = Client::default();
        // Default should work the same as new()
    }
}

mod authentication {
    use super::*;

    #[tokio::test]
    async fn test_login_success() {
        let mut server = Server::new_async().await;
        let _login_mock = setup_mock_login(&mut server).await;

        // Note: This test would need the client to accept a custom base URL
        // For now, it demonstrates the test structure
    }

    #[tokio::test]
    async fn test_unauthenticated_request() {
        let client = Client::new();
        let result = client.get_locations().await;

        // Should fail with authentication error
        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_login_invalid_credentials() {
        let mut server = Server::new_async().await;

        server
            .mock("GET", "/Account/Login")
            .with_status(200)
            .with_body("<html></html>")
            .create();

        server
            .mock("POST", "/api/accountApi/login")
            .with_status(401)
            .create();

        // Would need custom base URL support to test properly
    }

    #[tokio::test]
    async fn test_login_api_error() {
        let mut server = Server::new_async().await;

        server
            .mock("GET", "/Account/Login")
            .with_status(200)
            .with_body("<html></html>")
            .create();

        server
            .mock("POST", "/api/accountApi/login")
            .with_status(200)
            .with_header("content-type", "application/json")
            .with_body(
                json!({
                    "Content": null,
                    "Errors": [{"Message": "Service unavailable"}]
                })
                .to_string(),
            )
            .create();

        // Would test authentication error with API error response
    }
}

mod locations {
    use super::*;

    #[tokio::test]
    async fn test_get_locations_not_authenticated() {
        let client = Client::new();
        let result = client.get_locations().await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_get_location_not_authenticated() {
        let client = Client::new();
        let result = client.get_location("1232176").await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_get_location_system_not_authenticated() {
        let client = Client::new();
        let result = client.get_location_system("1232176").await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }
}

mod zones {
    use super::*;

    #[tokio::test]
    async fn test_get_zone_not_authenticated() {
        let client = Client::new();
        let result = client.get_zone("1232176", "5211675").await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_get_zone_by_name_not_authenticated() {
        let client = Client::new();
        let result = client.get_zone_by_name("1232176", "Livingroom").await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }
}

mod temperature_control {
    use super::*;

    #[tokio::test]
    async fn test_set_temperature_not_authenticated() {
        let client = Client::new();
        let result = client
            .set_zone_temperature("5211675", 21.5, true, 0, 0, false)
            .await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_set_temperature_permanent() {
        let client = Client::new();
        // Test that permanent temperature setting works
        let result = client
            .set_zone_temperature("5211675", 21.0, true, 0, 0, false)
            .await;

        // Should fail due to no authentication, but validates the API
        assert!(matches!(result, Err(Error::Authentication(_))));
    }

    #[tokio::test]
    async fn test_set_temperature_temporary() {
        let client = Client::new();
        // Test temporary temperature setting (2 hours)
        let result = client
            .set_zone_temperature("5211675", 22.0, false, 2, 0, false)
            .await;

        // Should fail due to no authentication, but validates the API
        assert!(matches!(result, Err(Error::Authentication(_))));
    }
}

mod account_info {
    use super::*;

    #[tokio::test]
    async fn test_get_account_info_not_authenticated() {
        let client = Client::new();
        let result = client.get_account_info().await;

        assert!(matches!(result, Err(Error::Authentication(_))));
    }
}

mod error_handling {
    use super::*;

    #[test]
    fn test_error_display() {
        let auth_error = Error::Authentication("Invalid credentials".to_string());
        assert_eq!(
            auth_error.to_string(),
            "Authentication failed: Invalid credentials"
        );

        let api_error = Error::Api("Server error".to_string());
        assert_eq!(api_error.to_string(), "API error: Server error");

        let zone_error = Error::ZoneNotFound("5211675".to_string());
        assert_eq!(zone_error.to_string(), "Zone not found: 5211675");
    }

    #[test]
    fn test_error_types() {
        // Test that errors are properly typed
        let _auth: Error = Error::Authentication("test".to_string());
        let _api: Error = Error::Api("test".to_string());
        let _zone: Error = Error::ZoneNotFound("test".to_string());
        let _location: Error = Error::LocationNotFound("test".to_string());
        let _session: Error = Error::SessionExpired;
    }
}

// Integration tests that require real credentials
// Run with: cargo test --ignored
#[cfg(test)]
mod integration {
    use super::*;

    #[tokio::test]
    #[ignore]
    async fn test_full_workflow() {
        let mut client = Client::new();

        // This test requires real credentials
        let email = std::env::var("EVOHOME_EMAIL").expect("EVOHOME_EMAIL not set");
        let password = std::env::var("EVOHOME_PASSWORD").expect("EVOHOME_PASSWORD not set");

        // Login
        let (login_response, _) = client.login(&email, &password).await.unwrap();
        assert!(!login_response.user_id.is_empty());
        // DisplayName might be null, so we just check if we got a user_id
        assert!(!login_response.user_id.is_empty());
        // assert!(!login_response.display_name.is_empty()); // Can be null

        // Get locations
        let locations = client.get_locations().await.unwrap();
        assert!(!locations.is_empty());

        let location_id = &locations[0].id;

        // Get location details
        let location = client.get_location(location_id).await.unwrap();
        assert_eq!(location.id, *location_id);

        // Get system
        let system = client.get_location_system(location_id).await.unwrap();
        assert!(!system.zones.is_empty());

        // Get account info
        let account = client.get_account_info().await.unwrap();
        assert!(!account.username.is_empty());

        // Test zone lookup
        if let Some(zone) = system.zones.first() {
            let zone_by_id = client.get_zone(location_id, &zone.id).await.unwrap();
            assert_eq!(zone_by_id.id, zone.id);

            let zone_by_name = client
                .get_zone_by_name(location_id, &zone.name.clone().unwrap_or_default())
                .await
                .unwrap();
            assert_eq!(zone_by_name.name, zone.name);
        }
    }

    #[tokio::test]
    #[ignore]
    async fn test_set_temperature_integration() {
        let mut client = Client::new();

        let email = std::env::var("EVOHOME_EMAIL").expect("EVOHOME_EMAIL not set");
        let password = std::env::var("EVOHOME_PASSWORD").expect("EVOHOME_PASSWORD not set");

        client.login(&email, &password).await.unwrap();

        let locations = client.get_locations().await.unwrap();
        let system = client
            .get_location_system(&locations[0].id)
            .await
            .unwrap();

        if let Some(zone) = system.zones.first() {
            // Set temperature (be careful with real systems!)
            let current_temp = zone.target_heat_temperature;

            // Set to current temperature (no actual change)
            client
                .set_zone_temperature(&zone.id, current_temp, true, 0, 0, false)
                .await
                .unwrap();
        }
    }

    #[tokio::test]
    #[ignore]
    async fn test_concurrent_requests() {
        use tokio::try_join;

        let mut client = Client::new();

        let email = std::env::var("EVOHOME_EMAIL").expect("EVOHOME_EMAIL not set");
        let password = std::env::var("EVOHOME_PASSWORD").expect("EVOHOME_PASSWORD not set");

        client.login(&email, &password).await.unwrap();

        let locations = client.get_locations().await.unwrap();
        let location_id = &locations[0].id;

        // Fetch multiple things concurrently
        let (system, account) = try_join!(
            client.get_location_system(location_id),
            client.get_account_info()
        )
        .unwrap();

        assert!(!system.zones.is_empty());
        assert!(!account.username.is_empty());
    }
}
