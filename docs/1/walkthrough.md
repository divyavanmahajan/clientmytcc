# Walkthrough: Packaging Rust Binary with Maturin

1. **Created `rust/pyproject.toml`**: This file tells Python's build system (using `maturin`) how to package the Rust binary.
2. **Setup Virtual Environment**: Created a venv in the `rust` directory to isolate dependencies.
3. **Installed Maturin**: Ran `pip install maturin` within the venv.
4. **Built and Installed**: Ran `maturin develop`. This compiled the Rust code and installed the `evohome-rs` package into the venv.
5. **Verified**: Ran `evohome --help` which confirmed the Rust binary is now available as a CLI command in the Python environment.
