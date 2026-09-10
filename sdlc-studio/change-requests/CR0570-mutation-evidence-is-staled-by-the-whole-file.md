# CR-0570: Mutation evidence is staled by the whole file's hash, so an edit anywhere re-measures every unit holding a row on that file

> **Status:** Complete
> **Decomposed-into:** EP0252
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Live ledger measured 2026-09-09: 78 entries, 515 live rows, 74 targets, 26 shared by more than one unit, verify_ac.py held by seven units. One commit needed four attempts and about forty minutes re-measuring six units whose sites it never touched.
> **Date:** 2026-09-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

A ledger entry is keyed by `(target, sha256 of the whole file)`. Any byte change to a target therefore invalidates EVERY row on it, including rows whose own mutation site was not touched - so editing one line of a module forces a re-measurement of every unit that ever registered evidence against it.

Measured on the live ledger: 78 entries, 515 live rows, 74 targets, and 26 of those targets carry rows from more than one unit. `verify_ac.py` holds evidence for SEVEN units; `mutation.py`, `transition.py`, `status.py` and `AGENTS.md` hold five each. A one-line edit to any of them is a seven-unit or five-unit re-measurement before the evidence-drift lane will accept the commit.

Measured in delivery on 2026-09-09: one commit took FOUR attempts and about forty minutes of re-measurement across BG0603, BG0643, BG0648, BG0653, US0815 and US0816, none of whose mutation sites the commit had touched. A single session accumulated forty hand-written re-measure runners. Two failure modes came out of that: BG0641's runner carried a hard-coded target filter and silently skipped `enable-hooks.sh` through three passes, leaving two rows stale while reporting success; and BG0616 had no runner at all, so one had to be written from the ledger rows before its file could be edited.

The row already has almost everything it needs. `mutation.py register` accepts `--anchor`, documented as `the ORIGINAL text the mutant replaced, which must occur EXACTLY ONCE in the target`, and it CHECKS that at registration - then discards it. The persisted row carries `line`, `mutant`, `test`, `verdict` and no anchor at all, so nothing on the row can answer whether its own site moved and the file hash is the only thing left to ask.

## Impact

This is the largest per-commit cost in the run that filed it, and it falls hardest on exactly the files a broad change touches. It also degrades the evidence itself: a re-measurement performed by a hand-written runner is only as good as that runner, and two of them have already been wrong in ways that reported success. Every consuming project inherits both the cost and the failure mode.

## Acceptance Criteria

- [ ] Given a row registered WITH an anchor, when an unrelated line elsewhere in the same target is edited, then the row stays LIVE and the evidence-drift lane does not demand it be re-measured
- [ ] Given the same row, when the text its anchor names is edited, then it is STALE and the lane names that row rather than the whole file
- [ ] Given a row whose anchor now occurs MORE THAN ONCE in the target, then it is STALE too - an anchor that no longer identifies one site cannot say which site the verdict was about, and treating it as live is the direction that reports a measurement nobody made
- [ ] Given a row registered with NO anchor - which is every one of the 515 rows on disk today - then it is judged by the target's content hash exactly as it is now, so widening the schema promotes nothing to live that was not live before
- [ ] Given `mutation.py register --anchor`, when the row is written, then the anchor is PERSISTED on it; and an anchor occurring other than exactly once is still refused at registration, as it is today
- [ ] Given a target holding rows from several units and an edit touching one unit's site, when the evidence-drift lane runs, then it names only the rows whose anchors moved and does not demand the others be re-measured

## Recommendation

PERSIST the anchor `register` already validates, and judge staleness per row: a row stays LIVE while its anchor still occurs exactly once in the target, and goes stale when it occurs zero times or more than once. That is the same question the runners already ask before applying a mutant, moved from forty scratch scripts into the ledger.

The safety direction is the one to get right. Zero occurrences means the site is gone; more than one means the anchor no longer identifies a site, and a mutant applied to the wrong one reports a verdict about code nobody chose. Both stale. Only the exactly-once case survives.

Every row already on disk carries no anchor, and must keep being judged by the file hash exactly as it is today - a widening that silently promoted 515 unanchored rows to live would convert this from a cost into a correctness failure, and this repository has the scar for widening a schema without testing the oldest shape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-09 | sdlc-studio | Raised |
