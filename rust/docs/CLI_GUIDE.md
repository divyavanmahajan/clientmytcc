# CLI User Guide

## Overview

The `evohome` command-line tool provides easy access to the MyTotalConnectComfort API for controlling your International Honeywell Evohome heating system. Available in both Python and Rust implementations with identical command structure.

## Installation

### Python

```bash
pip install clientmytcc
```

### Rust

```bash
cargo install clientmytcc
```

## Quick Start

### Quick Start

```bash
evohome login user@example.com
# Enter password when prompted
```

### List Locations

```bash
evohome locations
```

### View Zone Status

```bash
# Auto-selects location if you have only one
evohome zones

# Or specify location ID
evohome zones 1232176
```

### Set Temperature

```bash
# By zone name (case-insensitive prefix matching)
evohome set living 21C
evohome set bed 70F

# By zone ID
evohome set 5211675 21C

# With duration
evohome set living 22C --duration 2h
evohome set bedroom 72F --duration 30m

# Interactive mode (prompts for location, zone, and temperature)
evohome set
```

## Commands

### Authentication

#### `evohome login <email>`
Authenticate with your MyTotalConnectComfort account.

```bash
evohome login user@example.com
```

#### `evohome logout`
Clear stored credentials.

```bash
evohome logout
```

### Information

#### `evohome locations`
List all locations (homes) associated with your account.

```bash
evohome locations
```

Output:
```
┌──────────┬──────┬────────┬───────┐
│ ID       │ Name │ City   │ Zones │
├──────────┼──────┼────────┼───────┤
│ 1232176  │ Home │ London │ 5     │
└──────────┴──────┴────────┴───────┘
```

#### `evohome zones <location-id>`
List all zones in a location.

```bash
evohome zones 1232176
```

#### `evohome status <location-id> [--format table|json]`
Show current status of all zones.

```bash
# Table format (default)
evohome status 1232176

# JSON format
evohome status 1232176 --format json
```

#### `evohome account`
Show account information.

```bash
evohome account
```

### Temperature Control

#### `evohome set <zone> <temperature> [OPTIONS]`
Set zone temperature.

**Zone Parameter**:
- Zone ID (numeric): `5211675`
- Zone name: `Livingroom`, `Bedroom`
- Zone name prefix (case-insensitive): `liv`, `bed`, `bath`
- If multiple matches, prompts to select
- If omitted, prompts to select location and zone

**Temperature Parameter**:
- Celsius: `21`, `21C`, `21.5C`
- Fahrenheit: `70F`, `72F`
- If omitted, prompts for input

**Options:**
- `--duration <duration>` - Temporary duration (e.g., `2h`, `30m`, `1.5h`)
- `--location <id>` - Location ID (for zone selection)

**Examples:**

```bash
# By zone name with Celsius
evohome set living 21C
evohome set bedroom 70F

# By zone prefix
evohome set liv 21.5C
evohome set bed 22C

# By zone ID
evohome set 5211675 21C

# With duration
evohome set living 22C --duration 2h
evohome set bedroom 72F --duration 30m
evohome set bathroom 23C --duration 1.5h

# Interactive mode
evohome set
# → Prompts for location (if multiple)
# → Prompts for zone
# → Prompts for temperature
# → [INFO] Command to skip selection: evohome set 5211675 21C
```

## Common Use Cases

### Morning Boost

Boost all zones to a comfortable temperature for a few hours.

```bash
# Auto-selects location if you have only one
evohome boost --temp 22C --duration 2h

# Specify location
evohome boost 1232176 --temp 72F --duration 3h

# With minutes
evohome boost --temp 23C --duration 120m
```

**Options:**
- `--temp <temperature>` - Target temperature (default: 22C)
  - Celsius: `22C`, `21.5C`
  - Fahrenheit: `72F`, `70F`
- `--duration <duration>` - Duration (default: 2h)
  - Hours: `2h`, `3h`, `1.5h`
  - Minutes: `120m`, `90m`

**Example:**
```bash
# Boost to 23°C for 3 hours
evohome boost --temp 23C --duration 3h
```

### Energy Saving Mode

Set all zones to an energy-saving temperature.

```bash
# Auto-selects location
evohome eco --temp 18C

# With Fahrenheit
evohome eco --temp 64F

# Specify location
evohome eco 1232176 --temp 17C
```

**Options:**
- `--temp <temperature>` - Eco temperature (default: 18C)

**Example:**
```bash
# Set to 17°C
evohome eco 1232176 --temp 17.0
```

### Temperature Monitoring

View current status of all zones with heating status.

```bash
# Table format (auto-selects location)
evohome monitor

# JSON format for scripting
evohome monitor --format json

# Specify location
evohome monitor 1232176 --format table
```

**Table Output:**
```
Temperature Monitor: Home
Livingroom: 19.5°C → 21.0°C (Heating) ✓
Bedroom: 20.0°C → 20.0°C (Stable) ✓
Kitchen: 18.5°C → 19.0°C (Heating) ✓
```

**JSON Output:**
```json
[
  {
    "name": "Livingroom",
    "current": 19.5,
    "target": 21.0,
    "status": "heating",
    "online": true
  }
]
```

### Vacation Mode

Set all zones to frost protection temperature.

```bash
# Auto-selects location
evohome vacation --temp 12C

# With Fahrenheit
evohome vacation --temp 54F

# Specify location
evohome vacation 1232176 --temp 10C
```

**Options:**
- `--temp <temperature>` - Frost protection temperature (default: 12C)

### Resume Schedule

Reset all zones to follow their programmed schedule (removes any manual overrides).

```bash
# Auto-selects location
evohome schedule

# Specify location
evohome schedule 1232176
```

This command cancels any temporary or permanent temperature overrides and returns all zones to their normal scheduled operation.

## Smart Features

### Interactive Location Selection

If location is not specified:
- **Single location**: Auto-selects with confirmation message
- **Multiple locations**: Prompts you to select from list
- **Default location**: Uses `default_location` from config if set

```bash
# Set default location
evohome config set default_location 1232176

# Now all commands auto-use this location
evohome boost
evohome monitor
evohome zones
```

### Zone Name Matching

Zones can be specified by:
- **Zone ID** (numeric): `5211675`
- **Exact name**: `Livingroom`, `Bedroom`
- **Name prefix** (case-insensitive): `liv`, `bed`, `bath`

```bash
# All of these work:
evohome set 5211675 21C          # By ID
evohome set Livingroom 21C       # By exact name
evohome set livingroom 21C       # Case-insensitive
evohome set liv 21C              # By prefix
evohome set LIVING 21C           # Case-insensitive prefix
```

If multiple zones match the prefix, you'll be prompted to select:
```bash
evohome set b 21C
# → Multiple zones match 'b':
#    1.   5211675: ( 18.0°C -->  20.0°C) Bedroom             
#    2.   5211676: ( 19.0°C -->  21.0°C) Bathroom            
#   Enter number: 1
```

### Temperature Units

Supports both Celsius and Fahrenheit:
- **Celsius**: `21C`, `21.5C`, `21` (defaults to C)
- **Fahrenheit**: `70F`, `72F`

Automatic conversion to Celsius for API:
```bash
evohome set living 70F    # → 21.1°C
evohome boost --temp 72F  # → 22.2°C
```

### Duration Units

Supports hours and minutes:
- **Hours**: `2h`, `3h`, `1.5h` (decimals supported)
- **Minutes**: `30m`, `90m`, `120m`

```bash
evohome set living 21C --duration 2h      # 2 hours
evohome set bedroom 22C --duration 30m    # 30 minutes
evohome boost --duration 1.5h             # 1 hour 30 minutes
```

Configuration is stored in `~/.config/evohome/config.toml` (shared between Python and Rust CLIs).

```toml
email = "user@example.com"
default_location = "1232176"
```

## Output Formats

### Table Format (Default)

Beautiful, human-readable tables:

```
┌─────────────┬─────────┬────────┬────────┐
│ Zone        │ Current │ Target │ Status │
├─────────────┼─────────┼────────┼────────┤
│ Livingroom  │ 19.5°C  │ 21.0°C │ Online │
│ Bedroom     │ 18.0°C  │ 20.0°C │ Online │
└─────────────┴─────────┴────────┴────────┘
```

### JSON Format

Machine-readable output for scripting:

```bash
evohome status 1232176 --format json | jq '.[] | select(.status == "heating")'
```

## Scripting Examples

### Check if Any Zone is Heating

```bash
#!/bin/bash
STATUS=$(evohome monitor --format json)
HEATING=$(echo $STATUS | jq '[.[] | select(.status == "heating")] | length')

if [ "$HEATING" -gt 0 ]; then
    echo "$HEATING zones are currently heating"
fi
```

### Boost on Cold Mornings

```bash
#!/bin/bash
TEMP=$(curl -s "wttr.in/?format=%t" | tr -d '+°C')

if [ "$TEMP" -lt 5 ]; then
    echo "Cold morning detected, boosting heating"
    evohome boost --temp 23C --duration 2h
fi
```

### Set Specific Zones by Name

```bash
#!/bin/bash
# Set living areas to comfortable temperature
evohome set living 21C
evohome set kitchen 21C

# Set bedrooms cooler
evohome set bedroom 19C
evohome set "guest bedroom" 18C
```

### Temperature Control with Units

```bash
#!/bin/bash
# US users can use Fahrenheit
evohome set living 70F --duration 2h
evohome boost --temp 72F --duration 3h

# Mix and match
evohome set bedroom 68F
evohome set bathroom 22C
```

### Daily Temperature Report

```bash
#!/bin/bash
evohome monitor 1232176 --format json | \
    jq -r '.[] | "\(.name): \(.current)°C → \(.target)°C (\(.status))"'
```

## Troubleshooting

### Command Not Found

**Python:**
```bash
# Ensure package is installed
pip install --upgrade clientmytcc

# Check installation
which evohome
```

**Rust:**
```bash
# Ensure binary is in PATH
cargo install clientmytcc

# Check installation
which evohome
```

### Authentication

You can authenticate interactively or using environment variables.

#### Interactive Login
```bash
evohome login "email@example.com"
# You will be prompted for password
```

#### Secure Credentials Storage
You can securely store your credentials in the OS keyring (macOS Keychain, Windows Credential Manager, etc.) to enable seamless auto-login.

```bash
evohome config set-credentials --email user@example.com
# You will be prompted for your password securely
```

Once set, you can run any command without `login` or environment variables:
```bash
evohome locations
```

#### Environment Variables (Auto-Login)
You can set the following environment variables to avoid logging in manually or to enable auto-login if your session expires:

- `EVOHOME_USER` (or `EVOHOME_EMAIL`): Your email address
- `EVOHOME_PASSWORD`: Your password

```bash
export EVOHOME_USER="email@example.com"
export EVOHOME_PASSWORD="your_password"

# Now you can run commands without explicit login
evohome locations
```

## Tips

1. **Use JSON for Scripting**: The `--format json` option makes it easy to parse output in scripts
2. **Set Default Location**: Store your location ID in the config file to avoid typing it repeatedly
3. **Combine with Other Tools**: Pipe JSON output to `jq` for advanced filtering
4. **Schedule Commands**: Use cron (Linux/Mac) or Task Scheduler (Windows) to automate heating schedules
5. **Skip Interactive Prompts**: The CLI shows you the exact command to run next time to skip the interactive prompts

## See Also

- [Python Client Documentation](../python/README.md)
- [Rust Client Documentation](../rust/README.md)
- [API Documentation](API_DOCUMENTATION.md)
- [GitHub Repository](https://github.com/divyavanmahajan/clientmytcc)
