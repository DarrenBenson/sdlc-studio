# BG0867: A status transition rewrites an index row in compact style under an aligned header, so markdownlint fails the index it just synced

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_index_row_style.py, changelog.d/BG0867.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** backlog sweep 2026-10-01; sdlc-studio/test-specs/_index.md after the TS0001/TS0002 transition
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T10:03:30Z

## Summary

Found in the 2026-10-01 backlog sweep: `transition.py set --ids TS0001,TS0002 --status Complete` synced sdlc-studio/test-specs/_index.md, writing the two rows as `| ... | EP0010 | 28 | 0 | Complete |` beneath a header and separator padded to aligned column widths. markdownlint then failed MD060 (table-column-style) on the index, and the commit would have been refused; `markdownlint-cli2 --fix` repaired it. `reconcile.py apply` re-derives counts, not row format, so it does not fix it. Any padded index the transition syncs will fail the same way.

## Steps to Reproduce

On an index whose table header is padded, run `transition.py set --id <id> --status <s>`, then `npx markdownlint-cli2 <index>`: MD060 on the synced rows.

## Proposed Fix

Have the index row writer match the table's existing style (pad cells to the separator's widths when the header is padded, or re-render the whole table compact), so a synced index lints clean.

## Acceptance Criteria

- [ ] **AC1** Given an index whose table header and separator are padded to aligned widths, when `transition.py set` changes one row's status, then `markdownlint-cli2` reports no MD060 on that index. Fails on: HEAD, which writes the row compact under the padded header
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_index_row_style.py::IndexRowStyleTests::test_a_synced_row_matches_a_padded_table
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
