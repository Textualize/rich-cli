# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Nothing yet

## [1.8.1] - 2025-07-04

### Fixed

- "UserWarning: The parameter -j is used more than once" in https://github.com/Textualize/rich-cli/pull/74
- Fixed generic blend text in https://github.com/Textualize/rich-cli/pull/51

### Changed

- Rich-CLI now assumes that the input file is encoded in UTF-8 https://github.com/Textualize/rich-cli/pull/56
- The JSON display mode is now `-J/--json`
- _Python >= 3.9_ is now required, so no more support for 3.7 and 3.8
- Hard-code UTF-8 encoding for the input file in https://github.com/Textualize/rich-cli/pull/56
- Updated pyproject.toml to PEP621 and Poetry 2.* in https://github.com/Textualize/rich-cli/pull/103

## [1.8.0] - 2022-05-07

### Changed

- Bumped Rich for improved SVG export

## [1.7.0] - 2022-05-1

## Added

- Added Jupyter Notebook support https://github.com/Textualize/rich-cli/pull/47
- Added --export-svg option
- Added support for vi navigation to pager https://github.com/Textualize/rich-cli/pull/44/

## [1.6.1] - 2022-04-23

### Fixed

- Fixed wrong version number reported

## [1.6.0] - 2022-04-23

### Added

- Added space key to page down to pager

### Changed

- Change how code blocks in markdown are rendered (remove border, adding padding)
