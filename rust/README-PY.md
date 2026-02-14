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

## Features

- **Blazing Fast**: Core logic implemented in async Rust.
- **Cross-Platform**: Pre-built wheels for Linux, macOS, and Windows.
- **Full Control**: Support for listing locations, monitoring zones, setting temperatures, and managing schedules.
- **Session Management**: Automatic and secure session handling.

## Detailed Documentation

For a full list of commands, API details, and Rust library usage, please refer to the main [Rust README.md](https://github.com/divyavanmahajan/clientmytcc/blob/main/rust/README.md).

---

*Disclaimer: This is an unofficial tool and is not affiliated with Honeywell or Resideo.*
