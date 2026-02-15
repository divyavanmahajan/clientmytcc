# AGENT.md - MyTotalConnectComfort Repository

## Repository Overview

This is a **monorepo** containing client libraries for the **International Honeywell Evohome** heating system API (MyTotalConnectComfort). The repository provides both **Python** and **Rust** implementations, along with comprehensive API documentation.

### Repository Structure

```
clientmytcc/
├── python/           # Pure Python package (evohome_py)
├── rust/             # Rust library + CLI binary (evohome_rs)
├── api/              # API documentation and OpenAPI spec
├── docs/             # Project-wide documentation
└── .github/          # CI/CD workflows
```

## Packages

### 1. evohome_py (Python)
- **Package Name**: `evohome_py`
- **PyPI**: https://pypi.org/p/evohome_py
- **Location**: `python/`
- **Current Version**: 0.2.2
- **Type**: Pure Python library with CLI
- **Entry Points**: `evohome` and `evohome_py` commands

### 2. evohome_rs (Rust)
- **Package Name**: `evohome_rs`
- **PyPI**: https://pypi.org/p/evohome_rs (Python bindings)
- **Crates.io**: https://crates.io/crates/evohome_rs
- **Location**: `rust/`
- **Current Version**: 0.2.2
- **Type**: Rust library + standalone binary (packaged for Python via Maturin)
- **Entry Point**: `evohome_rs` command

## Version Management

**CRITICAL**: Both packages MUST maintain the same version number.

### Version Files to Update

When bumping versions, update ALL of these files:

1. **Python Package**:
   - `python/pyproject.toml` → `version = "X.Y.Z"`
   - `python/evohome_py/__init__.py` → `__version__ = "X.Y.Z"`

2. **Rust Package**:
   - `rust/Cargo.toml` → `version = "X.Y.Z"`
   - `rust/pyproject.toml` → `version = "X.Y.Z"`

### Version Bump Process

```bash
# 1. Update all 4 version files
# 2. Commit changes
git add .
git commit -m "chore: bump version to X.Y.Z"

# 3. Push and tag
git push
git tag vX.Y.Z
git push origin vX.Y.Z
```

## CI/CD Pipeline

### Publishing Workflow (`.github/workflows/pypi.yml`)

**Trigger**: Push of tags matching `v*` (e.g., `v0.2.2`)

**Jobs**:
1. **pypi-evohome-py**: Builds and publishes pure Python package
2. **linux/windows/macos/sdist**: Builds Rust binary wheels for multiple platforms
3. **release**: Publishes Rust package to PyPI

**Secrets Required**:
- `PYPI_API_TOKEN`: PyPI API token for publishing both packages

### Workflow Execution

When you push a tag:
```bash
git tag v0.2.2
git push origin v0.2.2
```

The workflow automatically:
1. Builds `evohome_py` Python package
2. Builds `evohome_rs` for Linux (x86_64), Windows (x64, x86), macOS (x86_64, aarch64)
3. Publishes both to PyPI

## Development Workflows

### Working on Python Package

```bash
cd python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

### Working on Rust Package

```bash
cd rust
cargo build
cargo test
cargo run --bin evohome_rs -- --help
```

### Testing CLI Tools

```bash
# Python CLI
evohome --help
evohome login --email user@example.com

# Rust CLI
evohome_rs --help
evohome_rs login --email user@example.com
```

## Common Tasks

### 1. Adding a New API Endpoint

1. **Update API Documentation**: `api/API_DOCUMENTATION.md`
2. **Python Implementation**:
   - Add method to `python/evohome_py/client.py`
   - Add models to `python/evohome_py/models.py`
   - Add tests to `python/tests/`
3. **Rust Implementation**:
   - Add method to `rust/src/client.rs`
   - Add models to `rust/src/models.rs`
   - Add tests to `rust/tests/`
4. **CLI Support** (if applicable):
   - Python: `python/evohome_py/cli.py`
   - Rust: `rust/src/bin/evohome_rs.rs`

### 2. Fixing a Bug

1. **Create GitHub Issue**: Document the bug
2. **Create Branch**: `git checkout -b fix/issue-description`
3. **Fix in Both Implementations** (if applicable)
4. **Add Tests**: Ensure regression tests exist
5. **Update Documentation**: If behavior changes
6. **Commit**: Use conventional commits (e.g., `fix: resolve temperature rounding issue`)
7. **Create PR**: Reference the issue number

### 3. Releasing a New Version

1. **Update Version**: All 4 version files (see above)
2. **Update Changelogs**: Document changes in both `python/` and `rust/`
3. **Commit**: `git commit -m "chore: bump version to X.Y.Z"`
4. **Tag**: `git tag vX.Y.Z`
5. **Push**: `git push && git push origin vX.Y.Z`
6. **Monitor CI**: Check GitHub Actions for build status
7. **Verify PyPI**: Confirm both packages published successfully

## Architecture Decisions

### Why Two Implementations?

1. **Python (`evohome_py`)**:
   - Easy to use for scripting and automation
   - Lower barrier to entry
   - Synchronous API (simpler mental model)
   - Ideal for Home Assistant integrations

2. **Rust (`evohome_rs`)**:
   - High-performance async operations
   - Type safety at compile time
   - Standalone binary with no Python dependency
   - Ideal for embedded systems or performance-critical apps

### Why Monorepo?

- Shared API documentation
- Consistent versioning
- Single source of truth for API behavior
- Easier to keep implementations in sync

## Testing Strategy

### Python Tests
- **Unit Tests**: Mock HTTP responses
- **Integration Tests**: Use environment variables for real credentials
- **Coverage**: Aim for >80%

### Rust Tests
- **Unit Tests**: Test individual functions
- **Integration Tests**: Marked with `#[ignore]`, require credentials
- **Doc Tests**: Examples in documentation are tested

### Environment Variables for Testing

```bash
export EVOHOME_EMAIL="your-email@example.com"
export EVOHOME_PASSWORD="your-password"

# Python
cd python && pytest

# Rust
cd rust && cargo test --ignored
```

## Documentation Structure

### Repository-Level Docs
- `README.md`: Overview and quick start
- `AGENT.md`: This file (AI agent context)
- `api/API_DOCUMENTATION.md`: Complete API reference

### Python Package Docs
- `python/README.md`: Installation and usage
- `python/AGENT.md`: Python-specific context
- `python/docs/`: Detailed guides

### Rust Package Docs
- `rust/README.md`: Installation and usage
- `rust/AGENT.md`: Rust-specific context
- `rust/docs/`: Detailed guides

## Troubleshooting

### Publishing Fails

1. **Check PyPI Token**: Ensure `PYPI_API_TOKEN` secret is set in GitHub
2. **Version Conflict**: PyPI won't accept duplicate versions - bump version
3. **Build Errors**: Check GitHub Actions logs for specific platform failures

### CLI Not Found After Install

**Python**:
```bash
pip install --upgrade evohome_py
which evohome  # Should show installed location
```

**Rust**:
```bash
pip install --upgrade evohome_rs
which evohome_rs  # Should show installed location
```

### Version Mismatch

If packages have different versions:
1. Update all 4 version files
2. Commit and tag
3. Re-publish

## Contributing

See individual package AGENT.md files for language-specific guidelines:
- `python/AGENT.md`
- `rust/AGENT.md`

## License

MIT License - See LICENSE files in `python/` and `rust/` directories.

## Disclaimer

This is an unofficial library for the International Honeywell Evohome system (provided by Resideo Technologies, Inc.). Not affiliated with Honeywell or Resideo.
