# Task: Secure Credentials Storage

As a user, I want to securely store my Evohome credentials on my local machine.

## Checklist
- [x] Add `keyring` dependency to `rust/Cargo.toml`.
- [x] Add `config` command to `evohome` CLI.
- [x] Implement `config set-credentials` to prompt for email and password and save to OS keyring.
- [x] Implement `get_credentials_from_keyring` helper.
- [x] Update `get_authenticated_client` to:
    1. Check CLI arguments (already done).
    2. Check environment variables (already done).
    3. Check keyring if previous methods fail.
    4. Provide helpful error if all methods fail.
- [x] Update documentation to explain how to use `config set-credentials`.
