# Walkthrough: Finalizing Package Metadata (Issue #2 & #3)

1. **Updated Cargo Metadata**: Specifically updated the `repository`, `documentation`, and `homepage` fields in `rust/Cargo.toml` to point to the correct GitHub URLs and `docs.rs/clientmytcc-rs`.
2. **Homepage Alignment**: Set the `homepage` field to point directly to the Rust-specific README on GitHub as requested.
3. **Harmonized Versions**: Bumped both Rust and Python packages to **`v0.1.12`** to ensure all published packages have the correct metadata.
4. **Git Sync**: Pushed all changes and the new tag `v0.1.12` to GitHub, triggering the automated PyPI publication workflow.
5. **Verified PyPI Docs**: Confirmed that `README-PY.md` is correctly linked in the metadata for the Python package.
