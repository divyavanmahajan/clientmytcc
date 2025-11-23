# Integration Tests

This directory contains integration tests that interact with the real Evohome API.

## Prerequisites

Set the following environment variables with your Evohome credentials:

```bash
export EVOHOME_USER="your-email@example.com"
export EVOHOME_PASSWORD="your-password"
```

## Running Tests

### Rust

```bash
# Run all integration tests
cargo test --test cli_integration_test -- --ignored

# Run a specific test
cargo test --test cli_integration_test test_boost_default_temp -- --ignored

# Run with output
cargo test --test cli_integration_test -- --ignored --nocapture
```

### Python

```bash
# Run all integration tests
pytest tests/test_cli_integration.py -v -m integration

# Run a specific test
pytest tests/test_cli_integration.py::test_boost_default_temp -v

# Run with output
pytest tests/test_cli_integration.py -v -s -m integration
```

## Test Coverage

The integration tests cover:

1. **Boost Command**
   - Default temperature (22°C)
   - Custom temperature (20°C)
   - Temperature restoration

2. **Eco Command**
   - Default temperature (18°C)
   - Only affects zones above eco temp
   - Temperature restoration

3. **Vacation Command**
   - Default temperature (12°C)
   - Temperature restoration

4. **Smart Skip Logic**
   - Zones at 5°C are skipped
   - Verification that skipped zones remain unchanged

## Important Notes

- **Temperature Restoration**: All tests save the original zone temperatures before making changes and restore them after the test completes.
- **5°C Zones**: Tests verify that zones set to 5°C (off/frost protection) are not modified unless the `--override` flag is used.
- **Real API**: These tests make real API calls and will actually change your heating system settings temporarily.
- **Rate Limiting**: Be mindful of API rate limits when running tests repeatedly.

## CI/CD

These tests are marked as `#[ignore]` in Rust and `@pytest.mark.integration` in Python, so they won't run in standard CI pipelines unless explicitly enabled.

To run in CI, you would need to:
1. Set up secure environment variables for credentials
2. Use `cargo test -- --ignored` or `pytest -m integration`
3. Consider running on a schedule rather than on every commit
