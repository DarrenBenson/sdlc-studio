# BG0382: close_owed treats a decision-terminal status as delivery, so a unit nobody built demands a sprint close

> **Status:** Open
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/close_owed.py, .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py
> **Severity:** Medium
> **Points:** 2

## Summary

`close_owed.scan_delivery` accepts every status `sdlc_md.is_terminal_status` calls absorbing, and that set mixes two different things. `Done` and `Fixed` are reached by DELIVERING; `Won't Implement`, `Won't Fix`, `Duplicate` and `Superseded` are reached by DECIDING. A close-down accounts for what a sprint delivered, so only the first kind can owe one.

US0483 is the live case. It reached `Won't Implement` on 2026-07-27 - a ruling, not a build - and it is now the sole entry in the close-owed advisory, asking for a retro to account for work that never happened. There is no retro that could honestly cover it and no sprint that delivered it.

## Steps to Reproduce

1. Take a project with a stamped close-owed baseline.
2. Rule a story `Won't Implement` (no delivery, no run).
3. `close_owed.py detect` lists it as owing a sprint close.

## Proposed Fix

Split the terminal set at the point of use. `close_owed` should account for DELIVERED-terminal statuses only, and treat decision-terminal ones as out of population rather than as covered - a unit that was never built is not a unit some retro forgot. Derive the split from the type vocabularies rather than hard-coding a list, or the next status added to a vocabulary is silently in the wrong half (LL0013).

## Acceptance Criteria

- [ ] A delivery unit at a decision-terminal status is not counted as owing a sprint close.
- [ ] A delivery unit at a delivered-terminal status still owes one, pinned by a test asserting both halves against the same fixture - so the carve-out cannot be widened into a blanket exemption.
- [ ] The split is derived from the status vocabularies rather than enumerated, and a test adds a new decision-terminal status to a vocabulary and asserts it lands on the correct side without any edit to close_owed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Acceptance criteria back-filled. They were supplied at filing and neither creation path wrote them: `artifact.py` has no Acceptance Criteria section for a bug, and `file_finding.py` rendered the STATED ABSENCE over them. Both are repaired under BG0384; these four documents are the evidence of the defect and are restored from the fields files they were filed from, not re-invented. |
