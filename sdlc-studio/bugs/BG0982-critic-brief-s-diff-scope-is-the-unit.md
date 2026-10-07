# BG0982: critic brief's diff scope is the unit's Affects only - files the unit changed but did not declare are invisible to the reviewer

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_undeclared_changes.py, changelog.d/BG0982.md
> **Evidence:** homelab RUN-01M4B5HP, US0185 critic brief fingerprint 3ca2252446de (before Affects was corrected), 2026-10-07
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:40:47Z

## Summary

`critic.py brief --unit US0185` built its `git diff <base> -- <paths>` from the story's Affects, which named the manifest and the two shell scripts but not the new module that does the work (utilities/fleet/drift-check.py) or its tests. The brief therefore pointed the independent reviewer at the edges of the change and away from its centre; it was caught only because the author read the brief before dispatching it. The plan already prints 'Affects contradicted by the unit's own content' for files a Verify line targets, but nothing compares Affects with the files the unit's commits actually touched, which is exactly what a reviewer needs.

## Steps to Reproduce

1. A story whose Affects omits a file its implementation creates (e.g. a new module)
2. Commit the implementation
3. critic.py brief --unit <id> --seat engineering -> the diff command lists only the Affects paths; the new module is absent and nothing warns

## Proposed Fix

In critic.py brief, also compute `git diff --name-only <run base>..HEAD` restricted to the unit's commits (or the run's commits touching the unit), and either widen the diff scope to include files changed outside Affects or print a loud 'changed but undeclared' block naming them - and suggest annotating Affects. Test with a fixture repo whose unit creates an undeclared file.

## Acceptance Criteria

- [ ] **AC1** For a unit whose commits since the run's base change a file its Affects does not declare, `critic.py brief` names that file in a 'changed but not declared' block in the brief the reviewer reads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_undeclared_changes.py -k undeclared_change_is_named
- [ ] **AC2** A unit whose changes all sit inside its Affects gets no such block
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_undeclared_changes.py -k declared_changes_print_no_block
- [ ] **AC3** The brief's diff scope stays the unit's Affects; the block informs the reviewer and suggests correcting Affects, it does not widen the bounded review
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_undeclared_changes.py -k diff_scope_stays_bounded

## Triage

- Reproduced at 8b844a80 by the code path: the brief's diff command is built from Affects alone and nothing in critic.py compares Affects with the files the unit changed. Not a regression.
- Of the two proposed fixes, warn rather than widen: AGENTS.md bounds a unit review to its declared Affects, and an undeclared file is evidence the Affects is wrong, which the reviewer should see and the author should fix.
- Related: BG0970 (the brief says nothing when Affects carry uncommitted changes). Both are the brief showing the reviewer a surface that is not the change; one fix can report both.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at 8b844a80; tool-derived criteria replaced with three executable ones, warning chosen over widening; BG0970 cross-referenced; changelog fragment added to Affects |
