# BG1733: transition.py drops a status decoration such as '(partially superseded)' on every move

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** run twenty-four RFC lane hand-back (BG1569/BG1678 migration), transition.py `_set_field` near line 1487
> **Created:** 2026-11-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-23T22:53:56Z

## Summary

transition.py writes the whole new status with `_set_field(text`, 'Status', `new_status)`, so a decorated status such as 'Accepted (partially superseded)' loses its decoration when the artifact moves, although `sdlc_md.canonical_status` reads decorated statuses as a supported form. Run twenty-four's RFC migration lost RFC0009's note this way, and the builder restored it by hand.

## Steps to Reproduce

1. Give an RFC the status 'Accepted (partially superseded)'. 2. Run transition.py set --id <RFC> --status Delivered. 3. The Status line reads 'Delivered', and the note is gone.

## Proposed Fix

Carry a parenthesised decoration from the old status onto the new one unless the caller passes its own, and say so in transition's output; pin both cases in `test_transition.py.`

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: transition.py writes the whole new status with `_set_field(text`, 'Status', `new_status)`, so a decorated status such as 'Accepted (partially superseded)'...
- [ ] **AC2** The proposed fix lands, pinned by a test: Carry a parenthesised decoration from the old status onto the new one unless the caller passes its own, and say so in transition's output; pin both cases in...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-23 | sdlc-studio | Filed |
