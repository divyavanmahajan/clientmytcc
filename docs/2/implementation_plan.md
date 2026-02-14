# Implementation Plan: Rename Rust Package to `evohome_rs` and Publish

## Goal
Rename the Rust crate to `evohome_rs` and update all references to ensure the project builds and is published to crates.io.

## Steps
- [x] **Update `rust/Cargo.toml`**: Rename package to `evohome_rs`.
- [x] **Global Search and Replace**: Update identifiers and text references from `mytcc_rs` to `evohome_rs`.
- [x] **Fix Documentation**: Update `README.md` and `README-PY.md`.
- [x] **Validation**: Run `cargo build` and `cargo test` in the `rust/` directory.
- [x] **Publication**: Publish `evohome_rs` to crates.io.

