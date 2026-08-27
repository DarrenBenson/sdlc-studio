# BG0632: a retro's index carries no Title column, so `retitle` would rename the file and leave the index and its inbound link pointing at the old name with the dry-run passing

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, sdlc-studio/retros/_index.md
> **Evidence:** Found 2026-08-27 by an independent plan review of BG0619, which measured the retitle path rather than reading it. Headers compared directly: retros are `| ID | Sprint | Date | Delivered | Blocked |`, handoffs and reviews are `| ID | Title | Date |`. `retitle_index_row` locates its cells by the `(id, title)` header pair, and `_swap` resolves the link target through `extract_record_id`, which returns None for a RETRO stem.
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`artifact.py retitle` renames an artefact in three places at once: the H1, the filename slug and the index row, plus every inbound link. For a retro, two of those cannot be done and nothing says so.

`retros/_index.md` has NO Title column. `reconcile.retitle_index_row` finds its cells by matching the header pair `(id, title)`, so there is no cell to update - and the row's visible text would stay stale while the file underneath it was renamed. Separately its link rewriter resolves the target through `extract_record_id`, which does not recognise a RETRO stem, so the link would not be rewritten either.

The failure mode is the bad one: `found=True` makes the dry-run validation pass, so the command reports success, renames the file, and leaves a dangling index link behind it. Handoffs and reviews are unaffected - both have a Title column - which is why BG0619 covers those two and excludes the retro rather than shipping a retitle that half works.

## Steps to Reproduce

1. Compare the three meta indexes: `head -3` on retros, handoffs and reviews under `sdlc-studio/`. Only the retro index lacks a Title column. 2. With BG0619's resolver fix in place, run `artifact.py retitle --id RETRO0109 --title '<new>'` in a fixture. 3. The command reports success and the file is renamed. 4. The index row still shows the old title and its link still points at the old filename.

## Proposed Fix

Decide what a retro's index row is FOR, then make the writer and the file agree. Two honest answers, and this bug does not choose: give the retro index a Title column like its two siblings, which makes one rule serve all three and costs a migration of the existing rows; or keep the sprint-shaped columns and have `retitle` REFUSE a retro by name, saying the index records the sprint rather than a title.

Whichever ships, the silent-success path must go first: a rewriter that cannot find the row it was asked to update must fail rather than report `found`. That is the defect underneath both answers, and it is not specific to retros.

## Acceptance Criteria

- [ ] **AC1** Given an index whose header carries no Title column, when the row rewriter is asked to update a title in it, then it REFUSES rather than reporting the row found - a rewriter that cannot find what it was asked to change must not answer that it changed it
- [ ] **AC2** Given an index that DOES carry a Title column, when the same rewriter runs, then it updates the row - the paired control, so refusing the missing case does not become a refusal of the working one
- [ ] **AC3** Given a retro, when `artifact.py retitle` is invoked on it through the shipped command, then the outcome is whatever this bug's fix decides and a test says which - either the index row and its link are both rewritten, or the command refuses and names the reason. What must not happen is the file being renamed while the command reports success
- [ ] **AC4** Given a retro's inbound links, when a retitle succeeds, then every link resolves - `extract_record_id` does not recognise a RETRO stem, so the link half fails independently of the column half and needs its own assertion

## Impact

The tool-first rule exists because a title lives in three places and a hand correction means editing all of them. A retitle that renames the file and silently leaves the index and its links behind is worse than the refusal it replaced: the operator believes the mechanical route worked and does not go looking. It lands on the artefact class that records what a run did.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Filed |
