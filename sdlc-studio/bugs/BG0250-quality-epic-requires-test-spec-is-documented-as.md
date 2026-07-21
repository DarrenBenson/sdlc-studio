# BG0250: quality.epic_requires_test_spec is documented as the caller's opt-out but is read by no Python code in the tree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/reference-config.md
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found while fixing BG0241. `epic_test_spec_check`'s docstring names `quality.epic_requires_test_spec` as the lever a caller uses to opt out of the hard epic-scope test-spec requirement, and AGENTS.md describes the gate as configurable in the same terms. A grep across the tree finds the key read by NO Python code. So either the gate cannot be turned off at all while the documentation says it can, or it is enforced somewhere that does not consult the key - and in both cases a consuming project setting it in good faith gets no effect and no warning. This is the project's own recurring defect class stated exactly: prose asserting a property the code does not have, which has been the surviving MAJOR in four consecutive closing reviews. It matters more now than it would have last month, because BG0241 has just made epic-ts FAIL for an epic whose only spec asserts no coverage, and the measured migration cost is 30 of 178 specs across the workspaces on this machine. Any project reaching for the documented opt-out to stage that migration will find it does nothing.

## Steps to Reproduce

1. Read the docstring of `epic_test_spec_check` in `verify_ac.py`, which names `quality.epic_requires_test_spec` as the caller's opt-out. 2. Search the tree for that key in Python source. Observed: no read site. 3. Set the key false in a project's sdlc-studio/.config.yaml and run the epic-ts check. Observed: behaviour is unchanged and nothing reports that the setting was ignored.

## Proposed Fix

Establish first which is true - the key is unimplemented, or it is implemented under another name - because the remedy differs and guessing produces a second false claim. If unimplemented, either wire it where the docstring says it is read, or delete the promise from the docstring and from any consuming-facing documentation; a documented lever that does nothing is worse than no lever, because it is acted on. If it is read under another name, reconcile the two. Whichever it is, add a test that sets the key and asserts the behaviour actually changes, so the documentation and the code cannot drift apart again silently. Consider a broader sweep for config keys named in prose and read by nothing - this one was found by accident.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
