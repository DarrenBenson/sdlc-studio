# BG1153: EXECUTES_VERIFIERS's docstring says verify_ac reads it, but verify_ac keeps its own VERIFIABLE_PREFIXES, and the TRD says an un-decomposed CR 'reaches Done'

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, changelog.d/BG1153.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** US1099 builder report, 2026-11-01, outside-the-unit items 1, 2 and 4.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T04:52:40Z

## Summary

Found by US1099's builder (2026-11-01). (1) The docstring on `sdlc_md.EXECUTES_VERIFIERS` says the runner, `verify_ac`, reads it, but `verify_ac.py` keeps its own `VERIFIABLE_PREFIXES = ("US", "BG")`, and only `test_validate.py`::`test_the_three_sites_read_one_authority` holds the two in step. The authority is therefore two copies kept equal by a test, not one value the runner reads. (2) The TRD's surviving sentence 'an un-decomposed CR reaches Done on prose alone' names the wrong terminal: a CR reaches Complete, not Done. (3) validate warns on an RFC at status Rejected because Rejected is not in the RFC terminal set (Accepted, Superseded, Withdrawn). It may be intended vocabulary; it needs a ruling.

## Steps to Reproduce

1. Read `sdlc_md.EXECUTES_VERIFIERS`'s docstring, then `grep -n VERIFIABLE_PREFIXES verify_ac.py`: a separate tuple.
2. `grep -n 'reaches Done on prose' sdlc-studio/trd.md`.
3. Give an RFC Status Rejected and run validate: it warns.

## Proposed Fix

Have `verify_ac` derive its prefixes from `sdlc_md.EXECUTES_VERIFIERS` (or correct the docstring to say a test holds the two equal), say 'Complete' in the TRD sentence, and rule on Rejected as an RFC terminal.

## Acceptance Criteria

- [ ] **AC1** `verify_ac`'s set of executable unit types is the one `sdlc_md.EXECUTES_VERIFIERS` holds, read from it, or the docstring says plainly that a test holds the two equal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py
- [ ] **AC2** The TRD names Complete as the terminal of a CR that reaches its end on prose alone.
  - **Verify:** shell ! grep -n 'un-decomposed CR reaches Done' sdlc-studio/trd.md
- [ ] **AC3** An RFC at Rejected either draws no open-request warning, or the RFC vocabulary rules why it should.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py

## Impact

A docstring and a TRD sentence state the authority and the terminal wrongly, and a Rejected RFC draws a warning nobody asked for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
