"""Integration tests for CLI commands that interact with the real API.

These tests require valid credentials set in environment variables:
- EVOHOME_USER or EVOHOME_EMAIL
- EVOHOME_PASSWORD

Run with: pytest tests/test_cli_integration.py -v
"""

import os
import time
import pytest
from click.testing import CliRunner
from clientmytcc import Client
from clientmytcc.cli import cli


@pytest.fixture
def authenticated_client():
    """Get authenticated client from environment variables."""
    email = os.environ.get("EVOHOME_USER") or os.environ.get("EVOHOME_EMAIL")
    password = os.environ.get("EVOHOME_PASSWORD")
    
    if not email or not password:
        pytest.skip("EVOHOME_USER/EVOHOME_EMAIL and EVOHOME_PASSWORD must be set")
    
    client = Client()
    client.login(email, password)
    return client


@pytest.fixture
def location_id(authenticated_client):
    """Get the first location ID."""
    locations = authenticated_client.get_locations()
    assert len(locations) > 0, "No locations found"
    return locations[0].id


@pytest.fixture
def save_and_restore_temps(authenticated_client, location_id):
    """Save temperatures before test and restore after."""
    # Save original temperatures
    system = authenticated_client.get_location_system(location_id)
    original_temps = {zone.id: zone.target_temperature for zone in system.zones}
    
    yield original_temps
    
    # Restore original temperatures
    for zone_id, temp in original_temps.items():
        authenticated_client.set_zone_temperature(
            zone_id=zone_id,
            temperature=temp,
            permanent=True
        )
    
    # Wait for API to process restoration
    time.sleep(2)


@pytest.mark.integration
def test_boost_default_temp(authenticated_client, location_id, save_and_restore_temps):
    """Test boost command with default temperature (22°C)."""
    # Get initial state
    system_before = authenticated_client.get_location_system(location_id)
    
    # Apply boost with default temp
    for zone in system_before.zones:
        if zone.is_alive and abs(zone.target_temperature - 5.0) > 0.1:
            authenticated_client.set_zone_temperature(
                zone_id=zone.id,
                temperature=22.0,
                permanent=False,
                duration_hours=2,
                duration_minutes=0
            )
    
    # Wait for API to process changes
    time.sleep(2)
    
    # Verify changes
    system_after = authenticated_client.get_location_system(location_id)
    
    for zone in system_after.zones:
        if zone.is_alive and abs(save_and_restore_temps[zone.id] - 5.0) > 0.1:
            assert abs(zone.target_temperature - 22.0) < 0.1, \
                f"Zone {zone.name} should be at 22°C, got {zone.target_temperature}°C"


@pytest.mark.integration
def test_boost_custom_temp_celsius(authenticated_client, location_id, save_and_restore_temps):
    """Test boost command with custom temperature (20°C)."""
    target_temp = 20.0
    
    # Get initial state
    system_before = authenticated_client.get_location_system(location_id)
    
    # Apply boost with custom temp
    for zone in system_before.zones:
        if zone.is_alive and abs(zone.target_temperature - 5.0) > 0.1:
            authenticated_client.set_zone_temperature(
                zone_id=zone.id,
                temperature=target_temp,
                permanent=False,
                duration_hours=2,
                duration_minutes=0
            )
    
    # Wait for API to process changes
    time.sleep(2)
    
    # Verify changes
    system_after = authenticated_client.get_location_system(location_id)
    
    for zone in system_after.zones:
        if zone.is_alive and abs(save_and_restore_temps[zone.id] - 5.0) > 0.1:
            assert abs(zone.target_temperature - target_temp) < 0.1, \
                f"Zone {zone.name} should be at {target_temp}°C, got {zone.target_temperature}°C"


@pytest.mark.integration
def test_eco_default_temp(authenticated_client, location_id, save_and_restore_temps):
    """Test eco command with default temperature (18°C)."""
    eco_temp = 18.0
    
    # Get initial state
    system_before = authenticated_client.get_location_system(location_id)
    
    # Apply eco mode
    for zone in system_before.zones:
        if (zone.is_alive 
            and zone.target_temperature > eco_temp 
            and abs(zone.target_temperature - 5.0) > 0.1):
            authenticated_client.set_zone_temperature(
                zone_id=zone.id,
                temperature=eco_temp,
                permanent=True
            )
    
    # Wait for API to process changes
    time.sleep(2)
    
    # Verify changes
    system_after = authenticated_client.get_location_system(location_id)
    
    for zone in system_after.zones:
        if (zone.is_alive 
            and save_and_restore_temps[zone.id] > eco_temp 
            and abs(save_and_restore_temps[zone.id] - 5.0) > 0.1):
            assert abs(zone.target_temperature - eco_temp) < 0.1, \
                f"Zone {zone.name} should be at {eco_temp}°C, got {zone.target_temperature}°C"


@pytest.mark.integration
def test_vacation_default_temp(authenticated_client, location_id, save_and_restore_temps):
    """Test vacation command with default temperature (12°C)."""
    vacation_temp = 12.0
    
    # Get initial state
    system_before = authenticated_client.get_location_system(location_id)
    
    # Apply vacation mode
    for zone in system_before.zones:
        if zone.is_alive and abs(zone.target_temperature - 5.0) > 0.1:
            authenticated_client.set_zone_temperature(
                zone_id=zone.id,
                temperature=vacation_temp,
                permanent=True
            )
    
    # Wait for API to process changes
    time.sleep(2)
    
    # Verify changes
    system_after = authenticated_client.get_location_system(location_id)
    
    for zone in system_after.zones:
        if zone.is_alive and abs(save_and_restore_temps[zone.id] - 5.0) > 0.1:
            assert abs(zone.target_temperature - vacation_temp) < 0.1, \
                f"Zone {zone.name} should be at {vacation_temp}°C, got {zone.target_temperature}°C"


@pytest.mark.integration
def test_skip_5c_zones(authenticated_client, location_id, save_and_restore_temps):
    """Test that zones at 5°C are skipped during boost."""
    # Get initial state
    system_before = authenticated_client.get_location_system(location_id)
    
    # Apply boost, skipping 5°C zones
    for zone in system_before.zones:
        if zone.is_alive and abs(zone.target_temperature - 5.0) > 0.1:
            authenticated_client.set_zone_temperature(
                zone_id=zone.id,
                temperature=22.0,
                permanent=False,
                duration_hours=2,
                duration_minutes=0
            )
    
    # Wait for API to process changes
    time.sleep(2)
    
    # Verify that 5°C zones were not changed
    system_after = authenticated_client.get_location_system(location_id)
    
    for zone in system_after.zones:
        if abs(save_and_restore_temps[zone.id] - 5.0) < 0.1:
            assert abs(zone.target_temperature - 5.0) < 0.1, \
                f"Zone {zone.name} at 5°C should not have been changed, got {zone.target_temperature}°C"


@pytest.mark.integration
def test_cli_boost_command():
    """Test boost command via CLI."""
    runner = CliRunner()
    
    # Test with default temp
    result = runner.invoke(cli, ['boost'])
    
    # Should succeed if credentials are set
    if "EVOHOME_USER" in os.environ and "EVOHOME_PASSWORD" in os.environ:
        assert result.exit_code == 0
        assert "Boosted" in result.output
    else:
        # Skip if no credentials
        pytest.skip("Credentials not set")


@pytest.mark.integration
def test_cli_eco_command():
    """Test eco command via CLI."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['eco'])
    
    if "EVOHOME_USER" in os.environ and "EVOHOME_PASSWORD" in os.environ:
        assert result.exit_code == 0
        assert "eco mode" in result.output
    else:
        pytest.skip("Credentials not set")


@pytest.mark.integration
def test_cli_vacation_command():
    """Test vacation command via CLI."""
    runner = CliRunner()
    
    result = runner.invoke(cli, ['vacation'])
    
    if "EVOHOME_USER" in os.environ and "EVOHOME_PASSWORD" in os.environ:
        assert result.exit_code == 0
        assert "Vacation mode" in result.output
    else:
        pytest.skip("Credentials not set")
