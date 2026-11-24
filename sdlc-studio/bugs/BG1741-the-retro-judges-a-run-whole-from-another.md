# BG1741: The retro judges a run whole from another harness's session when the closing session has no closing stamp, and drops a supplied delegated total

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** run twenty-five, BG1204 round-six qa review
> **Created:** 2026-11-24
> **Created-by:** sdlc-studio file
> **Raised-by:** Sam Eriksson (qa); persona; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-24T16:02:53Z

## Summary

When the session running the close has no closing stamp, retro.py's stamp-based judgement (the `if whole:` branch) can find every reading holding its subagents from an opencode session alone, though the closing capture is main-thread only. The basis then says 'The subagents are already in the reading, so the 1 delegated total(s) supplied are not added', and an untagged 300 is dropped from the retro's figure. Present at base 3994fa77; confirmed by the qa seat through the shipped CLI in run twenty-five's BG1204 review.

## Steps to Reproduce

1. A run with a Claude closing session that has no closing stamp and an opencode session stamped includes_subagents True. 2. `retro.py accuracy --delegated-tokens 300`, then `accuracy --tokens-from-harness`. 3. The 300 is not added and the basis says the subagents are in the reading.

## Proposed Fix

Judge 'whole' from the closing capture's own reading (or require its stamp) rather than from other sessions' stamps alone, and pin the no-closing-stamp case.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: When the session running the close has no closing stamp, retro.py's stamp-based judgement (the `if whole:` branch) can find every reading holding its subagents...
- [ ] **AC2** The proposed fix lands, pinned by a test: Judge 'whole' from the closing capture's own reading (or require its stamp) rather than from other sessions' stamps alone, and pin the no-closing-stamp case.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-24 | Sam Eriksson (qa) | Filed |
