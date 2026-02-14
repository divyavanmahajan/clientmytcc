# CLI User Guide

## Overview

The `evohome_rs` command-line tool provides easy access to the MyTotalConnectComfort API for controlling your International Honeywell Evohome heating system.

## Installation

### Python

```bash
pip install evohome_rs
```

### Rust

```bash
cargo install evohome_rs
```

## Quick Start

### Quick Start

```bash
evohome_rs login user@example.com
# Enter password when prompted
```

### List Locations

```bash
evohome_rs locations
```

### View Zone Status

```bash
# Auto-selects location if you have only one
evohome_rs zones

# Or specify location ID
evohome_rs zones 1232176
```

### Set Temperature

```bash
### Set Temperature

```bash
# By zone name (case-insensitive prefix matching)
evohome_rs set living 21C
evohome_rs set bed 70F

# By zone ID
evohome_rs set 5211675 21C

# With duration
evohome_rs set living 22C --duration 2h
evohome_rs set bedroom 72F --duration 30m

# Interactive mode (prompts for location, zone, and temperature)
evohome_rs set
```

## Commands

### Authentication

#### `evohome_rs login <email>`
Authenticate with your MyTotalConnectComfort account.

```bash
evohome_rs login user@example.com
```

#### `evohome_rs logout`
Clear stored credentials.

```bash
evohome_rs logout
```

### Information

#### `evohome_rs locations`
List all locations (homes) associated with your account.

```bash
evohome_rs locations
```

Output:
```
┌──────────┬──────┬────────┬───────┐
│ ID       │ Name │ City   │ Zones │
├──────────┼──────┼────────┼───────┤
│ 1232176  │ Home │ London │ 5     │
└──────────┴──────┴────────┴───────┘
```

#### `evohome_rs zones <location-id>`
List all zones in a location.

```bash
evohome_rs zones 1232176
```

#### `evohome_rs status <location-id> [--format table|json]`
Show current status of all zones.

```bash
# Table format (default)
evohome_rs status 1232176

# JSON format
evohome_rs status 1232176 --format json
```

#### `evohome_rs account`
Show account information.

```bash
evohome_rs account
```

### Temperature Control

#### `evohome_rs set <zone> <temperature> [OPTIONS]`
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
**Examples:**

```bash
# By zone name with Celsius
evohome_rs set living 21C
evohome_rs set bedroom 70F

# By zone prefix
evohome_rs set liv 21.5C
evohome_rs set bed 22C

# By zone ID
evohome_rs set 5211675 21C

# With duration
evohome_rs set living 22C --duration 2h
evohome_rs set bedroom 72F --duration 30m
evohome_rs set bathroom 23C --duration 1.5h

# Interactive mode
evohome_rs set
# → Prompts for location (if multiple)
# → Prompts for zone
# → Prompts for temperature
# → [INFO] Command to skip selection: evohome_rs set 5211675 21C
```

## Common Use Cases

### Morning Boost

Boost all zones to a comfortable temperature for a few hours.

```bash
# Auto-selects location if you have only one
evohome_rs boost --temp 22C --duration 2h

# Specify location
evohome_rs boost 1232176 --temp 72F --duration 3h

# With minutes
evohome_rs boost --temp 23C --duration 120m
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
evohome_rs boost --temp 23C --duration 3h
```

### Energy Saving Mode

Set all zones to an energy-saving temperature.

```bash
# Auto-selects location
evohome_rs eco --temp 18C

# With Fahrenheit
evohome_rs eco --temp 64F

# Specify location
evohome_rs eco 1232176 --temp 17C
```

**Options:**
- `--temp <temperature>` - Eco temperature (default: 18C)

**Example:**
```bash
# Set to 17°C
evohome_rs eco 1232176 --temp 17.0
```

### Temperature Monitoring

View current status of all zones with heating status.

```bash
# Table format (auto-selects location)
evohome_rs monitor

# JSON format for scripting
evohome_rs monitor --format json

# Specify location
evohome_rs monitor 1232176 --format table
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
evohome_rs vacation --temp 12C

# With Fahrenheit
evohome_rs vacation --temp 54F

# Specify location
evohome_rs vacation 1232176 --temp 10C
```

**Options:**
- `--temp <temperature>` - Frost protection temperature (default: 12C)

### Resume Schedule

Reset all zones to follow their programmed schedule (removes any manual overrides).

```bash
# Auto-selects location
evohome_rs schedule

# Specify location
evohome_rs schedule 1232176
```

This command cancels any temporary or permanent temperature overrides and returns all zones to their normal scheduled operation.

## Smart Features

### Interactive Location Selection

### Interactive Location Selection

If location is not specified:
- **Single location**: Auto-selects with confirmation message
- **Multiple locations**: Prompts you to select from list
- **Default location**: Uses `default_location` from config if set

```bash
# Set default location
evohome_rs config set default_location 1232176

# Now all commands auto-use this location
evohome_rs boost
evohome_rs monitor
evohome_rs zones
```

### Zone Name Matching

Zones can be specified by:
- **Zone ID** (numeric): `5211675`
- **Exact name**: `Livingroom`, `Bedroom`
- **Name prefix** (case-insensitive): `liv`, `bed`, `bath`

```bash
# All of these work:
evohome_rs set 5211675 21C          # By ID
evohome_rs set Livingroom 21C       # By exact name
evohome_rs set livingroom 21C       # Case-insensitive
evohome_rs set liv 21C              # By prefix
evohome_rs set LIVING 21C           # Case-insensitive prefix
```

If multiple zones match the prefix, you'll be prompted to select:
```bash
evohome_rs set b 21C
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
evohome_rs set living 70F    # → 21.1°C
evohome_rs boost --temp 72F  # → 22.2°C
```

### Duration Units

Supports hours and minutes:
- **Hours**: `2h`, `3h`, `1.5h` (decimals supported)
- **Minutes**: `30m`, `90m`, `120m`

```bash
evohome_rs set living 21C --duration 2h      # 2 hours
evohome_rs set bedroom 22C --duration 30m    # 30 minutes
evohome_rs boost --duration 1.5h             # 1 hour 30 minutes
```

Configuration is stored in `~/.config/evohome_rs/config.toml` (shared between Python and Rust CLIs).

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
evohome_rs status 1232176 --format json | jq '.[] | select(.status == "heating")'
```

## Scripting Examples

### Check if Any Zone is Heating

```bash
#!/bin/bash
STATUS=$(evohome_rs monitor --format json)
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
    evohome_rs boost --temp 23C --duration 2h
fi
```

### Set Specific Zones by Name

```bash
#!/bin/bash
# Set living areas to comfortable temperature
evohome_rs set living 21C
evohome_rs set kitchen 21C

# Set bedrooms cooler
evohome_rs set bedroom 19C
evohome_rs set "guest bedroom" 18C
```

### Temperature Control with Units

```bash
#!/bin/bash
# US users can use Fahrenheit
evohome_rs set living 70F --duration 2h
evohome_rs boost --temp 72F --duration 3h

# Mix and match
evohome_rs set bedroom 68F
evohome_rs set bathroom 22C
```

### Daily Temperature Report

```bash
#!/bin/bash
evohome_rs monitor 1232176 --format json | \
    jq -r '.[] | "\(.name): \(.current)°C → \(.target)°C (\(.status))"'
```

## Troubleshooting

### Command Not Found

**Python:**
```bash
# Ensure package is installed
pip install --upgrade evohome_rs

# Check installation
which evohome_rs
```

**Rust:**
```bash
# Ensure binary is in PATH
cargo install evohome_rs

# Check installation
which evohome_rs
```

### Authentication

You can authenticate interactively or using environment variables.

#### Interactive Login
```bash
evohome_rs login "email@example.com"
# You will be prompted for password
```

#### Secure Credentials Storage
You can securely store your credentials in the OS keyring (macOS Keychain, Windows Credential Manager, etc.) to enable seamless auto-login.

```bash
evohome_rs config set-credentials --email user@example.com
# You will be prompted for your password securely
```

Once set, you can run any command without `login` or environment variables:
```bash
evohome_rs locations
```

#### Environment Variables (Auto-Login)
You can set the following environment variables to avoid logging in manually or to enable auto-login if your session expires:

- `EVOHOME_USER` (or `EVOHOME_EMAIL`): Your email address
- `EVOHOME_PASSWORD`: Your password

```bash
export EVOHOME_USER="email@example.com"
export EVOHOME_PASSWORD="your_password"

# Now you can run commands without explicit login
evohome_rs locations
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
