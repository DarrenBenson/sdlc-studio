# BG0734: the blockquote skip in check_versions is unreachable, so it guards nothing

> **Status:** Open
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_versions.py, tools/tests/test_check_versions.py
> **Severity:** Medium
> **Points:** 1

## Summary

BG0463 claim 8, re-executed at HEAD on 2026-09-21. `_is_superseded` continues on a line beginning with `>`, but the regex that skip protects never matches a `>`-prefixed line in the first place - all three blockquoted Status forms return False when executed directly. The skip changes no outcome for any input, so it is either dead code or the regex is wrong, and the two readings have opposite fixes.

## Steps to Reproduce

1. Call `_is_superseded` with `> **Status:** Superseded`, `>**Status:**Superseded` and `>  **Status:** Superseded`. 2. All three return False, with and without the skip. 3. Delete the skip: the whole suite stays green.

## Proposed Fix

Decide which reading is right and pin it. If blockquoted status lines SHOULD be read, widen the regex to accept a leading `>` so the skip has an input to act on. If they should not, delete the skip. Either way add a fixture with a blockquoted Status.

## Acceptance Criteria

### AC1: the blockquote skip either guards a real input or is gone

- **Given** the three blockquoted `Status:` forms
- **When** `_is_superseded` is called on each
- **Then** the chosen reading is pinned - either the regex accepts a leading `>` so the skip has an input to act on, or the skip is deleted; a branch that changes no outcome for any input is not acceptable
- **Mutant:** in `tools/check_versions.py`, delete the `>` skip and change nothing else. The whole suite stays green, which is the proof that the branch guards nothing today
- **Verify:** pytest tools/tests/test_check_versions.py::BlockquotedStatusTests::test_a_blockquoted_status_line_takes_the_chosen_reading
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | US0853 AC2 | Minted as its own artefact so no BG0463 survivor is carried as a bullet inside another. The filer routes Low findings into a themed consolidation CR by design, so this was created through `artifact.py new` instead - not a severity inflated to dodge the mechanism, and not the mechanism switched off. BG0731 carries the conflict. |
