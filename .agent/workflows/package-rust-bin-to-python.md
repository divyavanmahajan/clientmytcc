---
description: How to package an existing Rust project as a Python package with a standalone binary.
---

# Package Rust Binary to Python Workflow

Follow these steps to convert an existing Rust project into a Python-distributable package that installs a binary on the user's PATH.

## 1. Prepare Cargo.toml

Ensure your Rust project has at least one binary target. Open `Cargo.toml` and verify or add a `[[bin]]` section.

**Example addition:**
```toml
[[bin]]
name = "your-command-name"
path = "src/main.rs" # or src/bin/your_cmd.rs
```

## 2. Create pyproject.toml

In the same directory as `Cargo.toml`, create a `pyproject.toml` file to configure the Python package metadata and the Maturin build system.

**Template:**
```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "your-python-package-name"
version = "0.1.0"
description = "Description of your tool"
requires-python = ">=3.7"

[tool.maturin]
bindings = "bin"
```

## 3. Verify Maturin Installation

Ensure you have `maturin` installed in your Python environment.

// turbo
```bash
pip install maturin
```

## 4. Install for Local Testing

Run `maturin develop` to build the Rust binary and install it into your current Python environment.

// turbo
```bash
maturin develop
```

## 5. Verify the Binary

Once the command completes, you should be able to run your binary directly from the terminal.

```bash
your-command-name --help
```

---

*Note: If you encounter issues with multiple binaries or need to include a library as well, refer to the [rust_binary_python_package skill](../skills/rust_binary_python_package/SKILL.md) for advanced configurations.*
