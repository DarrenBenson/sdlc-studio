# BG0623: artifact.py retitle refuses precisely the artefact that needs it, because a malformed H1 is both the defect and the thing the tool requires to work

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** Found during RUN-01M0YXN3 wave 1, 2026-08-26. BG0621's hardened bar reported BG0131 unparseable - the first live instance the new guard surfaced - and `retitle` then refused to repair it. The H1 was corrected by hand, which is the outcome this bug is about.
> **Created:** 2026-08-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`retitle` exists because a title lives in the H1, the filename slug and the index row at once, so correcting one by hand means correcting all three plus every inbound link. But it resolves the artefact through `find_by_id`, which needs the H1 to parse - so the one case where the H1 is WRONG is the one case the tool cannot help with. Hit on 2026-08-26 on BG0131, whose H1 read `# BG0131 (CORRECTED - the original claim was WRONG): ...`, putting a parenthetical between the id and the colon. `retitle --id BG0131` answered "no `# <ID>: <title>` H1 ... to rewrite". The refusal message is honest and names the remedy - add the heading, then retitle - but that remedy is the hand-edit the tool exists to replace, and it is performed on the file least likely to be noticed, since a malformed heading is exactly what makes an artefact invisible to the readers that would otherwise flag it.

## Steps to Reproduce

1. Take any artefact whose H1 does not match `# <ID>: <title>` - BG0131 was the live instance, found by the hardened release bar reporting it unparseable. 2. `artifact.py retitle --id BG0131 --title '<anything>' --dry-run`. 3. It refuses at the `h1` surface and writes nothing, leaving the hand-edit as the only route.

## Proposed Fix

Let `retitle` REPAIR an unparseable H1 rather than require a parseable one. The unit is already identified by `--id` and by the filename, so the H1 does not have to be the lookup key for a verb whose whole job is to rewrite it. A narrower option is a `--repair-heading` mode that accepts a file path instead of an id. Either way the tool should be able to fix the state it currently refuses, because that state is the one its own callers cannot fix any other way.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `retitle` exists because a title lives in the H1, the filename slug and the index row at once, so correcting one by hand means correcting all three plus every...
- [ ] **AC2** The proposed fix lands, pinned by a test: Let `retitle` REPAIR an unparseable H1 rather than require a parseable one.

## Impact

The doctrine's rule is that mechanical work goes through a tool and hand-authoring is an error. Here the tool declines exactly when hand-authoring is most dangerous: a malformed H1 makes an artefact invisible to the id-addressed readers, so the artefact that most needs a deterministic repair is the one that gets a manual one. BG0619 records the sibling shape, where a retro and a handoff cannot be addressed at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-26 | sdlc-studio | Filed |
