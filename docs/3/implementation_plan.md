# Implementation Plan: Rename package to mytcc_rs

## Goal
Transition the project from `clientmytcc-rs` to `mytcc_rs`.

## Steps
1. **Update `rust/Cargo.toml`**:
   - `name = "mytcc_rs"`
   - `[lib] name = "mytcc_rs"`
2. **Update `rust/pyproject.toml`**:
   - `name = "mytcc_rs"`
3. **Internal Code Update**:
   - Replace all `clientmytcc_rs` with `mytcc_rs` in `.rs` files.
4. **Documentation Update**:
   - Update `README.md` and `README-PY.md` with the new package name and usage examples.
5. **Version Bump**:
   - Set version to `0.1.0` (fresh start for the new name).
6. **Publication**:
   - Push to GitHub to trigger CI.
   - Publish manually to crates.io (after verification).
