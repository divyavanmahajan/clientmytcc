"""Tests for the Client class."""

import pytest
import requests_mock
from clientmytcc import Client
from clientmytcc.exceptions import (
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
)


class TestClientInitialization:
    """Test client initialization."""

    def test_client_creation(self):
        """Test creating a client instance."""
        client = Client()
        assert client is not None
        assert client.session is not None
        assert client._authenticated is False

    def test_client_base_url(self):
        """Test client has correct base URL."""
        client = Client()
        assert client.BASE_URL == "https://international.mytotalconnectcomfort.com"


class TestAuthentication:
    """Test authentication functionality."""

    def test_login_success(self, client, mock_login_response):
        """Test successful login."""
        with requests_mock.Mocker() as m:
            # Mock login page
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )

            # Mock login API
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            result = client.login("test@example.com", "password")

            assert result["UserId"] == "3194795"
            assert result["DisplayName"] == "Test User"
            assert client._authenticated is True

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with requests_mock.Mocker() as m:
            # Mock login page
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )

            # Mock failed login
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                status_code=401,
            )

            with pytest.raises(AuthenticationError, match="Invalid email or password"):
                client.login("test@example.com", "wrong_password")

    def test_login_api_error(self, client):
        """Test login with API error response."""
        with requests_mock.Mocker() as m:
            # Mock login page
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )

            # Mock API error
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json={
                    "Content": None,
                    "Errors": [{"Message": "Service unavailable"}],
                },
            )

            with pytest.raises(AuthenticationError, match="Service unavailable"):
                client.login("test@example.com", "password")


class TestLocations:
    """Test location-related functionality."""

    def test_get_locations(self, client, mock_login_response, mock_locations_response):
        """Test getting locations."""
        with requests_mock.Mocker() as m:
            # Mock login
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            # Mock get locations
            m.get(
                "https://international.mytotalconnectcomfort.com/api/locationsapi/getlocations",
                json=mock_locations_response,
            )

            client.login("test@example.com", "password")
            locations = client.get_locations()

            assert len(locations) == 1
            assert locations[0].id == "1232176"
            assert locations[0].name == "Home"
            assert len(locations[0].zones) == 1

    def test_get_locations_not_authenticated(self, client):
        """Test getting locations without authentication."""
        with pytest.raises(AuthenticationError, match="Not authenticated"):
            client.get_locations()


class TestZones:
    """Test zone-related functionality."""

    def test_get_zone_by_id(self, client, mock_login_response):
        """Test getting a zone by ID."""
        with requests_mock.Mocker() as m:
            # Mock login
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            # Mock get location system
            m.get(
                "https://international.mytotalconnectcomfort.com/Api/LocationsApi/GetLocationSystem",
                json={
                    "Content": {
                        "LocationModel": {
                            "Id": "1232176",
                            "Zones": [
                                {
                                    "Id": "5211675",
                                    "Name": "Livingroom",
                                    "Temperature": 19.5,
                                    "TargetHeatTemperature": 21.0,
                                    "MinHeatSetpoint": 5.0,
                                    "MaxHeatSetpoint": 35.0,
                                    "IsAlive": True,
                                }
                            ],
                        }
                    }
                },
            )

            client.login("test@example.com", "password")
            zone = client.get_zone("1232176", "5211675")

            assert zone.id == "5211675"
            assert zone.name == "Livingroom"
            assert zone.temperature == 19.5

    def test_get_zone_not_found(self, client, mock_login_response):
        """Test getting a non-existent zone."""
        with requests_mock.Mocker() as m:
            # Mock login
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            # Mock get location system with no zones
            m.get(
                "https://international.mytotalconnectcomfort.com/Api/LocationsApi/GetLocationSystem",
                json={"Content": {"LocationModel": {"Id": "1232176", "Zones": []}}},
            )

            client.login("test@example.com", "password")

            with pytest.raises(ZoneNotFoundError):
                client.get_zone("1232176", "invalid_zone_id")


class TestTemperatureControl:
    """Test temperature control functionality."""

    def test_set_zone_temperature(self, client, mock_login_response):
        """Test setting zone temperature."""
        with requests_mock.Mocker() as m:
            # Mock login
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            # Mock set temperature
            m.post(
                "https://international.mytotalconnectcomfort.com/api/ZonesApi/SetZoneTemperature",
                json={"Errors": None},
            )

            client.login("test@example.com", "password")
            # Should not raise an exception
            client.set_zone_temperature(
                zone_id="5211675", temperature=21.5, permanent=True
            )

            # Verify the request was made
            assert m.call_count == 3  # Login page + login API + set temperature


class TestErrorHandling:
    """Test error handling."""

    def test_api_error_with_status_code(self, client, mock_login_response):
        """Test API error with status code."""
        with requests_mock.Mocker() as m:
            # Mock login
            m.get(
                "https://international.mytotalconnectcomfort.com/Account/Login",
                text="<html></html>",
            )
            m.post(
                "https://international.mytotalconnectcomfort.com/api/accountApi/login",
                json=mock_login_response,
            )

            # Mock API error
            m.get(
                "https://international.mytotalconnectcomfort.com/api/locationsapi/getlocations",
                json={"Content": None, "Errors": [{"Message": "Server error"}]},
            )

            client.login("test@example.com", "password")

            with pytest.raises(APIError, match="Server error"):
                client.get_locations()
