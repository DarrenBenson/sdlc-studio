# BG0970: `critic.py brief` says nothing when the unit's Affects carry uncommitted changes, though it sends the reviewer to an isolated worktree that cannot see them

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_brief_uncommitted_affects.py, changelog.d/BG0970.md
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. BG0955's first brief.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:09Z

## Summary

The brief tells the reviewer to mutate in an ISOLATED CHECKOUT, and in Claude Code that is a worktree made from HEAD. If the author has not committed the unit's change, the worktree holds the code before it, and the reviewer reviews the wrong revision without any sign of it: a review that approves code it never saw. `critic.py brief --unit BG0955` printed a full brief on 2026-10-06 while the fix it covered was uncommitted; the author caught it only by noticing, and committed before dispatching. `mutation.py run` already refuses uncommitted changes to protect the author; the brief has no equivalent.

## Steps to Reproduce

Change a file in a unit's Affects without committing; run `critic.py brief --unit <id> --seat qa`; it prints the brief and its fingerprint with no warning.

## Proposed Fix

When any Affects path has uncommitted changes, `critic.py brief` warns on stderr naming the paths and saying a worktree reviewer will not see them, or refuses unless the caller confirms; the brief's fingerprint records the commit it was cut at.

## Acceptance Criteria

- [ ] **AC1** `critic.py brief` on a unit whose Affects hold uncommitted changes names those paths on stderr and says an isolated reviewer will not see them
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_uncommitted_affects.py -k brief_warns_on_uncommitted_affects
- [ ] **AC2** A brief over a clean tree prints no such warning
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_uncommitted_affects.py -k brief_on_a_clean_tree_is_silent
- [ ] **AC3** The brief records the commit it was cut at, so a verdict can be matched to the revision it judged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_brief_uncommitted_affects.py -k brief_records_its_commit

## Related

- BG0982: the brief also says nothing about files the unit changed outside its Affects. Both are the brief showing the reviewer a surface that is not the change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
