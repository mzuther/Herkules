# Change Log

_All notable changes to this project will be documented in this
file. This change log follows the conventions of
[keepachangelog.com]._

_I tend to not use
[semantic versioning](https://semver.org/), but we will see what
happens._

<!--- ---------------------------------------------------------------------- -->

## Unreleased

<!--- ---------------------------------------------------------------------- -->

## 1.2.2 - 2026-01-01

### Added

- add type information to tests

### Changed

- refactor code and tests
- run `mypy` when executing lint script

### Fixed

- fix broken main script (move source directory)

<!--- ---------------------------------------------------------------------- -->

## 1.2.1 - 2025-12-31

### Added

- add type information (and refactor)

### Changed

- fix and update dependencies

<!--- ---------------------------------------------------------------------- -->

## 1.2.0 - 2025-12-18

### Added

- add functions `herkules_diff_run()` and `herkules_diff()` which find differences
  between old runs of `herkules()` and the current state

### Changed

- enhance `example_herkules.py`
- refactor code and tests
- add coverage support and add tests for missing coverage

<!--- ---------------------------------------------------------------------- -->

## 1.1.1 - 2025-12-13

### Added

- add new option `add_metadata` which returns a list of dictonaries with keys
  "path" and "mtime" (the option defaults to `False`, so no changes are needed
  for existing code)

### Changed

- change internal representation of directory tree
- remove default values from `_herkules_recurse()`
- update `.gitignore`

### Fixed

- fix unit tests on Windows (file separator)

<!--- ---------------------------------------------------------------------- -->

## 1.1.0 - 2025-12-07

### Added

- add new option `relative_to_root` which returns paths relative to root
  directory (the option defaults to `False`, so no changes are needed for
  existing code)

### Changed

- format and lint source code using ruff
- refactor code

<!--- ---------------------------------------------------------------------- -->

## 1.0.0 - 2024-08-08

- This is the first stable release (although I have been using it professionally for over two years now).

<!--- ---------------------------------------------------------------------- -->

[keepachangelog.com]: http://keepachangelog.com/
