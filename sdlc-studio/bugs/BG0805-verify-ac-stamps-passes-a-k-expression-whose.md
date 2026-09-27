# BG0805: verify_ac stamps passes a -k expression whose dead term hides behind a live one, so eight stamped criteria verify nothing of what they claim

> **Status:** Open
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_k_terms.py, sdlc-studio/stories/US0062-evidence-as-schema-per-type-required-evidence-lint.md, sdlc-studio/stories/US0077-route-github-sync-and-verify-ac-through-shared.md, sdlc-studio/stories/US0081-batch-scaffold-wiring-polish.md, sdlc-studio/bugs/BG0264-verify-ac-lint-accepts-a-grep-or-file.md, sdlc-studio/bugs/BG0555-twelve-scripts-declare-root-only-per-subcommand-a.md, changelog.d/BG0805.md
> **Severity:** Medium
> **Points:** 2

## Summary

CR0592 bullet (file line 46) re-measured at f76b70cc and wider than filed: `verify_ac.py stamps --bugs` reads 'every stamped verifier still resolves' while 8 `-k` terms each collect 0 tests (US0062 x2, US0077, US0081, BG0264 x3, BG0555). Example: US0081 AC1's `-k "batch_wires or batch_creates_wires or batch_defaults_to_full_template"` collects 2 tests; the third term, renamed by BG0755, collects none, so the template claim is unverified. The release bar's '`verify_ac` stamps clean' is met vacuously for these five artefacts.

## Steps to Reproduce

pytest --collect-only .claude/skills/sdlc-studio/scripts/tests/`test_artifact.py` -k `batch_defaults_to_full_template`: no tests collected; `verify_ac.py` stamps --bugs: exit 0.

## Proposed Fix

Resolve each `or`-joined term of a stamped -k expression separately and name a dead one; repoint or retire the 8 terms in the same commit.

## Acceptance Criteria

- [ ] **AC1** Given a stamped Verify line `pytest <file> -k "a or b"` where `b` selects no test in `<file>` and `a` selects one, when `verify_ac stamps` runs, then it names the criterion and the dead term and exits non-zero. Fails on: resolving the expression as a whole, so a live term hides the dead one (HEAD)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_k_terms.py::StampsKTermTests::test_a_dead_k_term_is_named
- [ ] **AC2** Given this repository, when `verify_ac stamps --bugs` runs, then it exits 0 and none of the 8 dead terms remains: each is repointed to the test that replaced it or retired in the D0259 pattern. Fails on: HEAD, 8 terms selecting nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_stamps_k_terms.py::StampsKTermTests::test_the_repository_carries_no_dead_k_term

## Notes

Release-bar blocker: without it 'verify_ac stamps clean' is a vacuous green. Strengthens an existing check (LC-008 neutral). Mint from CR0592 and remove the bullet. The QA seat re-confirmed the US0081 term by collection.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0805) |
