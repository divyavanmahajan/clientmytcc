# Example: Packaging a Rust CLI as a Python Package

This example demonstrates how to set up a minimal Rust project that packages a binary into a Python wheel.

## 1. Project Structure

```text
my_tool/
├── Cargo.toml
├── pyproject.toml
└── src/
    └── main.rs
```

## 2. Cargo.toml

```toml
[package]
name = "my_tool_rust"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "my-fast-cli"
path = "src/main.rs"
```

## 3. src/main.rs

```rust
fn main() {
    println!("Hello from Rust binary packaged in Python!");
}
```

## 4. pyproject.toml

```toml
[build-system]
requires = ["maturin>=1.0,<2.0"]
build-backend = "maturin"

[project]
name = "my-tool-python"
version = "0.1.0"
description = "Python wrapper for a Rust CLI"
requires-python = ">=3.7"

[tool.maturin]
bindings = "bin"
```

## 5. Usage

1.  **Install**: `pip install .` (or `maturin develop`)
2.  **Run**: `my-fast-cli`
