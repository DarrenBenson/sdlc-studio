# BG0875: US0974 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Closed with findings in:** US0974's discharge: its rejecting reviewer's APPROVE answered every finding (RUN-01M3VF2J critic-verdicts)
> **Discharge review 1:** REJECT by the rejecting reviewer (2026-10-01): a failed step was reported as writing nothing after writing, and the unreadable file was not named; answered in b7afec00
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/project_upgrade.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/migrate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py, changelog.d/US0974.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_project_upgrade.py, .claude/skills/sdlc-studio/scripts/tests/test_conformance.py, .claude/skills/sdlc-studio/scripts/tests/test_migrate.py
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T16:04:03Z

## Summary

US0974 was rejected at round 2, the review cap, by qa-seat reviewer (subagent a855eb81), so it was carried as a known issue rather than reviewed again. The findings still open: [regression] the repair dropped persona files from the readability probe: a non-UTF-8 sdlc-studio/personas/maya.md was named unreadable at 6ee67c56 and at d6b386e8 exits 1 with a UnicodeDecodeError traceback from project\_upgrade.py:438 -> :232 \_old\_persona\_signals, because \_sweep\_inputs (migrate.py:542-555) lists no persona or seat cards; [new] the \_sweep\_inputs docstring (migrate.py:547-548) says instructions files are read through readers that tolerate an unreadable file, false: a non-UTF-8 AGENTS.md or CLAUDE.md crashes via validate.py:1101 check\_instructions and .version crashes via project\_upgrade.py:143 \_read\_version - the crashes predate the unit, the false claim is new; [regression] MOVED, not closed: the meta files the probe now adds (reviews RVxxxx, retros RETROxxxx) are opened by no sweep step yet still halt --apply - rm .config.yaml and corrupt RV0001: base applies and creates the config, d6b386e8 applies nothing - and migrate.py:543-544 claims the steps read them; [new] no test covers the META\_TYPES half of \_sweep\_inputs (dropping \_meta\_files at migrate.py:553 survives); [pre-existing] BG0872 open; [pre-existing] engagement\_floor, provenance and sprint.py:413 cutoffs still refuse a ULID (declared); [pre-existing] 6 environmental failures identical at base

## Steps to Reproduce

1. Read the round 2 REJECT of US0974 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0974 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] the repair dropped persona files from the readability probe: a non-UTF-8 sdlc-studio/personas/maya.md was named unreadable at 6ee67c56 and at d6b386e8 exits 1 with a UnicodeDecodeError traceback from project\_upgrade.py:438 -> :232 \_old\_persona\_signals, because \_sweep\_inputs (migrate.py:542-555) lists no persona or seat cards
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] the \_sweep\_inputs docstring (migrate.py:547-548) says instructions files are read through readers that tolerate an unreadable file, false: a non-UTF-8 AGENTS.md or CLAUDE.md crashes via validate.py:1101 check\_instructions and .version crashes via project\_upgrade.py:143 \_read\_version - the crashes predate the unit, the false claim is new
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** The round 2 REJECT finding no longer holds: [regression] MOVED, not closed: the meta files the probe now adds (reviews RVxxxx, retros RETROxxxx) are opened by no sweep step yet still halt --apply - rm .config.yaml and corrupt RV0001: base applies and creates the config, d6b386e8 applies nothing - and migrate.py:543-544 claims the steps read them
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC4** The round 2 REJECT finding no longer holds: [new] no test covers the META\_TYPES half of \_sweep\_inputs (dropping \_meta\_files at migrate.py:553 survives)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC5** The round 2 REJECT finding no longer holds: [pre-existing] BG0872 open
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC6** The round 2 REJECT finding no longer holds: [pre-existing] engagement\_floor, provenance and sprint.py:413 cutoffs still refuse a ULID (declared)
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC7** The round 2 REJECT finding no longer holds: [pre-existing] 6 environmental failures identical at base
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC8** US0974 AC1 still passes: Given a schema v3 fixture whose config sets `conformance.adopt_after: BG-01KX95QP`, when `conformance.py check --root <fixture>` runs, then it raises no `ValueError` and exempts a unit whose ULID sorts at or before the cutoff. Fails on: HEAD `parse_cutoff('BG-01KX95QP')` raises `ValueError`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_a_ulid_cutoff_is_accepted
  - **Verified:** yes (2026-10-01)
- [ ] **AC9** US0974 AC2 still passes: Given an up-to-date fixture with no `sdlc-studio/retros/`, when `migrate.py --root <fixture>` runs, then the missing directory is not listed under needs-a-human. Fails on: HEAD lists `no retros dir(s) - created when you first use them` there
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_an_unused_standard_dir_needs_no_human
  - **Verified:** yes (2026-10-01)
- [ ] **AC10** US0974 AC3 still passes: Given a story file holding non-UTF-8 bytes, when `migrate.py --format json --root <fixture>` runs, then stdout parses as JSON naming that file as unreadable and no traceback is printed. Fails on: HEAD exits 1 with `UnicodeDecodeError` and empty stdout (premise)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v5_upgrade_clean.py::V5UpgradeCleanTests::test_an_unreadable_story_is_named_in_the_json
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
