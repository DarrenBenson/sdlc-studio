# US0461: verify_ac lint --ratchet refuses a duplicate group the baseline does not record with a reason, and the pinned pre-commit lane set gains it

> **Status:** Ready
> **Delivers:** CR0433
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, sdlc-studio/.verify-lint-baseline.json, .githooks/pre-commit, tools/tests/test_precommit_lane_order.py, .claude/skills/sdlc-studio/help/verify.md, .claude/skills/sdlc-studio/reference-scripts.md, CHANGELOG.md
> **Epic:** EP0169
> **Points:** 5

## User Story

**As an** engineer committing a groomed story or bug
**I want** a duplicate Verify selector refused at commit time unless the baseline records it with a stated reason
**So that** the advisory count stops drifting upward and a shared selector has to be argued for rather than absorbed

## Notes

**US0480** (CR0443) ratchets validate's `affects-undeclared`, `affects-unresolvable` and
`pseudo-verify` warnings and follows this story's design: a baseline recording each
tolerated instance by identity with a stated reason, compared as a SET, and wired into a
blocking lane. Separate baseline file, same entry schema and the same
not-baselined / corrupt / stale / reasonless states. Whichever lands second should reuse
the machinery rather than build a second shape of ratchet.

## Acceptance Criteria

### AC1: AC1: an unbaselined duplicate group refuses, over stories AND bugs

- **Given** a workspace whose baseline records the tolerated groups, and a story and a bug each introducing a shared selector the baseline does not hold
- **When** `verify_ac.py lint --ratchet --bugs` runs
- **Then** each refuses non-zero naming the shared command and every AC claiming it, a recorded group passes silently, and the scan covers `sdlc-studio/bugs` as `stamps --bugs` already does, so a shared selector cannot be parked in a bug where `duplicate_verifiers` never looked
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RatchetTests::test_an_unbaselined_duplicate_refuses_across_stories_and_bugs

### AC2: AC2: a swap that keeps the total flat is still refused

- **Given** a baselined group that has been split and a brand new shared selector introduced in the same change, so the number of duplicate groups is unchanged
- **When** the ratchet runs
- **Then** the new group is refused on its own identity, because the comparison is over the SET of groups and not a count, so the guard a rising total would have passed does not pass here
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RatchetTests::test_a_swap_that_keeps_the_count_flat_is_still_refused

### AC3: AC3: a baseline it cannot trust never reports clean

- **Given** three workspaces: one with no baseline file, one whose baseline is unreadable, and one recording a group whose ACs no longer share a selector
- **When** the ratchet runs over each
- **Then** each exits non-zero in a distinct not-baselined / corrupt / stale state naming the offending entries and the command to restamp, so the tolerated set only ever shrinks and a fixed group cannot be spent again to admit a new one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RatchetTests::test_no_untrustworthy_baseline_reports_clean

### AC4: AC4: an entry cannot silence the ratchet without a reason that resolves

- **Given** candidate baseline entries: one with an empty reason, one naming an AC id no artefact in the workspace holds, and one covering more ACs than the recorded cap
- **When** the entry is validated, and separately when `lint --ratchet --stamp` is asked to write it
- **Then** each is refused by `verify_ac.py` itself rather than accepted, and `--stamp` will not mint an entry with no reason, so the exemption field is machinery in this story and not an assumption made by a later one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::BaselineSchemaTests::test_a_reasonless_unresolvable_or_oversized_entry_is_refused

### AC5: AC5: the lane blocks a real commit and the pinned lane set names it

- **Given** a temp clone with the shipped hooks enabled and a staged story introducing an unrecorded shared selector
- **When** `git commit` is run for real
- **Then** the commit is refused by the named ratchet lane with the tree unchanged, and `EXPECTED_LANES` in `tools/tests/test_precommit_lane_order.py` carries the new key among the cheap lanes, so `test_no_lane_is_lost_in_the_reorder` stays green on the commit that lands this
- **Verify:** pytest tools/tests/test_precommit_lane_order.py::LaneOrderTests::test_no_lane_is_lost_in_the_reorder

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: authored from the reviewed breakdown (two adversarial rounds), scope capped to the request per D0069 |
| 2026-07-28 | Claude Opus 5 (BG0345) | Notes now name US0480 as the paired ratchet, so the shared design is visible from either story |
