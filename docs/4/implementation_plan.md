# Implementation Plan: Secure Credentials Storage (Issue #4)

## Goal
Enable users to securely store and retrieve their Evohome credentials from the OS keyring, eliminating the need for environment variables or manual entry.

## User Review Required
> [!IMPORTANT]
> This requires adding the `keyring` crate dependency, which links to system libraries (e.g., `libsecret` on Linux). This might require installing `libsecret-1-dev` on Linux build environments.

## Proposed Changes

### `rust/Cargo.toml`
- Add `keyring` dependency.

### `rust/src/bin/evohome.rs`
1. **Update `enum Commands`**:
   - Add `Config { command: ConfigCommands }` subcommand.
   - Define `ConfigCommands` enum with `SetCredentials` variant.

2. **Implement `set_credentials`**:
   - Prompt user for email and password.
   - Use `keyring::Entry::new("mytcc-rs", email)` to store the password.
   - Also store the email in `~/.config/mytcc_rs/config.toml` (or similar) so we know which user to look up, OR just use a fixed key like "default_user" in keyring if we only support one user, OR prompt for email and look up password.
   - *Refined Approach*: Use `keyring::Entry::new("mytcc-rs", "default")` to store a JSON object `{"email": "...", "password": "..."}`?
   - *Better Approach*: Use `keyring` for password only. Store the "current email" in a config file.
   - *Simpler MVP*: `evohome config set-credentials` asks for email and password. Stores password in keyring under service "mytcc-rs" and username == email. Stores the email in a local config file as "default_user".

3. **Update `get_authenticated_client`**:
   - **Priority 1**: CLI Args (`--email`, `--password`)
   - **Priority 2**: Environment Variables (`EVOHOME_USER`, `EVOHOME_PASSWORD`)
   - **Priority 3**: Config File + Keyring
     - Load `default_user` from config file.
     - If found, look up password in keyring for service "mytcc-rs" and username `default_user`.
     - Login with these credentials.

4. **Update** all the docs to reflect the changes.
## Verification Plan

### Manual Verification
- Run `evohome config set-credentials`.
- Verify credentials are saved (e.g., check Keychain on macOS).
- Run `evohome locations` without env vars or args.
- Verify login succeeds.
