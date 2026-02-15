# User Guide

## Introduction

Welcome to the MyTotalConnectComfort Python Client Library! This guide will help you get started with controlling your **International Honeywell Evohome** heating system programmatically.

> **About the System**: The Evohome system is provided by **Resideo**, who licensed the Honeywell brand from Honeywell International. This library is specifically designed for the international version accessible via `international.evohome_py.com`. If you have a North American Honeywell system, it may use different endpoints.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Working with Locations](#working-with-locations)
5. [Working with Zones](#working-with-zones)
6. [Temperature Control](#temperature-control)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Common Use Cases](#common-use-cases)
10. [Troubleshooting](#troubleshooting)

## Installation

### From PyPI

```bash
pip install evohome_py
```

### From Source

```bash
git clone https://github.com/divyavanmahajan/evohome_py.git
cd evohome_py/python
pip install -e .
```

### Verify Installation

```python
python -c "from evohome_py import Client; print('Installation successful!')"
```

## Quick Start

Here's a complete example to get you started:

```python
from evohome_py import Client

# Create and authenticate
client = Client()
client.login("your-email@example.com", "your-password")

# Get your locations
locations = client.get_locations()
print(f"You have {len(locations)} location(s)")

# Get zones for first location
location = locations[0]
system = client.get_location_system(location.id)

# Display current temperatures
for zone in system.zones:
    print(f"{zone.name}: {zone.temperature}°C → {zone.target_temperature}°C")

# Set a temperature
client.set_zone_temperature(
    zone_id=system.zones[0].id,
    temperature=21.0,
    permanent=True
)
```

## Authentication

### Basic Login

```python
from evohome_py import Client
from evohome_py.exceptions import AuthenticationError

client = Client()

try:
    client.login("user@example.com", "password")
    print("[OK] Login successful")
except AuthenticationError as e:
    print(f"[ERROR] Login failed: {e}")
```

### Session Persistence

The client maintains your session automatically using cookies. You don't need to login again for subsequent requests within the same session:

```python
client = Client()
client.login("user@example.com", "password")

# All these work without re-authenticating
locations = client.get_locations()
account = client.get_account_info()
system = client.get_location_system(locations[0].id)
```

### Session Expiry

Sessions expire after 1 hour. If you get a `SessionExpiredError`, simply login again:

```python
from evohome_py.exceptions import SessionExpiredError

try:
    locations = client.get_locations()
except SessionExpiredError:
    client.login("user@example.com", "password")
    locations = client.get_locations()
```

## Working with Locations

### List All Locations

```python
locations = client.get_locations()

for location in locations:
    print(f"Location: {location.name}")
    print(f"  ID: {location.id}")
    print(f"  Address: {location.street_address}")
    print(f"  City: {location.city}, {location.country}")
    print(f"  Zones: {len(location.zones)}")
```

### Get Location Details

```python
location_id = "1232176"
location = client.get_location(location_id)

print(f"Owner: {location.owner_name}")
print(f"Postcode: {location.postcode}")
print(f"Time Zone: {location.time_zone_display_name}")
print(f"Notification Emails: {', '.join(location.notification_emails)}")
```

### Get Location System (with Zones)

```python
system = client.get_location_system(location_id)

print(f"System Device ID: {system.id}")
print(f"Time Offset: {system.time_offset} minutes")
print(f"Number of Zones: {len(system.zones)}")
```

## Working with Zones

### List All Zones

```python
system = client.get_location_system(location_id)

for zone in system.zones:
    status = "[Online]" if zone.is_alive else "[Offline]"
    print(f"{zone.name} {status}")
    print(f"  Current: {zone.temperature}°C")
    print(f"  Target: {zone.target_temperature}°C")
```

### Get Zone by ID

```python
from evohome_py.exceptions import ZoneNotFoundError

try:
    zone = client.get_zone(location_id="1232176", zone_id="5211675")
    print(f"Found zone: {zone.name}")
except ZoneNotFoundError as e:
    print(f"Zone not found: {e}")
```

### Get Zone by Name

```python
zone = client.get_zone_by_name(
    location_id="1232176",
    zone_name="Livingroom"
)
print(f"Zone ID: {zone.id}")
print(f"Temperature: {zone.temperature}°C")
```

### Check Zone Status

```python
zone = client.get_zone(location_id, zone_id)

# Check if zone is online
if not zone.is_alive:
    print(f"[WARNING] {zone.name} is offline!")

# Check for alerts
if zone.has_alerts:
    print(f"[WARNING] {zone.name} has alerts")
    if zone.has_battery_low_alert:
        print("  - Battery low")
    if zone.has_comm_lost_alert:
        print("  - Communication lost")
    if zone.has_sensor_failure_alert:
        print("  - Sensor failure")

# Check override status
if zone.override_active:
    if zone.hold_permanently:
        print(f"  Temperature held permanently at {zone.target_temperature}°C")
    else:
        print(f"  Temporary override active")
```

## Temperature Control

### Set Temperature (Permanent)

```python
# Set temperature permanently (until manually changed)
client.set_zone_temperature(
    zone_id="5211675",
    temperature=21.5,
    permanent=True
)
```

### Set Temperature (Temporary)

```python
# Set temperature for 2 hours, then return to schedule
client.set_zone_temperature(
    zone_id="5211675",
    temperature=22.0,
    permanent=False,
    duration_hours=2,
    duration_minutes=0
)
```

### Set Temperature for 30 Minutes

```python
client.set_zone_temperature(
    zone_id="5211675",
    temperature=23.0,
    permanent=False,
    duration_hours=0,
    duration_minutes=30
)
```

### Validate Temperature Range

```python
zone = client.get_zone(location_id, zone_id)

desired_temp = 25.0

if desired_temp < zone.min_temperature:
    print(f"Temperature too low! Minimum is {zone.min_temperature}°C")
elif desired_temp > zone.max_temperature:
    print(f"Temperature too high! Maximum is {zone.max_temperature}°C")
else:
    client.set_zone_temperature(zone_id=zone.id, temperature=desired_temp)
```

## Error Handling

### Comprehensive Error Handling

```python
from evohome_py import Client
from evohome_py.exceptions import (
    AuthenticationError,
    APIError,
    ZoneNotFoundError,
    LocationNotFoundError,
    SessionExpiredError,
)

client = Client()

try:
    # Login
    client.login("user@example.com", "password")
    
    # Get locations
    locations = client.get_locations()
    
    # Set temperature
    client.set_zone_temperature(
        zone_id="5211675",
        temperature=21.0
    )
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Please check your email and password")
    
except ZoneNotFoundError as e:
    print(f"Zone not found: {e}")
    print("Please check the zone ID")
    
except LocationNotFoundError as e:
    print(f"Location not found: {e}")
    print("Please check the location ID")
    
except SessionExpiredError as e:
    print(f"Session expired: {e}")
    print("Please login again")
    
except APIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Reuse Client Instance

```python
# Good: Reuse client
client = Client()
client.login(email, password)
locations = client.get_locations()
account = client.get_account_info()

# Avoid: Creating multiple clients
client1 = Client()
client1.login(email, password)
client2 = Client()  # Unnecessary
client2.login(email, password)
```

### 2. Cache Location and Zone Data

```python
# Cache location data to avoid repeated API calls
locations = client.get_locations()
location_id = locations[0].id

# Cache system data
system = client.get_location_system(location_id)
zones = {zone.name: zone for zone in system.zones}

# Use cached data
livingroom = zones["Livingroom"]
print(f"Current temp: {livingroom.temperature}°C")
```

### 3. Use Context Managers for Cleanup

```python
class ManagedClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.client = None
    
    def __enter__(self):
        self.client = Client()
        self.client.login(self.email, self.password)
        return self.client
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup if needed
        pass

# Usage
with ManagedClient("user@example.com", "password") as client:
    locations = client.get_locations()
    # Client automatically cleaned up
```

### 4. Validate Before Setting Temperature

```python
def safe_set_temperature(client, zone, temperature):
    """Safely set temperature with validation."""
    if not zone.is_alive:
        raise ValueError(f"Zone {zone.name} is offline")
    
    if temperature < zone.min_temperature or temperature > zone.max_temperature:
        raise ValueError(
            f"Temperature {temperature}°C out of range "
            f"({zone.min_temperature}°C - {zone.max_temperature}°C)"
        )
    
    client.set_zone_temperature(zone_id=zone.id, temperature=temperature)
```

## Common Use Cases

### 1. Morning Boost

```python
def morning_boost(client, location_id, target_temp=22.0, duration_hours=2):
    """Boost all zones in the morning."""
    system = client.get_location_system(location_id)
    
    for zone in system.zones:
        if zone.is_alive:
            client.set_zone_temperature(
                zone_id=zone.id,
                temperature=target_temp,
                permanent=False,
                duration_hours=duration_hours
            )
            print(f"[OK] Boosted {zone.name} to {target_temp}°C for {duration_hours}h")
```

### 2. Energy Saving Mode

```python
def energy_saving_mode(client, location_id, eco_temp=18.0):
    """Set all zones to energy-saving temperature."""
    system = client.get_location_system(location_id)
    
    for zone in system.zones:
        if zone.is_alive and zone.temperature > eco_temp:
            client.set_zone_temperature(
                zone_id=zone.id,
                temperature=eco_temp,
                permanent=True
            )
            print(f"[OK] Set {zone.name} to eco mode ({eco_temp}°C)")
```

### 3. Temperature Monitoring

```python
def monitor_temperatures(client, location_id):
    """Monitor and report zone temperatures."""
    system = client.get_location_system(location_id)
    
    report = []
    for zone in system.zones:
        diff = zone.target_temperature - zone.temperature
        status = "heating" if diff > 0.5 else "stable"
        
        report.append({
            "name": zone.name,
            "current": zone.temperature,
            "target": zone.target_temperature,
            "status": status,
            "online": zone.is_alive
        })
    
    return report
```

### 4. Vacation Mode

```python
def vacation_mode(client, location_id, frost_protect_temp=12.0):
    """Set all zones to frost protection temperature."""
    system = client.get_location_system(location_id)
    
    for zone in system.zones:
        if zone.is_alive:
            client.set_zone_temperature(
                zone_id=zone.id,
                temperature=frost_protect_temp,
                permanent=True
            )
    
    print(f"[OK] Vacation mode activated ({frost_protect_temp}°C)")
```

## Troubleshooting

### Problem: Login Fails

**Solution:**
- Verify email and password are correct
- Check if you can login via the web interface
- Ensure you're using the correct regional server (international)

### Problem: Session Expired

**Solution:**
```python
# Implement auto-retry
def api_call_with_retry(client, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except SessionExpiredError:
        client.login(email, password)
        return func(*args, **kwargs)
```

### Problem: Zone Not Found

**Solution:**
```python
# List all zones to find correct ID
system = client.get_location_system(location_id)
for zone in system.zones:
    print(f"{zone.name}: {zone.id}")
```

### Problem: Temperature Not Changing

**Possible causes:**
1. Zone is offline (`zone.is_alive == False`)
2. Temperature out of range
3. System in away mode
4. Hardware issue

**Debug:**
```python
zone = client.get_zone(location_id, zone_id)
print(f"Online: {zone.is_alive}")
print(f"Range: {zone.min_temperature}°C - {zone.max_temperature}°C")
print(f"Override active: {zone.override_active}")
```

## Advanced Topics

### Custom Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = Client()
logger.info("Logging in...")
client.login(email, password)
logger.info("Login successful")
```

### Concurrent Operations

```python
from concurrent.futures import ThreadPoolExecutor

def set_zone_temp(client, zone_id, temp):
    client.set_zone_temperature(zone_id=zone_id, temperature=temp)
    return zone_id

# Set multiple zones concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    for zone in system.zones:
        future = executor.submit(set_zone_temp, client, zone.id, 21.0)
        futures.append(future)
    
    for future in futures:
        zone_id = future.result()
        print(f"[OK] Updated zone {zone_id}")
```

## Getting Help

- [API Documentation](../../api/API_DOCUMENTATION.md)
- [Architecture](ARCHITECTURE.md)
- [Development Guidelines](DEVELOPMENT.md)
- [Issue Tracker](https://github.com/divyavanmahajan/evohome_py/issues)
