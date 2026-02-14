# Walkthrough: Secure Credentials Storage

## 1. Added Dependencies
- Added `keyring` crate to `rust/Cargo.toml` for cross-platform secure credentials storage.
- Added `toml` crate to `rust/Cargo.toml` for configuration file handling.

## 2. Updated CLI
- Added `config` subcommand to `evohome` CLI.
- Implemented `set-credentials` command securely prompting for password and saving it to the OS keyring.
- Saved user email to `~/.config/mytcc_rs/config.toml` to support auto-login lookup.

## 3. Updated Logic
- Modified `get_authenticated_client` to include a fallback chain:
    1. CLI Arguments
    2. Session Cookie (if valid)
    3. Secure Keyring (using stored email from config)
    4. Environment Variables

## 4. Documentation
- Updated `CLI_GUIDE.md`, `README.md`, and `README-PY.md` to include instructions for using the new secure storage feature.

## 5. Testing
- Added unit tests for `parse_temperature` in `src/bin/evohome.rs`.
- Validated all tests pass with `cargo test`.

