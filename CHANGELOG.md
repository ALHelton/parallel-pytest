# Changelog

All notable changes to para-pytest will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2026-01-12

### Fixed
- **Critical**: Serial pattern matching now correctly matches test node IDs
  - Previously, patterns like `"app/tests/unit/test_database.py"` would not match actual test node IDs like `"app/tests/unit/test_database.py::test_function"`
  - This caused tests configured as serial to incorrectly run in parallel, leading to database collisions and test failures
  - Patterns ending in `.py` without `::` are now automatically expanded to match all tests within those files

### Added
- Automatic pattern expansion for file paths - no need to manually add wildcards
  - Simple file paths like `"tests/unit/test_database.py"` now automatically match all tests in the file
  - Wildcard patterns still work as expected (e.g., `"**/test_database_*"`, `"tests/e2e/**"`)

### Changed
- Improved pattern matching logic to be more intuitive
- Enhanced documentation with clear examples of simple file paths vs wildcard patterns

## [0.1.2] - Previous Release

Initial release with basic parallel test execution functionality.


