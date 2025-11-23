"""Tests for data models."""

import pytest
from clientmytcc.models import Zone, Location, UserInfo, Gateway


class TestZone:
    """Test Zone model."""

    def test_zone_from_dict(self, mock_zone_data):
        """Test creating Zone from dictionary."""
        zone = Zone.from_dict(mock_zone_data)

        assert zone.id == "5211675"
        assert zone.name == "Livingroom"
        assert zone.temperature == 19.5
        assert zone.target_temperature == 21.0
        assert zone.min_temperature == 5.0
        assert zone.max_temperature == 35.0
        assert zone.is_alive is True
        assert zone.has_alerts is False
        assert zone.override_active is True
        assert zone.thermostat_units == "Celsius"

    def test_zone_defaults(self):
        """Test Zone with minimal data."""
        zone = Zone.from_dict({"Id": "123", "Name": "Test"})

        assert zone.id == "123"
        assert zone.name == "Test"
        assert zone.temperature == 0.0
        assert zone.target_temperature == 0.0
        assert zone.is_alive is False

    def test_zone_optional_fields(self, mock_zone_data):
        """Test Zone with optional fields."""
        zone = Zone.from_dict(mock_zone_data)

        assert zone.device_id == 5211675
        assert zone.mac_id == "B82CA06CB358"
        assert zone.thermostat_model == "Evo"
        assert zone.thermostat_version == "EvoTouch"


class TestLocation:
    """Test Location model."""

    def test_location_from_dict(self, mock_location_data):
        """Test creating Location from dictionary."""
        location = Location.from_dict(mock_location_data)

        assert location.id == "1232176"
        assert location.name == "Home"
        assert location.city == "Test City"
        assert location.country == "Test Country"
        assert location.postcode == "12345"
        assert location.street_address == "123 Test St"
        assert location.heating_system_type == 1

    def test_location_with_zones(self, mock_location_data, mock_zone_data):
        """Test Location with zones."""
        mock_location_data["Zones"] = [mock_zone_data]
        location = Location.from_dict(mock_location_data)

        assert len(location.zones) == 1
        assert location.zones[0].name == "Livingroom"

    def test_location_get_zone_by_id(self, mock_location_data, mock_zone_data):
        """Test getting zone by ID."""
        mock_location_data["Zones"] = [mock_zone_data]
        location = Location.from_dict(mock_location_data)

        zone = location.get_zone_by_id("5211675")
        assert zone is not None
        assert zone.name == "Livingroom"

        # Test non-existent zone
        zone = location.get_zone_by_id("invalid")
        assert zone is None

    def test_location_get_zone_by_name(self, mock_location_data, mock_zone_data):
        """Test getting zone by name."""
        mock_location_data["Zones"] = [mock_zone_data]
        location = Location.from_dict(mock_location_data)

        zone = location.get_zone_by_name("Livingroom")
        assert zone is not None
        assert zone.id == "5211675"

        # Test case-insensitive
        zone = location.get_zone_by_name("livingroom")
        assert zone is not None

        # Test non-existent zone
        zone = location.get_zone_by_name("Invalid")
        assert zone is None

    def test_location_defaults(self):
        """Test Location with minimal data."""
        location = Location.from_dict({"Id": "123", "Name": "Test"})

        assert location.id == "123"
        assert location.name == "Test"
        assert location.zones == []
        assert location.gateways == []
        assert location.notification_emails == []


class TestGateway:
    """Test Gateway model."""

    def test_gateway_from_dict(self):
        """Test creating Gateway from dictionary."""
        data = {"Id": "3795953", "MacId": "B82CA06CB358", "Crc": "9C26"}
        gateway = Gateway.from_dict(data)

        assert gateway.id == "3795953"
        assert gateway.mac_id == "B82CA06CB358"
        assert gateway.crc == "9C26"


class TestUserInfo:
    """Test UserInfo model."""

    def test_userinfo_from_dict(self):
        """Test creating UserInfo from dictionary."""
        data = {
            "Username": "test@example.com",
            "FirstName": "Test",
            "LastName": "User",
            "StreetAddress": "123 Test St",
            "City": "Test City",
            "Postcode": "12345",
            "CountryId": 1,
            "CountryName": "Test Country",
            "UserLanguage": 2,
        }
        user = UserInfo.from_dict(data)

        assert user.username == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.street_address == "123 Test St"
        assert user.city == "Test City"
        assert user.postcode == "12345"
        assert user.country_id == 1
        assert user.country_name == "Test Country"
        assert user.user_language == 2

    def test_userinfo_minimal(self):
        """Test UserInfo with minimal data."""
        data = {"Username": "test@example.com", "FirstName": "Test", "LastName": "User"}
        user = UserInfo.from_dict(data)

        assert user.username == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.street_address is None
        assert user.city is None
