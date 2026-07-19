# CR-0356: reconcile never checks the index row's title, so a retitled artefact drifts silently and no script can fix it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

reconcile's census compares status, counts, links and breakdown state between an artefact and its index row, but never the TITLE. Retitling an artefact - which is normal when a CR is widened or a bug is better understood - leaves the index row carrying the old title with no drift reported, so the index and the artefact disagree permanently and silently. Found while widening CR0351: after the rewrite, detect reported `drift_items`=0 while the row still read the superseded title. The index is supposed to be derived from the files, so a field it copies but never re-checks is a hole in that guarantee. It also leaves the operator no tool-driven way to fix it: the standing rule is never to hand-author _index.md, and no script offers a retitle or a title sync.

## Impact

The index is the surface every status view, dashboard and reviewer reads first. A row whose title no longer matches the artefact misdescribes the work in the one place people look before opening the file, and because detect stays green nothing ever surfaces it.

## Acceptance Criteria

- [ ] a title mismatch between an artefact H1 and its index row is reported as a drift kind
- [ ] reconcile apply syncs the row from the file, since the file is the source of truth
- [ ] the new kind is registered in `DRIFT_KINDS` and in the remediation registry so status and hint surface it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
