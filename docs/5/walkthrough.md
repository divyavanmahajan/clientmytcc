# Walkthrough - evohome_py and CLI Alignment

I have successfully prepared the Python client for publication as `evohome_py` and aligned its CLI with the Rust implementation.

## Changes

### 1. Renamed Package
The python package has been renamed from `clientmytcc` to `evohome_py`.
- Source directory: `python/evohome_py`
- All imports updated in source code, tests, and examples.
- `pyproject.toml` updated with new name and entry point.

### 2. CLI Alignment
The Python CLI has been reviewed and aligned with the Rust CLI functionality.
- Commands matched: `login`, `logout`, `locations`, `account`, `set`, `boost`, `eco`, `monitor`, `vacation`, `schedule`.
- Configuration management command `config` is available.

### 3. GitHub Workflow
Created a new GitHub workflow `.github/workflows/publish-pypi.yml` to automatically publish the package to PyPI when a release is published.

## Verification Results

### Automated Tests
I verified the installation and CLI help output using the local environment.

#### CLI Help Output
```
Usage: evohome [OPTIONS] COMMAND [ARGS]...

  MyTotalConnectComfort CLI for Evohome heating control.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  account    Show account information.
  boost      Boost all zones in a location.
  config     Manage configuration.
  eco        Set all zones to energy-saving temperature.
  locations  List all locations.
  login      Authenticate with MyTotalConnectComfort.
  logout     Clear stored credentials.
  monitor    Monitor zone temperatures (alias: zones).
  schedule   Reset all zones to follow their programmed...
  set        Set zone temperature.
  vacation   Set all zones to frost protection (vacation...
```

### Next Steps
- Push the changes to GitHub.
- Create a release on GitHub to trigger the PyPI publication (once configured with trusted publishing or secrets).
