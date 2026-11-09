# BG1299: A commit that changes sdlc-studio/trd.md selects 2 of the test modules that read it, so a broken spec sentence is first seen by the full suite at push

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate_selection_reaches_loaders.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Push refused on test_token_premise.py at the US1138 landing, 2026-11-08; selector output above at ed79b0d9
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T00:06:49Z

## Summary

The commit-time selection (`gate.py --suite-decision`) reaches a module that is staged, is named for a staged file, imports or loads one, or names it in a `test-census-subject` header. A module that reads a spec document by path, such as `TRD = REPO / "sdlc-studio" / "trd.md"` in tools/tests/`test_token_premise.py`:26, is none of those. `gate.py --suite-decision --changed sdlc-studio/trd.md` selects tools/tests/`test_lean_specs_v63.py` and tools/tests/`test_lean_trd_refresh.py`, while at least ten modules under tools/tests read trd.md (`test_token_premise`, `test_adr011_agreement`, `test_availability_contract`, `test_porting_doctrine`, `test_spec_versions_tracked`, `test_check_versions`, `test_lean_spec_restatements`, `test_lean_gate_toolchain_docs`, `test_lean_trd_constraints_repo` and `test_lean_specs_v63).` Found during the 6.3.0 release: US1138 dropped a sentence from TRD section 10 and Won't Have, its commits passed, and the push gate then refused on `test_token_premise.py`, costing a repair and a second push (about 18 minutes of gate time). BG1115 is the same class for scripts reached through `surface.enumerate_scripts`.

## Steps to Reproduce

Run `python3 .claude/skills/sdlc-studio/scripts/gate.py --root . --suite-decision --changed sdlc-studio/trd.md`: 2 of 510 modules selected, `test_token_premise.py` not among them.

## Proposed Fix

Have the selection's census also read a module's repo-relative path literals for tracked documents (the spec files under sdlc-studio/ and docs/), so a module that reads a document by path is selected when it changes. Or let a module name several subjects in `test-census-subject` lines and add the header to each spec reader, with a census check refusing a module that reads a spec by path and names none.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The commit-time selection (`gate.py --suite-decision`) reaches a module that is staged, is named for a staged file, imports or loads one, or names it in a...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `python3 .claude/skills/sdlc-studio/scripts/gate.py --root .
- [ ] **AC3** The proposed fix lands, pinned by a test: Have the selection's census also read a module's repo-relative path literals for tracked documents (the spec files under sdlc-studio/ and docs/), so a module...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
