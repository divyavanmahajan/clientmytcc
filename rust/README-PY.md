# clientmytcc-rs

This Python package provides a fast, Rust-powered CLI for the **International Honeywell Evohome** heating system (MyTotalConnectComfort). It is a lightweight wrapper around the `evohome` binary built in Rust.

## Quick Start (No Installation Required)

You can run the CLI immediately without installing it using `uvx`:

```bash
# Login to your account
uvx clientmytcc-rs login --email user@example.com

# Check your zone temperatures
uvx clientmytcc-rs monitor
```

## Installation

Install the package via `pip` or `uv`:

```bash
pip install clientmytcc-rs
# OR
uv add clientmytcc-rs
```

Once installed, you can use the `evohome` command directly:

```bash
evohome --help
```

## CLI Usage
The project includes a binary `evohome` for controlling your heating system from the command line.

### Basic Commands
```bash
# Login (saves session to ~/.config/clientmytcc/session.json)
evohome login --email user@example.com

# List locations
evohome locations

# Monitor all zones
evohome monitor

# Logout (clears session)
evohome logout
```

### Temperature Control
```bash
# Set temperature for a specific zone
evohome set --zone-id "Living Room" --temperature 21.0

# Boost all zones
evohome boost --temp 22.0 --duration 2

# Enable Eco mode
evohome eco

# Enable Vacation mode
evohome vacation --temp 12.0

# Reset all zones to follow schedule
evohome schedule
```

## Detailed Documentation

For a full list of commands, API details, and Rust library usage, please refer to the main [Rust README.md](https://github.com/divyavanmahajan/clientmytcc/blob/main/rust/README.md) or the [API Documentation](https://docs.rs/clientmytcc-rs).

---

*Disclaimer: This is an unofficial tool and is not affiliated with Honeywell or Resideo.*
