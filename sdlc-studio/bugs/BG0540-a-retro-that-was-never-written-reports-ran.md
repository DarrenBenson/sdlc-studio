# BG0540: a retro that was never written reports `ran` on the close checklist, because a missing file is graded as a structural error rather than an absence

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07, found while writing US0591's AC3, whose Given named an unwritten retro as the example of a close-window item that still gates. The fixture deleted the retro and the row returned `ran`, so the criterion could not be satisfied as written and now names the closing-review row instead. The plan review had verified the positive half - a written retro resolves RAN - and not this one.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The `retro` checklist row returns `NOT_RUN` only when `retro.validate` answers an empty dict. For a retro file that does not exist, `validate` answers a populated dict carrying the error `no retro file for <id> in sdlc-studio/retros/`, so the row takes the errors branch and returns RAN with `1 structural error(s)`.

RAN is the state that means the stage happened. So a sprint with NO RETRO AT ALL reports its retro stage as having run, and only the value cell - which a reader scans second - carries the contradiction. The row's own detail says the file is missing while its state says the stage ran.

An absence and a fault are different facts. `_ck_reconciled`, `_ck_closing_review` and `_ck_lessons` in the same table all return `NOT_RUN` for their absence case; this row is the one that does not, and it is the row for the artefact the close exists to produce.

## Steps to Reproduce

1. Build a close fixture with no file under `sdlc-studio/retros/`. 2. Resolve the checklist. 3. The `retro` row reads `state: ran`, `value: 1 structural error(s)`, `detail: no retro file for RETRO9100 ...`. 4. It is absent from `outstanding`, so the close is not held by a missing retro.

## Proposed Fix

Return `NOT_RUN` when the retro file cannot be found at all, keeping RAN-with-errors for a retro that exists and is malformed - the distinction the other rows in the table already draw. `retro.validate` already reports the two cases differently in its error text; the row needs to read that rather than counting errors.

Both directions need a test. A missing retro must hold the close, and a written, structurally complete retro must still resolve RAN - otherwise the repair trades a false pass for a gate that refuses every close.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The `retro` checklist row returns `NOT_RUN` only when `retro.validate` answers an empty dict.
- [ ] **AC2** The proposed fix lands, pinned by a test: Return `NOT_RUN` when the retro file cannot be found at all, keeping RAN-with-errors for a retro that exists and is malformed - the distinction the other rows...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
