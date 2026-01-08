# Parallel Pytest (para-pytest)

Run pytest tests in parallel chunks for significantly faster test execution.


## Installation

```bash
pip install para-pytest
```


## Quick Start

```bash
# Run with default settings (4 chunks)
para-pytest

# Specify number of chunks
para-pytest --chunks 8

# Specify test path
para-pytest --path tests/
```


## Use Cases

### Local Development

Speed up your test suite during development:

```bash
# Before (sequential execution)
pytest tests/

# After (parallel execution)
para-pytest --chunks 4
```

### Continuous Integration

Add to your GitHub Actions workflow:
```yaml
name: Tests

on: [push, pull_request]

jobs: 
	test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12.3'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install para-pytest

      - name: Run tests
        run: para-pytest --chunks 4 --path tests/
```

Or use the Github Action:
```yaml
- uses: ALHelton/parallel-pytest@v1
  with:
    chunks: 8
    path: tests/
```

### Python API

```python
from para_pytest import ParaPytestRunner

# Serial patterns are automatically loaded from pyproject.toml
runner = ParaPytestRunner(chunks=4, pytest_args=['tests/'])
exit_code = runner.run()

# Or override with explicit patterns
runner = ParaPytestRunner(
    chunks=4,
    pytest_args=['tests/'],
    serial_patterns=['**/test_database_*', '**/test_integration_*']
)
exit_code = runner.run()
```


## Configuration (Optional)

### Serial Test Patterns

Some tests can't run in parallel (e.g., database tests, integration tests with shared state). Configure these to run serially by adding to your existing `pyproject.toml`:

```toml
[tool.para-pytest]
serial_patterns = [
    "**/test_database_*",
    "**/test_migration_*",
    "**/test_integration_*",
    "tests/e2e/**"
]
```

**Pattern examples:**
- `**/test_database_*` - Any test file starting with `test_database_` anywhere in your project
- `tests/e2e/**` - All tests in the `tests/e2e/` directory and subdirectories
- `**/test_*_integration.py` - Any test file ending with `_integration.py`

That's it! No external dependencies required - the configuration is parsed using built-in Python modules.


## How It Works

1. Loads serial patterns from `pyproject.toml` (if configured)
2. Collects all tests from pytest
3. Separates tests into parallel and serial groups based on patterns
4. Splits parallel tests into equal chunks
5. Runs parallel chunks concurrently using asyncio
6. Runs serial tests sequentially (if any)
7. Aggregates and displays results


## Requirements

- Python 3.8+
- pytest 7.0+


## License 

MIT