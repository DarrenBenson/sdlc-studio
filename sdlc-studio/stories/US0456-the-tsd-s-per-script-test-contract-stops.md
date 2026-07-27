# US0456: The TSD's per-script test contract stops being prose: a sweep of scripts and scripts/lib derives the exception list, and the shipped document is held to it

> **Status:** Ready
> **Delivers:** CR0428
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md, tools/check_script_tests.py, tools/tests/test_check_script_tests.py, package.json, .githooks/pre-commit
> **Epic:** EP0168
> **Points:** 5

## User Story

**As a** maintainer judging whether the per-script test contract is actually held
**I want** the TSD's coverage map derived from a sweep of every script and shared-library module on disk, and the sweep run in the gate
**So that** the document cannot assert the contract absolutely in two places while its own map is stale in both directions and names a rule nothing enforces

## Acceptance Criteria

### AC1: the sweep derives the module set from disk, including scripts/lib

- **Given** a fixture skill tree containing top-level modules, a `lib/` package and a `tests/` directory, where the expected partner of `<pkg>/<name>.py` is `scripts/tests/test_<name>.py`
- **When** a new module with no partner test is added at the top level, and separately under `lib/`, and the sweep runs with no edit to the sweep
- **Then** both new modules appear in the reported exception set, `tests/` modules and `lib/__init__.py` are excluded by a rule the test exercises, and no module is dropped by a `scripts/*.py`-shaped glob - the exemption-by-omission that would silently lose `lib/tiers`
- **Verify:** pytest tools/tests/test_check_script_tests.py::SweepDerivesTheModuleSet::test_new_untested_top_level_and_lib_modules_are_both_reported

### AC2: the TSD exception list becomes machine-readable and must match the sweep in both directions

- **Given** the TSD Unit coverage map's indirect-only exceptions rewritten from the current prose sentence (tsd.md:219-224) into a fenced list the checker parses, one module path per line
- **When** the checker compares that parsed list against the sweep's output over a fixture tree
- **Then** it exits non-zero when the list names a module that now has a dedicated test, and equally when a swept module without one is missing from the list, naming the offending module and the direction in each case
- **Verify:** pytest tools/tests/test_check_script_tests.py::TsdExceptionListAgreesWithTheSweep::test_the_list_and_the_sweep_disagree_in_either_direction_and_exit_non_zero

### AC3: the shipped tsd.md agrees with the shipped scripts tree

- **Given** the real repository root, not a fixture
- **When** the checker runs against it
- **Then** it exits zero, which is true only once the map names exactly the modules the sweep finds - today `carry_forward`, `triage` and `lib/tiers` - and stops listing `refine` and `lib/run_state`, whose dedicated test modules now exist; adding an untested script or editing the list reddens it
- **Verify:** pytest tools/tests/test_check_script_tests.py::TheShippedDocumentAgrees::test_the_real_tsd_map_matches_the_real_scripts_tree

### AC4: the absolute claims are refused by a denylist over the two located passages

- **Given** the two passages that state the contract as met, located by heading rather than by whole-file search: the Script tier paragraph (tsd.md:98-102) and the coverage-aspiration paragraph (tsd.md:436-440), plus a named denylist of the absolute phrasings ('Every script has a matching', 'every script and every shared-library module has a dedicated test module')
- **When** the checker extracts each passage and applies the denylist
- **Then** a denied phrase inside either extracted passage exits non-zero naming the phrase and the passage, and a renamed or absent heading exits non-zero saying which passage it could not locate rather than matching nothing and reporting clean
- **Verify:** pytest tools/tests/test_check_script_tests.py::AbsoluteClaimsAreRefused::test_a_denied_phrase_fails_and_a_renamed_heading_fails_loud

### AC5: the checker is a lane in the gate people already run

- **Given** the lint chain in package.json and the cheap-lane sequence in .githooks/pre-commit, which the existing lane-order tests already read
- **When** the guard reads both files
- **Then** `tools/check_script_tests.py` appears as a lane in each, so the checker runs on every commit rather than existing as a binary only its own fixture tests invoke; an unreadable scripts or tests directory makes that lane exit non-zero naming the directory instead of printing a zero-exception result it did not measure
- **Verify:** pytest tools/tests/test_check_script_tests.py::TheCheckerIsAGateLane::test_the_checker_is_wired_into_npm_lint_and_the_pre_commit_hook

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
