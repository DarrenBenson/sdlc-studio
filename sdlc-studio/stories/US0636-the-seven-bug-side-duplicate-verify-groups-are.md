# US0636: The seven bug-side duplicate Verify groups are split and the baseline empties of intra-record debt

> **Status:** Ready
> **Delivers:** CR0445
> **Supersedes:** US0482
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/bugs, sdlc-studio/.verify-lint-baseline.json, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0174
> **Depends on:** BG0530, US0635
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader taking a Fixed bug's evidence as proof of the criterion beside it
**I want** a bug's criteria held to the same discriminating-selector rule as a story's
**So that** a shared selector cannot be parked in a bug, where the burn-down would never look

## Notes

Split from US0482, which was at the 8-point ceiling. This is the bug-side half of the
burn-down and the unit that closes the baseline out; US0635 is the story-side half; US0637 is
the reporting change that was US0482's AC2.

Scope is bugs on purpose. The ratchet in US0461 (AC1) scans `sdlc-studio/bugs` precisely so a
shared selector cannot be parked where `duplicate_verifiers` never looked, and a stories-only
burn-down would leave the bug-side groups baselined for good.

Measured at split time with `verify_ac.duplicate_verifiers` over the live tree: **7
intra-record groups across 6 bug records** - BG0239, BG0240, BG0241, BG0242, BG0245 and
BG0251, which holds two. Every one is a whole-file `unittest discover -p` selector, the shape
that reads as green evidence for criteria it never separately exercised.

AC3 depends on US0635 having landed, and `Depends on:` now makes that hard rather than
leaving it to prose - this unit's `Affects` excludes `sdlc-studio/stories`, so if the sibling
had not landed AC3 would fail on thirteen entries this unit is not permitted to touch.

## Acceptance Criteria

### AC1: no intra-record duplicate group remains in a bug

- **Given** the duplicate groups confined within a single record under `sdlc-studio/bugs`
- **When** `verify_ac.py lint --ratchet --bugs` runs over the workspace, deriving the set from
  the resolver at lint time rather than from any count recorded in prose
- **Then** it reports no intra-record duplicate group in that directory, each having been
  split into a per-criterion selector that RESOLVES, on the same terms a story's is - because
  uniqueness alone is met by a cosmetic split that collects nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_no_intra_record_group_remains_in_bugs

### AC2: emptying the bug side did not disarm the guard

- **Given** a bug introducing a fresh duplicate group, added after the burn-down
- **When** the ratchet runs with `--bugs`
- **Then** it refuses, naming that fixture's own selector, with `verdict["state"]` still `ok` -
  and the same live paths WITHOUT the fixture answer ok, the control - proving the entries were
  removed by splitting the selectors rather than by weakening the check that protects them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_a_fresh_duplicate_in_a_bug_is_still_refused

### AC3: with both halves landed, the baseline carries no intra-record group at all

- **Given** US0635 shipped, so the story-side entries are already gone
- **When** the baseline is read after this unit lands
- **Then** it lists no intra-record group in either directory - the burn-down is complete
  rather than half-done, and what remains in the file is cross-record only
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DuplicateBurndownTests::test_the_baseline_holds_no_intra_record_group_in_either_directory

## Test-plan notes

Written after a plan review rejected the first draft. The story-side notes in US0635 apply here
in full; four things are specific to the bug side:

1. **All seven bug-side groups use the `shell` verb**, so `selector_resolves` answers None for
   every one and `cmd_lint` omits them from its duplicate-report lines entirely. A test that
   scrapes those lines is green before any work is done. The assertion is over the resolver's
   intra-record subset for `sdlc-studio/bugs`, and each split selector must resolve - which
   forces all seven onto a collectable verb rather than a narrower `discover -p`.
2. **Prove the bug scan is live.** `walk_stories(bugs)` without `prefixes=("BG",)` yields
   nothing, and this repo has already shipped that exact vacuity. The test asserts a non-zero
   bug record count and that a known cross-record group - `BG0378 AC3` with `BG0382 AC1` - is
   still seen.
3. **Two escapes cost the implementer nothing and must be closed.** `dup_group_key` folds only
   whitespace and the leading verb, so quoting a pattern or adding `-v` makes two groups of one
   and reports no duplicate at all; and `_is_manual` drops a group entirely if a criterion is
   downgraded to `Verify: manual`. Both empty the set without splitting anything.
4. **AC3's premise is now mechanised**: `Depends on` names US0635. It was carried in prose only,
   while this unit's `Affects` excludes `sdlc-studio/stories` - so if the sibling had not landed,
   AC3 would fail on thirteen entries this unit is not permitted to touch.

5. **A bare `assertFalse(ok)` is not a refusal assertion.** `dup_ratchet` returns every
   live group as `new` for the `not-baselined` and `corrupt` states, so once the fixture runs
   against the LIVE baseline - a mis-resolved root, or a baseline broken while the seven
   entries are being removed - the planned `assertIn` passes while the ratchet is holding
   nothing. AC2 therefore asserts `state == "ok"` alongside, and carries its positive control:
   the same live paths without the fixture answer ok.

Nothing here asserts the baseline only shrank; that is `tools/tests/test_baselines_only_shrink.py`,
which compares against HEAD. The reliance is deliberate rather than an omission.

One line in Notes above - that this unit is shippable whichever order the pair runs in - is now
wrong: `Depends on` makes US0635 hard. The dependency wins; the Notes line is the stale one.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | change one split criterion under sdlc-studio/bugs to a node id that collects nothing, so the group is unique and vacuous | no intra-record duplicate group remains in a bug |
| AC2 | widen sdlc-studio/.verify-lint-baseline.json with the fixture's shared selector, so the bug-side ratchet forgives a fresh group | emptying the bug side did not disarm the guard |
| AC3 | return one intra-record entry to sdlc-studio/.verify-lint-baseline.json after both halves have landed | with both halves landed, the baseline carries no intra-record group at all |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Split from US0482 (8 points, over the ceiling): the bug-side burn-down and the baseline close-out, groomed against the resolver's measurement of the live tree |
