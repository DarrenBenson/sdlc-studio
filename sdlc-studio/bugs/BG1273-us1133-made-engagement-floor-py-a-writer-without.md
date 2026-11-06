# BG1273: US1133 made engagement_floor.py a writer without a confinement case or allowlist entry, so the push gate's roster sweep is red

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_confinement.py
> **Evidence:** run eight (RUN-01M6RZQZ) push of e0a060bc, refused at the push boundary by devserver1's full suite
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:45:10Z

## Summary

The push of e0a060bc was refused by the full suite on devserver1 (1 failed, 8644 passed): `test_confinement.py::ConfinementRosterSweepTests::test_every_writer_is_covered_or_allowlisted` lists `engagement_floor.py`, which US1133's `--write-trailers` turned into a writer. It writes only the commit-message file git hands the commit-msg hook, never a workspace artefact, but the roster names neither a case nor a reason.

## Steps to Reproduce

Run `python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::ConfinementRosterSweepTests -q` at e0a060bc.

## Proposed Fix

Add `engagement_floor.py` to `CONFINEMENT_ALLOWLIST` with the reason: it writes only the commit-message file it is handed, pinned by the commit-msg hook tests.

## Acceptance Criteria

- [ ] **AC1** Every script that writes to the workspace has a confinement case or an allowlist entry saying why, `engagement_floor.py` included, and the allowlist holds no stale entry.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_confinement.py::ConfinementRosterSweepTests
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored for run eight |
