# BG0590: sprint close appends a handoff bullet that fails the repo's own markdown lane

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The close writes a `## Handoff` section into the retro using a dash bullet, regardless of the list style the rest of that document uses. Where the retro was scaffolded with asterisk bullets - which is what `artifact.py new` produces and what every retro in this repository carries - markdownlint's MD004 refuses the file, so the very next commit is BLOCKED by the tool's own output. The close succeeds and then makes the tree uncommittable, which is the worst ordering: the operator has already been told the run closed.

## Steps to Reproduce

Reproduced 2026-08-17 on RUN-01M05A5M at 4766cfe3. `sprint.py close --retro RETRO0103` exits 0 and appends to the retro: `- [HO-0059](../handoffs/HO0059-....md) - 12 remaining item(s)`. The following `git commit` is refused by the markdown lane: `RETRO0103-...md:257:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]`. Fixed by hand to an asterisk for that commit; the writer is unchanged.

## Proposed Fix

Read the document's established list style before appending, or - simpler and with fewer ways to be wrong - have the close write the handoff line through the same helper that scaffolds the retro, so one module owns the bullet. Whichever is chosen, pin it with a test that appends to a retro carrying asterisk bullets and runs the markdown lane over the result, because a test asserting the string naming a dash and HO- would pass on the defect. Check the other close-time appenders for the same assumption before assuming the handoff line is the only one.

## Acceptance Criteria

- [ ] **AC1** Given a retro whose lists use asterisk bullets, when the close appends its handoff section, then markdownlint reports no MD004 error for that file
- [ ] **AC2** Given a retro whose lists use dash bullets, when the close appends, then markdownlint reports no MD004 error either - the fix must follow the document, not swap one hardcoded bullet for another

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
