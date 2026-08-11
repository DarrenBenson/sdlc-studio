# US0635: The thirteen story-side duplicate Verify groups are split into discriminating selectors

> **Status:** Done
> **Delivers:** CR0445
> **Supersedes:** US0482
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories, sdlc-studio/.verify-lint-baseline.json, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Depends on:** BG0530
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader taking a Done story's evidence as proof of the criterion beside it
**I want** each acceptance criterion in a story to name a selector no sibling criterion shares
**So that** a green stamp means that criterion was checked, not that some criterion in the story was

## Notes

Split from US0482, which was at the 8-point ceiling. This is the story-side half of the
burn-down; US0636 is the bug-side half and closes the baseline out; US0637 is the reporting
change that was US0482's AC2.

Measured at split time with `verify_ac.duplicate_verifiers` over the live tree: **13
intra-record groups across 13 story records** - US0025, US0111, US0113, US0114, US0123,
US0124, US0166, US0167, US0170, US0247, US0266, US0268, US0392. Nine are whole-file
selectors (`unittest discover -p test_x.py`, `pytest ... -k`), which is how one run comes to
stand as evidence for criteria it never separately exercised.

Those figures are context for the size, not the pass condition. Every criterion below is
satisfied by running the resolver over the workspace and finding nothing left, so a group
added or paid down between grooming and delivery does not make the story wrong.

Splitting a whole-file selector sometimes needs a named test that does not exist yet. Write
it rather than narrowing the selector to a `-k` expression that still matches several
criteria - a selector that discriminates by accident is the debt this pays down.

## Acceptance Criteria

### AC1: no intra-record duplicate group remains in a story

- **Given** the duplicate groups confined within a single record under `sdlc-studio/stories`
- **When** `verify_ac.py lint --ratchet` runs over the workspace, deriving the set from the
  resolver at lint time rather than from any count recorded in prose
- **Then** it reports no intra-record duplicate group in that directory, each having been
  split into a per-criterion selector that RESOLVES - `selector_resolves` answers True, not
  None and not False - because uniqueness alone is met by appending junk that collects nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_no_intra_record_group_remains_in_stories
- **Verified:** yes (2026-08-07)

### AC2: the baseline no longer carries the story-side entries, and only shrank

- **Given** `sdlc-studio/.verify-lint-baseline.json`, which records the pre-existing groups so
  the ratchet can be enforced from there and whose set may only shrink
- **When** the burn-down lands
- **Then** no intra-record story-side group remains listed, and no entry has been added -
  compared against the file at this story's base ref, so the direction is proven rather than
  asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_the_story_side_baseline_entries_are_gone_and_none_were_added
- **Verified:** yes (2026-08-07)

### AC3: emptying the story side did not disarm the guard

- **Given** a story introducing a fresh duplicate group, added after the burn-down
- **When** the ratchet runs
- **Then** it refuses, proving the entries were removed by splitting the selectors rather than
  by weakening the check that protects them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_a_fresh_duplicate_in_a_story_is_still_refused
- **Verified:** yes (2026-08-07)

## Test-plan notes

Written after a plan review rejected the first draft. Six conditions, each of which is what
stops a planned test from passing over a burn-down that burned nothing down:

1. **Uniqueness is not the bar; resolvability is.** `duplicate_verifiers` groups byte-identical
   normalised commands, so appending distinct junk node ids empties the intra-record set, the
   baseline entries then go stale and are removed, and all three criteria pass over thirteen
   selectors that collect no tests. AC1 now demands `selector_resolves is True`.
2. **The assertion is over the resolver's intra-record subset for `sdlc-studio/stories`**, never
   over `lint --ratchet`'s exit code. That verdict is red today for reasons outside this unit -
   23 stale entries appear only when bugs are scanned - so a test pinned to it can never go
   green from this unit's work, and one pinned to it loosely goes green for the wrong reason.
3. **Prove the scan is live before asserting it is empty.** `selector_resolves` answers None
   when the runner is absent from PATH, so on a machine without pytest every group is
   unanswerable and "nothing remains" is green over an empty set. The test asserts a non-zero
   record count and that a known cross-record group is still seen.
4. **The four `shell ... unittest discover` groups are in scope, not excluded.** They are the
   unanswerable class, and leaving them makes the burn-down nine rather than thirteen. They are
   rewritten into collectable pytest node ids.
5. **The baseline comparison is pinned to committed state**, not to `run_state.base_ref`, which
   reads an untracked run-local file and answers empty once the run closes - a permanent suite
   test cannot keep an oracle that disappears. The thirteen keys expected gone are literals, and
   the test asserts the base side parsed non-empty before comparing.
6. **AC3 runs `dup_ratchet` over the LIVE story paths plus one fixture record**, which is what
   makes the shipped baseline the mutant surface. Every existing ratchet test builds an isolated
   tmp root with its own baseline, and against those, editing the shipped file changes nothing.
   The assertion names the fixture's own selector in `verdict["new"]`: `dup_ratchet` answers not-
   ok for at least five distinct reasons, so a bare `assertFalse(ok)` passes for the wrong one -
   and `dup_ratchet` returns every live group as `new` for the `not-baselined` and
   `corrupt` states, so the test asserts `state == "ok"` alongside, with the same live paths
   minus the fixture as its control.

Re-pointing these Verify lines invalidates the recorded AC fingerprint on thirteen mostly-Done
stories. The burn-down re-verifies each split criterion rather than leaving a `**Verified:**`
stamp standing for a selector that was never run.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change one split criterion under sdlc-studio/stories to a node id that collects nothing, so the group is unique and vacuous | no intra-record duplicate group remains in a story |
| AC2 | widen sdlc-studio/.verify-lint-baseline.json with a newly created group instead of splitting it, so the recorded set grew | the baseline no longer carries the story-side entries, and only shrank |
| AC3 | widen sdlc-studio/.verify-lint-baseline.json with the fixture's shared selector, so the ratchet forgives a group introduced after the burn-down | emptying the story side did not disarm the guard |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Split from US0482 (8 points, over the ceiling): the story-side burn-down, groomed against the resolver's measurement of the live tree |
