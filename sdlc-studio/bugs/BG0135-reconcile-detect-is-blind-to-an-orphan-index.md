# BG0135: reconcile detect is blind to an orphan index row whose artefact file is gone

> **Status:** Open
> **Severity:** Medium
> **Effort:** M
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, tools/check_links.py
> **Raised-by:** sdlc-studio; agent; v1

## Summary

reconcile syncs the index in one direction only: it walks the artefact FILES and fixes their rows. An index row pointing at a file that no longer exists is never noticed, so the index keeps advertising an artefact that is not there. The whole promise of the index is that it is DERIVED and that reconcile is the thing that makes that true; in this direction it is not. Three guards miss it independently: reconcile detect reports `drift_items`=0, `check_links` reports all links resolve (it validates anchors, not relative file targets, so a dead row link is invisible to it), and validate check reports 0 errors. The phantom is then counted by status and read by anything that trusts the index. Found by dogfooding: a probe artefact was created to test BG0132 refusal behaviour, deleted from disk, and its row survived every check in the gate.

## Steps to Reproduce

1. Create any CR: `file_finding.py` file --type cr ... (mints e.g. CR0261 and writes its index row). 2. Delete the artefact file: rm sdlc-studio/change-requests/CR0261-*.md. 3. Run reconcile.py apply -> "changed 0 row(s)". 4. Run reconcile.py detect -> scope=all `drift_items`=0. 5. grep CR0261 sdlc-studio/change-requests/_index.md -> the row is still there, linking to a file that does not exist. 6. python3 tools/`check_links.py` -> "All markdown anchor links resolve". 7. validate.py check -> errors=0.

## Proposed Fix

reconcile must reconcile BOTH directions. Add an orphan-row check: for every row in an _index.md, the artefact file it links to must exist; if it does not, report it as drift (kind: `orphan_row)` under detect, and under apply remove the row (or, safer, report-only under detect and require an explicit flag to prune, since a missing file can also mean a bad checkout or an in-flight rename rather than a deletion). Separately, `check_links.py` validates anchors but not relative file targets - a link to a non-existent sibling markdown file should fail it. Fixing either would have caught this; fixing both is right, because they fail for different reasons.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
