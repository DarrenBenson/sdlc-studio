# BG0655: the survivor filer reads a WITHDRAWN row as a live survivor, so a close files a High bug for a mutant the ledger says is dead

> **Status:** Open
> **Mutation-survivor-run:** RUN-01M1YK70
> **Mutation-survivor:** US0818-4124f2e32130f7e4
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Created:** 2026-09-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`transition.py` `_survivor_records` selects a ledger row on its verdict alone - `mu.get("verdict") == "survived"` - with no test for the `withdrawn` mark every other reader applies. A row that was recorded survived, withdrawn with a reason and then re-registered killed is therefore read as a live survivor, and the close files a High bug naming a mutant the ledger says is dead.

This artefact is that false positive, kept and retitled rather than deleted: the run's close filed it against US0818 AC2 r4 at `mutation.py:2173`, where the ledger holds the survived row withdrawn and the killed row live. A false High is not harmless - the v5.1 bar is zero open High, so an over-reporting filer holds a release on evidence that does not exist.

## Steps to Reproduce

1. Apply `print the CALLER's line rather than the live row's, so the remedy names a row retract cannot find` at .claude/skills/sdlc-studio/scripts/mutation.py:2173. 2. Run pytest .claude/skills/sdlc-studio/scripts/tests/`test_mutation.py`::RegisterReplacesTests::`test_a_disagreeing_verdict_or_test_is_refused_naming_retract.` 3. It stays green.

## Proposed Fix

Add the assertion the mutant escapes, then re-register: `mutation.py register --unit US0818 --criterion AC2 --target .claude/skills/sdlc-studio/scripts/mutation.py --line 2173 --mutant '<the edit>' --test '<the command>' --verdict killed`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0818 reached a terminal status carrying a SURVIVING mutant.
- [ ] **AC2** The proposed fix lands, pinned by a test: Add the assertion the mutant escapes, then re-register: `mutation.py register --unit US0818 --criterion AC2 --target...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-08 | sdlc-studio | Filed |
