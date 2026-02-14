# Walkthrough: Renaming to evohome_rs (Issue #3)

1. **Availability Check**: Verified that `evohome_rs` and `mytcc-rs` are available on both PyPI and crates.io using a browser subagent and `curl`.
2. **Structural Renaming**:
   - Updated `rust/Cargo.toml`: Package name set to `evohome_rs`, library name set to `evohome_rs`.
   - Updated `rust/pyproject.toml`: Package name set to `evohome_rs`.
3. **Identifier Refactoring**:
   - Performed a global search and replace of `clientevohome_rs` with `evohome_rs` across all source files, tests, and examples.
4. **Documentation Overhaul**:
   - Updated both `README.md` and `README-PY.md` with the new package name, updated installation commands (`pip install evohome_rs`, `uvx evohome_rs`), and badges.
5. **Fresh Versioning**:
   - Reset version to **`v0.1.0`** to signify a clean slate for the new name.
6. **Publication**:
   - Created and pushed tag `v0.1.0-mytcc`.
   - Automated CI workflows for PyPI and crates.io are currently publishing the new packages.
7. **Verification**:
   - Successfully ran a local `cargo publish --dry-run` to ensure the package is valid.
