# BG0137: Every archived index row link is wrong-depth: 361 dead links on GitHub

> **Status:** Fixed
> **Severity:** Medium
> **Effort:** M
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Affects:** .claude/skills/sdlc-studio/scripts/archive.py, tools/check_links.py
> **Verification depth:** functional - verified by ATTACK through the public guard, not by reading the report. An independent walker resolved every archived row link relative to the sub-index it sits in: 361 links, 361 resolve, 0 broken. Then one link was regressed to the pre-fix bare-filename depth and `tools/check_links.py` exited 1 and named it; restored, it exits 0. The guard is real and is not fail-open.
> **Raised-by:** sdlc-studio; agent; v1

## Summary

archive.py copies the live index row verbatim into the archive sub-index, which means it copies the BARE FILENAME (BG0001-x.md). But the sub-index lives at <type>/archive/<release>/, two levels below the artefact, so the correct relative target is ../../BG0001-x.md. Every archived row therefore links to a path that does not exist relative to the file it sits in, and every one of them 404s when a reader clicks it on GitHub. 361 rows are affected. This is a link-depth defect, not a phantom: all 361 artefact files exist in their type directory, so nothing is lost - it is purely that the archive, which is the permanent record a reader is most likely to browse cold, is entirely un-navigable. Surfaced by BG0135 while widening `check_links` to validate index row links; the new guard resolves archived rows against the type dir precisely so that it does not cry wolf over this, which means the defect is currently invisible to the gate and will stay that way until it is fixed.

## Steps to Reproduce

1. Open any archive sub-index, e.g. sdlc-studio/bugs/archive/<release>/_index.md. 2. Read a row link: it is a bare filename, `[BG-0001](BG0001-x.md)`. 3. The file it names is at sdlc-studio/bugs/BG0001-x.md, two levels up. 4. Click the link on GitHub -> 404. 5. Repeat for all 361 archived rows.

## Proposed Fix

archive.py must rewrite the row link when it moves the row, not copy it verbatim: a bare filename becomes ../../<filename>. Fix the writer, then backfill the 361 existing rows in one mechanical pass. Once the rows are correct, tighten the `check_links` index-row pass to resolve archive sub-index links relative to the sub-index itself (it currently resolves them against the type dir as a deliberate accommodation for this defect), so the guard can never let the depth regress.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |

## Correction to the repro (2026-07-14)

The Steps above name the archive sub-index as `_index.md`. It is actually `<type>/archive/<release>/<type>.md`
(e.g. `sdlc-studio/bugs/archive/v3.4.0/bug.md`). The repro PATH was wrong; the diagnosis, the depth and the
count of 361 were all correct. Recorded rather than silently edited, because a bug report that was wrong in
a checkable detail is worth knowing about.
