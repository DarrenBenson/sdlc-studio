# BG0501: batch add-epic and batch swap price stories at zero because they hand-roll the points reader instead of using the shared one

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_capacity.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] add-epic and swap price a story carrying `Story Points` correctly, and the points figure comes from the shared reader.

## Impact

A batch resized by these verbs reports a capacity delta of zero, so the appetite check they exist to inform is uninformed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | closing review RUN-01KYZKY5 | Filed |
