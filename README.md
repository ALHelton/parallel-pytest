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

# Specify test path (default '.')
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

runner = ParaPytestRunner(chunks=4, pytest_args=['tests/'])
exit_code = runner.run()
```


## How It Works

1. Collects all tests from pytest
2. Splits tests into equal chunks
3. Runs chunks in parallel using asyncio
4. Aggregates and displays results


## Requirements

- Python 3.9+
- pytest 7.0+


## License 

MIT