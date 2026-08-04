# BG0501: batch add-epic and batch swap price stories at zero because they hand-roll the points reader instead of using the shared one

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Verification depth:** functional
> **Evidence:** Executed by the independent closing-review passes on US0470 and US0471 during the RUN-01KYZKY5 close.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** closing review RUN-01KYZKY5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`_swap_points` reads points with `int(extract_field(text, 'Points'))` rather than `sdlc_md.read_points`, which is documented as THE reader. Real stories in this corpus carry `**Story Points:**`, not `**Points:**`, and a decorated value such as `5 (relative)` does not parse as an int either. So `batch add-epic --epic EP0005` selects all thirteen of its stories correctly and then reports them as zero points. Both `_cmd_batch_swap` and `_cmd_batch_add_epic` price through it. Separately, both units' criteria claim the output carries 'the same capacity line' from the shared renderer, and neither command calls `_render_capacity` at all.

## Steps to Reproduce

Run `sprint.py batch add-epic --epic EP0005 --status Done` against this repo's own corpus: thirteen stories are selected and the points total reads 0.

## Proposed Fix

Route both through `sdlc_md.read_points`, and either emit the shared capacity line the criteria describe or correct the criteria to what the commands print.

## Acceptance Criteria

> **Affects widened at the plan-time goal review.** The named fix - route through the shared
> reader - does not fix the defect: `sdlc_md.read_points` reads `Points` and misses the
> `**Story Points:**` spelling too, so it returns None on the same stories. The reader itself
> must learn the second spelling, and it is shared by every size consumer in the repo, so the
> blast radius is stated rather than discovered.

- [x] **AC1: the shared reader reads both spellings.**
  - **Given** a story carrying `**Story Points:** 5` and one carrying `> **Points:** 5`
  - **When** `sdlc_md.read_points` runs over each
  - **Then** both return 5, because the reader missing a spelling is the actual defect and
    routing a second caller through a reader that cannot read it changes nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::StoryPointsSpellingTests::test_both_spellings_read_back
  - **Verified:** yes (2026-08-04)

- [x] **AC2: add-epic and swap price such a story correctly, through that reader.**
  - **Given** an epic whose stories carry the `Story Points` spelling
  - **When** `sprint.py batch add-epic` and `batch swap` compute the capacity effect
  - **Then** the total is the real points sum rather than 0, and it comes from the shared reader
    rather than a hand-rolled parse
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py::StoryPointsSpellingTests::test_add_epic_and_swap_price_through_the_shared_reader
  - **Verified:** yes (2026-08-04)

## Verification evidence

Functional. Three mutants executed, `__pycache__` purged and each child run under `python3 -B`,
anchors asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| drop the `Story Points` fallback in `read_points` | killed |
| try `Story Points` FIRST, so it beats an explicit `Points` | killed |
| restore the hand-rolled points parse in `_swap_points` | killed |

The second mutant is the one worth naming: a fallback that wins over the canonical field would
silently change what an existing artefact means, so the ORDER is pinned, not just the lookup.

**The filed fix would not have fixed the filed defect.** It said to route through the shared
reader. `read_points` asked `extract_field` for `Points`, which does not match `**Story
Points:**` either, so both readers returned None on the same 20 stories and routing one through
the other would have changed nothing. That was found at the plan-time goal review by execution,
before any code was written, and the unit's `Affects` was widened to name `lib/sdlc_md.py` -
the reader shared by every size consumer in the repo - so the blast radius was stated rather
than discovered.

## Impact

A batch resized by these verbs reports a capacity delta of zero, so the appetite check they exist to inform is uninformed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
