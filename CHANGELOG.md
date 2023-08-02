# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning](https://calver.org).<br>
![](https://img.shields.io/badge/calver-YYYY.0M.0D-informational)

## [Unreleased]
### Added

### Changed

### Removed
### [2023.07.12]
### Added
- `-s/--short` display short test and plan names
- `-stn/--split-testname` specify index from which the test name will be shortened
- `-spn/--split-planname` specify index from which the plan name will be shortened

### Changed
- `-l/--level` changed to `-l2/--level2` switch since the level1 (plan) view is default
- `-c/--cmd` option of the report command supports one argument at a time, but `-c/--cmd` can be passed several
   times for multiple results aggregation.

### Removed
- `-l/--level` argument to choose between level1 (plan) view and level2 (test) view

## [2023.06.29]
### Added
- subcommand `test` and `report`
- `test` keeps the current behavior of dispatching jobs to the Testing Farm Endpoint
- `report` parses the requests xunit for results at two levels l1: plans, l2: tests
  - `-l/--level` provides detail for either plans (l1) or tests (l2)
  - `-w/--wait` waits for the task to finish and reports afterward
  - tasks can be parsed from multiple sources
    - default is the `./latest_jobs` file
    - `-lt/--latest` parses tasks from latest `test` session created at `/tmp/tesar_latest_jobs`
    - `-f/--file` parses a specified file location, other than the default
    - `-c/--cmd` parses tasks from passed to the commandline
    - `-d/--download-logs` downloads log files locally
 - option `-w/--wait` to specify number of seconds to wait for a successful response with default 20 seconds
 - option `-nw/--no-wait` to bypass waiting for response and get the link ASAP
 - option `-pw/--pool-workaround` to request `baseosci-openstack` pool for the provisioning
### Changed
- request official non-custom AWS AMIs as targets (applies to Alma, Rocky and Oracle-latest)
- fixed broken top level plan invocation, when plan ends with `/`
### Removed
- mapping for CentOS 8.4
- default `/plans` from the `-p/--plans` argument
- copr-cli section from config file

## [2022.11.11]
### Added
  - request response watcher
    - check if the artifact url is sending a 200 response code, if not, notify the user after 30 seconds
### Changed
  - `centos-8` and `oraclelinux-8` distro context changed to `centos-8-latest` and `oraclelinux-8.6` respectively
    - differentiate better the provisioned machine
### Removed
  - Oracle Linux 8.4 disabled as a part of default composes to be tested on
## [2022.08.19]
### Added
- check if the repo url is correct in case of gitlab.cee.redhat
- `--debug` argument and move redundant links to debug
- `--dry-run` argument to get just the payload printed
- `--dry-run-cli` argument to get https command with required payload printed
- pass task ID as a reference to a brew build directly
  - fixes heavy dependency on NVR working correctly
- pass copr build ID directly
  - fixes heavy dependency on NEVRA working correctly
- pass multiple build references
  - PR reference (e.g. PR123, pr123)
  - copr build ID's
  - package release version (e.g. 0.1-2)
  - brew build task ID's

### Changed
- hardcode copr API configuration - discard from config file
- pass git references `[git_base_url repository_owner branch]` under one argument
- change `-git/--git_url` argument to `-g/--git`
  - `-g/--git` is required with default option `[github oamg main]`
- simplify the outputted test links to just test results
- make epel_composes in brew_api load dynamically from COMPOSE_MAPPING
  - previously hardcoded approach was naive as it required changes to epel_composes mapping, whenever COMPOSES_MAPPING keys were changed

### Removed
- branch argument
- copr API configuration from configuration file altogether
  - remove copr login, copr api token and copr username from requirements and configfile as it is not needed for querying the build ID
---

---
### Previously introduced changes
#### [DISCLAIMER]
As the tool was previously mostly used by a very limited number of users (read me), there was no proper changelog included.<br>
Provided below is a timeline with some more or less notable functional changes made over the tool's short life with their respective date of introduction.
Proper versioning and changelog starts with `v2022.08.19`

#### [2022-07-20]
`commit 0565756264c2c8938a82963987bbaf00619b5e4f`
- Bump OracleLinux to 8.6, code cleanup
  - Bump version of OracleLinux requested on testing farm to 8.6
  - Cleanup code in tf_send_request
  - Add FormatText class

#### [2022-07-18]
`commit 0be97f427e91d200d0fc3e159a8d60d4f6c1ea68`
- Add log, minor fixes
  - Add possibility to log outputted links in a file.
  - In cases of many individual plans and many composes run the outputted cli is getting messy with multiple links being outputted
  - Log links into a file

#### [2022-06-30]
`commit 7a57594dd8044f131195c2601ff7157a59cbabd4`
- Move logger, argparser, configparser, variables
  - Move logger, argparser, configparser and variables to __init__.
  - Cleanup logger implementation.

#### [2022-06-22]
`commit 90603cdad805be2bb5f6fa56b090faa895a1fbbb`
- --reference argument required

#### [2022-06-20]
`commit 897b2946455b22a7f2aab03e4913681d8b4aad5a`
- Add working version of setup.py
- Change and rename config file

#### [2022-06-06]
`commit a8df852460cf7e21afa546a8068828e002117a39`
- Add setup.py to be able to install the package.
- Add __init__.py
- Change .config file instead of .env

`commit dc126d74c1950daafc905a07e9e45b78779211ec`
- Add -c/--compose argument
  - With this change, the possibility to specify individual compose to run tests on is implemented.
  - Previously there was the only option to run on all mapped composes

#### [2022-06-06]
`commit 01ac4b03845377dfbc43a79bb8aa28285fed57b1`
- Fix broken distro mapping
  - The tmt context distro was broken due to improper mapping, thus not filtering which tests to run properly.

#### [2022-04-28]
`commit 5520848c7a9d9187f936db162f427e791d1e8699`
- Parse arguments

#### [2022-04-25]
`commit 940b73772e2cc23169e9c3fdb22866157cac42f3`
- Add copr api
  - Get copr build ID's automatically from copr.fedorainfracloud.org by passing pull request reference

#### [2022-04-20]
`commit 8cfd16f478c8baf9b03b8e998e1bc00a01c8af57`
- Add brew API connection
  - Get task ID's from brew hub automatically by passing release ver

#### [2022-04-11]
`commit 22d39f39c93c95494e1b5984fac9964604fdfea4`
- Initial commit
- Basic functionality through changing values in `.env` file
  - Pseudo semi-automated solution
  - Test requests were sent automatically through the script though :))
