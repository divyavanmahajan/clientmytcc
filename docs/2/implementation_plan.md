# Implementation Plan: Rename Rust Package and Prepare for crates.io

## Goal
Rename the Rust crate to `clientmytcc-rs` and update all references to ensure the project builds and is ready for publication.

## Steps
1. **Update `rust/Cargo.toml`**: Change `name = "clientmytcc"` to `name = "clientmytcc-rs"`.
2. **Global Search and Replace**:
   - Replace `clientmytcc` with `clientmytcc_rs` in all `.rs` files (identifiers use underscores).
   - Update `pyproject.toml` if it references the library name (it currently uses `bindings = "bin"`, so it might be fine, but I'll check).
3. **Fix Documentation**: Update `README.md` and `README-PY.md`.
4. **Validation**: Run `cargo build` and `cargo test` in the `rust/` directory.
5. **Publication Preparation**: Ensure `Cargo.toml` has all necessary fields for crates.io.
