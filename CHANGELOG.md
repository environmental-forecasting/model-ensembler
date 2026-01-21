# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-01-21

### Added
* Testing suite coverage for the batcher, config, cli, runners and templates (#57, #62).
* `model_ensembler_init` command to initialise a model_ensembler project structure (#41).
* PyPI badge to README (#69).

### Changed
* Updated Makefile to reflect package structure changes (#63).
* Removed `git-authors` method of acknowledgement in favour of `authors` plugin, which generates team page/acknowledgement using an authors yaml file (#64).
* Polling rate of `submit_jobs()` to prevent spurious warnings (#42). 
* Replaced deprecated `datetime.datetime.utcnow()` with `datetime.now(timezone.utc)` (#61).
* Change `sanity-check.yml` cluster from `long` to `rocky`.
* `current_jobs` now filters by user, in addition to partition, job_name and state (#68).

## [0.6.2] - 2025-07-22

Successful installation hotfix.

## [0.6.1] - 2025-07-22

Attempted installation hotfix, yanked.

## [0.6.0] - 2025-07-16

### Added

No new features added, but restructure of package. See below.

### Changed

* Updating Documentation ([#11](https://github.com/environmental-forecasting/model-ensembler/issues/11), [#22](https://github.com/environmental-forecasting/model-ensembler/issues/22)):
    * Changed from sphinx to [mkdocs](https://www.mkdocs.org/), in line with other [environmental-forecasting](https://github.com/environmental-forecasting) tools.
    * API/Reference automatically generated using [mkdocstrings](https://mkdocstrings.github.io/) and [mkdocs-autoapi](https://mkdocs-autoapi.readthedocs.io/en/latest/).
    * Documentation now includes user guide, developer guide, testimonials and acknowledgement chapters and links to top-level files (LICENSE, CONTRIBUTING etc). Respective sub-chapters added.
    * Technical diagrams added where appropriate.
* Condensed README.md and moved non-essential sections to the docs.
* `.mailmap` file added to use James' work email in favour of personal email, for accurate contribution acknowledgement.
* Removed `setup.py`, `setup.cfg` in favour of solely using `pyproject.toml`. Automatically propagates version number from `__init.py__`. Updated editable install instructions, optional dependency management.
* Updated all docstrings to conform with [google style](https://mkdocstrings.github.io/python/usage/configuration/docstrings/), improves formatting of mkdocs-autoapi. 

## [0.5.5] - 2022-09-20

* Fixing job submissions endlessly looping after fast completion ([#40](https://github.com/environmental-forecasting/model-ensembler/issues/40))

## [0.5.2] - 2021-12-13

### Added

* Daemon functionality ([#23](https://github.com/environmental-forecasting/model-ensembler/issues/23))

### Changed

* Fixed issue with local dummy runner
* Fixed re-copy on pickup issue with deep templates

## [0.5.1] - 2021-10-31

### Added

* Ability to specify CLI based run arguments

### Changed

* Fixed issue with statuses

## [0.5.0] - 2021-10-07

_This release was a big collection of amendments from 0.4.0_

## [0.4.0] - 2021-02-06

### Added:

Initial release into the wild of the code, previously used only internally in BAS

[0.7.0]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.7.0
[0.6.2]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.6.2
[0.6.1]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.6.1
[0.6.0]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.6.0
[0.5.5]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.5.5
[0.5.2]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.5.2
[0.5.1]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.5.1 
[0.5.0]: https://github.com/environmental-forecasting/model-ensembler/releases/tag/v0.5.0
[0.4.0]: https://github.com/JimCircadian/model-ensembler/releases/tag/v0.4.0