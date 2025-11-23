"""Tests for the CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from clientmytcc.cli import cli
from clientmytcc.models import Zone, Location, LocationSystem

@pytest.fixture
def mock_client():
    with patch('clientmytcc.cli._get_authenticated_client') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def mock_system():
    zone1 = Zone(
        id="12345",
        name="Living Room",
        temperature=20.0,
        target_heat_temperature=22.0,
        is_alive=True,
        has_alerts=False,
        has_battery_low_alert=False,
        has_comm_lost_alert=False,
        has_sensor_failure_alert=False,
        min_heat_setpoint=5.0,
        max_heat_setpoint=35.0,
        override_active=False,
        hold_temperature_permanently=False
    )
    zone2 = Zone(
        id="67890",
        name="Bedroom",
        temperature=19.0,
        target_heat_temperature=19.0,
        is_alive=False,
        has_alerts=False,
        has_battery_low_alert=False,
        has_comm_lost_alert=False,
        has_sensor_failure_alert=False,
        min_heat_setpoint=5.0,
        max_heat_setpoint=35.0,
        override_active=False,
        hold_temperature_permanently=False
    )
    
    system = LocationSystem(
        id="loc1",
        name="Home",
        zones=[zone1, zone2]
    )
    return system

def test_status_command(mock_client, mock_system):
    """Test the status command output format."""
    mock_client.get_locations.return_value = [Location(id="loc1", name="Home", street_address=None, city=None, country=None, postcode=None, time_zone_display_name=None, notification_emails=[], zones=[], gateways=[], owner_name=None)]
    mock_client.get_location_system.return_value = mock_system
    
    runner = CliRunner()
    result = runner.invoke(cli, ['status', 'loc1'])
    
    assert result.exit_code == 0
    # Check for column headers
    assert "Zone" in result.output
    assert "Current" in result.output
    assert "Target" in result.output
    assert "Diff" in result.output
    assert "Status" in result.output
    assert "ID" in result.output
    
    # Check for zone 1 (Heating, Online)
    assert "Living Room" in result.output
    assert "20.0°C" in result.output
    assert "22.0°C" in result.output
    assert "+2.0°C" in result.output
    assert "Heating" in result.output
    assert "12345" in result.output
    
    # Check for zone 2 (Stable, Offline)
    assert "Bedroom" in result.output
    assert "19.0°C" in result.output
    assert "+0.0°C" in result.output
    assert "Stable" in result.output
    assert "Offline" in result.output
    assert "67890" in result.output

def test_zones_alias(mock_client, mock_system):
    """Test that zones command is an alias for status."""
    mock_client.get_locations.return_value = [Location(id="loc1", name="Home", street_address=None, city=None, country=None, postcode=None, time_zone_display_name=None, notification_emails=[], zones=[], gateways=[], owner_name=None)]
    mock_client.get_location_system.return_value = mock_system
    
    runner = CliRunner()
    result = runner.invoke(cli, ['zones', 'loc1'])
    
    assert result.exit_code == 0
    # Should produce same output as status
    assert "Living Room" in result.output
    assert "Heating" in result.output
    assert "12345" in result.output
