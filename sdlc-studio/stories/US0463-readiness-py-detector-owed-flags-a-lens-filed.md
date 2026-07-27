# US0463: readiness.py detector-owed flags a lens filed in two separate audit runs and files the sized unit that will build the check

> **Status:** Ready
> **Delivers:** CR0435
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/help/audit.md, .claude/skills/sdlc-studio/reference-scripts.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 5

## User Story

**As an** operator closing out an adversarial audit
**I want** the run's survivors compared against what earlier runs filed, the recurring lenses named, and a delivery unit minted for each
**So that** a judgement the model has now paid for twice becomes a scheduled script instead of being re-derived every run

## Acceptance Criteria

### AC1: AC1: a lens filed under two distinct runs is detector-owed and the report exits non-zero

- **Given** findings attributed to one lens under two registered run ids, and a second workspace with no such lens
- **When** `readiness.py detector-owed --format json` runs over each
- **Then** the owed workspace names the lens, both run ids, both filed findings and the pack's own manual rationale for why no search singles the class out, and exits non-zero while the clean one exits zero with the same verdicts in the JSON, so a close-out lane can refuse a run that leaves a class unconverted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py::DetectorOwedTests::test_a_lens_filed_in_two_runs_is_owed_and_the_exit_code_and_json_agree

### AC2: AC2: repeats inside one run are not detector-owed

- **Given** five findings attributed to one lens, all from a single registered run
- **When** the report runs
- **Then** the lens is not detector-owed, because the rule is survival across runs and not volume within one - a run finding a class five times is the lens working
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py::DetectorOwedTests::test_repeats_inside_one_run_are_not_owed

### AC3: AC3: a recurring lens whose signature is already mechanical is detector-exists

- **Given** a lens recurring across two runs whose pack signature parses as mechanical
- **When** the report runs
- **Then** it is listed detector-exists with the command finders should run and skip on, not detector-owed, so an existing script is never re-commissioned
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py::DetectorOwedTests::test_a_mechanical_signature_reports_detector_exists

### AC4: AC4: findings it cannot classify are named, never treated as nothing owed

- **Given** a workspace holding findings with no lens attribution, including backfilled ones whose lens is explicitly unknown
- **When** the report runs
- **Then** it names and counts them and exits in a distinct cannot-judge state separate from both owed and clean, so a workspace it could not read is never reported as having nothing owed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py::DetectorOwedTests::test_unattributed_findings_are_named_not_counted_as_clean

### AC5: AC5: each owed class gets exactly one sized delivery unit, filed not described

- **Given** a detector-owed lens, run twice: once with nothing filed against it, once when a unit already exists
- **When** `readiness.py detector-owed --file` runs
- **Then** the first run mints one sized CR through `file_finding.py` naming the lens, both runs and both findings as the evidence the check must catch, and the second run reports the existing unit and mints nothing, so CR0435's third criterion is delivered without filing the same unit every close-out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_detector_owed.py::DetectorOwedFilingTests::test_an_owed_class_is_filed_once_and_never_twice

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
