# US0462: A filed finding records the lens, profile and a resolvable audit run, and the existing corpus is backfilled from its Raised-by stamps

> **Status:** Ready
> **Delivers:** CR0435
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/readiness.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_readiness.py, .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/help/audit.md, .claude/skills/sdlc-studio/reference-scripts.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 3

## User Story

**As an** audit filer closing out a run
**I want** each finding stamped with the lens, profile and a run id that resolves against a recorded register
**So that** a class recurring across runs can be counted mechanically instead of being defeated by a typo or recognised by whoever remembers the last run

## Acceptance Criteria

### AC1: AC1: lens, profile and run are stamped as readable metadata

- **Given** `file_finding.py file --lens accepted-without-running --profile process --audit-run <recorded id>`
- **When** the finding is filed
- **Then** the artefact carries all three as metadata fields beside the existing provenance stamp, readable without parsing the `Raised-by` prose the 54 existing findings hide the run in
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_lens_profile_and_run_are_stamped_as_metadata

### AC2: AC2: a lens or profile no pack declares is refused before an id is minted

- **Given** a `--lens` name the named profile's pack does not carry, and separately a `--profile` no pack declares
- **When** filing is attempted
- **Then** each is refused by name listing what the resolver does declare, and nothing is minted - no id consumed, no index row written, matching how `check_mutation_run` refuses an unresolvable run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_an_undeclared_lens_or_profile_is_refused_before_an_id_is_minted

### AC3: AC3: an audit run the register does not hold is refused before an id is minted

- **Given** an `--audit-run` id absent from the recorded audit-run register, which the close-out writes and which mirrors `mutation.series_path`
- **When** filing is attempted
- **Then** it is refused by name pointing at the register path, and nothing is minted, so a one-character typo cannot manufacture a second distinct run id and with it a false detector-owed verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditRunRegisterTests::test_an_unregistered_run_id_is_refused_before_an_id_is_minted

### AC4: AC4: half an attribution is refused

- **Given** `--lens` supplied with no `--audit-run`, and `--audit-run` with no `--lens`
- **When** filing is attempted
- **Then** both are refused explaining that a class is counted per run, so a half-stamped finding that could never participate in the comparison is never created
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditAttributionTests::test_a_lens_without_a_run_or_a_run_without_a_lens_is_refused

### AC5: AC5: the existing corpus is backfilled so the comparison has real data on day one

- **Given** the findings already carrying wf_804ef18d, wf_9903a6e6 or wf_d141ccb5 inside their `Raised-by` line
- **When** the backfill pass runs and the register is seeded with those three runs
- **Then** each gains the run metadata field with the lens recorded as explicitly unknown where it cannot be derived, and a sweep asserts no artefact carries a run id in prose that is absent from its metadata field, so the detector-owed report is exercised against a real corpus rather than only reaching its cannot-judge state
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::AuditBackfillTests::test_no_finding_carries_a_run_id_in_prose_that_is_missing_from_metadata

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
