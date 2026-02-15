# Implementation Plan - Publish evohome_py and Align CLI

The goal is to prepare the Python client for publishing as `evohome_py` on PyPi and ensure its CLI parity with the Rust implementation.

## User Review Required

> [!IMPORTANT]
> The Python package name will be changed from `clientmytcc` to `evohome_py`. This involves renaming the source directory and updating configuration.

## Proposed Changes

### Configuration
#### [MODIFY] [pyproject.toml](file:///Users/divya/Documents/projects/homeautomation/mytotalconnectcomfort/python/pyproject.toml)
- Update `project.name` to `evohome_py`.
- Update `project.scripts` to point to the new package structure.
- Review dependencies and classifiers.

### Python Codebase
#### [RENAME] `python/clientmytcc` -> `python/evohome_py`
- Rename the source directory.

#### [MODIFY] [python/evohome_py/cli.py](file:///Users/divya/Documents/projects/homeautomation/mytotalconnectcomfort/python/clientmytcc/cli.py)
- Review and update CLI commands to match `rust/src/bin/evohome_rs.rs`.
- Ensure arguments and defaults match (e.g., Duration handling in `set` command).
- Ensure output formatting is consistent.

### GitHub Workflows
#### [NEW] `.github/workflows/publish-pypi.yml`
- Create a workflow to publish to PyPi on release or tag.

## Verification Plan

### Automated Tests
- Run existing tests using `pytest` to ensure no regression after renaming.
- `cd python && pytest`

### Manual Verification
- Install the package locally: `pip install -e python/`
- Run CLI commands and compare with Rust CLI output.
    - `evohome --help`
    - `evohome login`
    - `evohome list` / `evohome monitor`
    - `evohome set --help`
