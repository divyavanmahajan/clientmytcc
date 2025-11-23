"""Test configuration and shared fixtures."""

import pytest
from mytotalconnectcomfort import Client


@pytest.fixture
def client():
    """Create a client instance for testing."""
    return Client()


@pytest.fixture
def mock_login_response():
    """Mock successful login response."""
    return {
        "Content": {
            "UserId": "3194795",
            "DisplayName": "Test User",
            "UserName": "test@example.com",
            "Reauthenticated": False,
        },
        "Errors": None,
        "RedirectUrl": "https://international.mytotalconnectcomfort.com/Locations",
    }


@pytest.fixture
def mock_locations_response():
    """Mock locations API response."""
    return {
        "Content": {
            "Locations": [
                {
                    "Id": "1232176",
                    "Name": "Home",
                    "City": "Test City",
                    "Country": "Test Country",
                    "Postcode": "12345",
                    "StreetAddress": "123 Test St",
                    "HeatingSystemType": 1,
                    "Zones": [
                        {
                            "Id": "5211675",
                            "DeviceId": 5211675,
                            "Name": "Livingroom",
                            "MacId": "B82CA06CB358",
                            "ThermostatModelType": "Evo",
                            "IsAlive": True,
                            "HasAlerts": False,
                            "Temperature": 19.5,
                            "MinHeatSetpoint": 5.0,
                            "MaxHeatSetpoint": 35.0,
                            "TargetHeatTemperature": 21.0,
                            "OverrideActive": True,
                            "HoldTemperaturePermanently": True,
                            "SetPointStatus": 2,
                            "ThermostatUnits": "Celsius",
                            "ThermostatVersion": "EvoTouch",
                        }
                    ],
                }
            ]
        },
        "Errors": None,
    }


@pytest.fixture
def mock_zone_data():
    """Mock zone data."""
    return {
        "Id": "5211675",
        "DeviceId": 5211675,
        "Name": "Livingroom",
        "MacId": "B82CA06CB358",
        "ThermostatModelType": "Evo",
        "IsAlive": True,
        "HasAlerts": False,
        "HasCommLostAlert": False,
        "HasBatteryLowAlert": False,
        "HasSensorFailureAlert": False,
        "Temperature": 19.5,
        "MinHeatSetpoint": 5.0,
        "MaxHeatSetpoint": 35.0,
        "TargetHeatTemperature": 21.0,
        "OverrideActive": True,
        "HoldTemperaturePermanently": True,
        "SetPointStatus": 2,
        "ThermostatUnits": "Celsius",
        "ThermostatVersion": "EvoTouch",
    }


@pytest.fixture
def mock_location_data():
    """Mock location data."""
    return {
        "Id": "1232176",
        "Name": "Home",
        "City": "Test City",
        "Country": "Test Country",
        "Postcode": "12345",
        "StreetAddress": "123 Test St",
        "HeatingSystemType": 1,
        "Zones": [],
    }
