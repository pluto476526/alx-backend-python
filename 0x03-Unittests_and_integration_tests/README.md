
# 0x03. Unittests and Integration Tests

This project contains unit tests and integration tests for utility functions defined in `utils.py`.

## Project Structure

- **utils.py**  
  A Python module with utility functions:
  - `access_nested_map`: Safely accesses values in nested dictionaries.
  - `get_json`: Fetches and parses JSON from a given URL.
  - `memoize`: Decorator to cache method results on a per-instance basis.

- **test_utils.py**  
  Contains unit tests for the above utilities using the `unittest` framework, `parameterized` for test coverage, and `unittest.mock` for mocking.

## Unit Tests

### `TestAccessNestedMap`
Tests the `access_nested_map` function with:
- Valid paths (parameterized)
- Invalid paths that raise `KeyError` (with expected error messages)

### `TestGetJson`
Mocks `requests.get` to test `get_json` without making real HTTP calls. Verifies:
- Correct return value
- That the mocked request was called once with the expected URL

### `TestMemoize`
Tests the `memoize` decorator by:
- Mocking a method decorated with `@memoize`
- Confirming the method is only executed once, even if accessed multiple times

## How to Run

```bash
python3 -m unittest test_utils.py
````

## Requirements

* Python 3.7
* `parameterized` module: install via `pip install parameterized`
* Follows `pycodestyle` (PEP8) formatting guidelines
* All functions and classes include proper docstrings and type annotations

