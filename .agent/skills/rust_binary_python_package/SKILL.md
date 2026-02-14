---
name: rust_binary_python_package
description: Package a Rust binary into a Python package using Maturin.
---

# Rust Binary into Python Package with Maturin

This skill provides a comprehensive guide and templates for packaging a Rust application as a standalone binary within a Python package. This allows users to `pip install` your Rust tool and have it available on their system path.

## Background

Maturin supports distributing binary applications written in Rust as Python packages using the `bin` bindings. Binaries are packaged into the wheel as "scripts" and are automatically available on the user's `PATH` (e.g., in the `bin` directory of a virtual environment) once installed.

## Prerequisites

- [Maturin](https://github.com/pyo3/maturin) installed: `pip install maturin`
- A Rust project with one or more binary targets (`[[bin]]` in `Cargo.toml`).

## Core Configuration

To package a Rust binary, you need a `pyproject.toml` file in your Rust project root (or the root of your repository if it's a workspace).

### pyproject.toml Template

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "my-cli-tool"
version = "0.1.0"
description = "A powerful tool written in Rust"
requires-python = ">=3.7"
license = { text = "MIT" }

[tool.maturin]
# Explicitly specify 'bin' bindings to ensure it's packaged as a script
features = ["pyo3"] # Optional, only if you also have pyo3 bindings
bindings = "bin"
```

### Cargo.toml Setup

Ensure your `Cargo.toml` has a binary target:

```toml
[package]
name = "my-cli-tool"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "my-bin"
path = "src/main.rs"
```

## Implementation Workflow

1.  **Initialize pyproject.toml**: Create a `pyproject.toml` in your Rust project directory.
2.  **Verify Binary Target**: Ensure `Cargo.toml` has the correct `[[bin]]` sections.
3.  **Local Development**:
    *   Install the package locally in editable mode (requires `pip >= 21.3` and building with `--interpreter` if needed):
        ```bash
        maturin develop
        ```
    *   Verify the binary is available: `my-bin --help`
4.  **Building Wheels**:
    *   Build wheels for the current platform:
        ```bash
        maturin build --release
        ```
    *   The resulting wheels will be in `target/wheels/`.

## Best Practices

### Both Binary and Library?
If you want to ship both a library and a binary, maturin suggests exposing a CLI function in the library and using a Python entrypoint instead of `bin` bindings to avoid doubling the wheel size.

**Python Entrypoint Example:**

1.  In `src/lib.rs` (using PyO3):
    ```rust
    #[pyfunction]
    fn run_cli() -> PyResult<()> {
        // Your CLI logic here
        Ok(())
    }

    #[pymodule]
    fn my_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(run_cli, m)?)?;
        Ok(())
    }
    ```

2.  In `pyproject.toml`:
    ```toml
    [project.scripts]
    my-tool = "my_module:run_cli"
    ```

## Troubleshooting

- **Binary not found**: Ensure `bindings = "bin"` is set in `pyproject.toml` or passed via `-b bin` to maturin.
- **Multiple binaries**: If you have multiple `[[bin]]` targets, all of them will be included in the wheel and made available on the `PATH`.
- **Naming conflicts**: Ensure the binary names in `Cargo.toml` don't conflict with existing Python scripts or common system tools.
