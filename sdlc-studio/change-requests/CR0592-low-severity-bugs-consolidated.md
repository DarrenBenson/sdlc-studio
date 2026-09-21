# CR-0592: Low-severity bugs (consolidated)

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-09-21
> **Consolidation:** low-severity-bugs
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A themed consolidation of Low-severity findings that individually do not warrant a standalone artefact (triage noise control, schema v3). Triage the batch, then action or reject as one.

## Impact

Each finding here is Low-severity on its own; the batch is triaged, then actioned or rejected as one. Left unconsolidated, the same findings would each mint an artefact and drown the real signal.

**Points:** 3

## Consolidated Findings

- **the blockquote skip in check_versions is unreachable, so it guards nothing**: BG0463 claim 8, confirmed by execution. `_is_superseded` continues on a line beginning with `>`, but the regex that skip protects never matches a `>`-prefixed line in the first place - all three blockquoted Status forms return False when executed directly. The skip changes no outcome for any input, so it is either dead code or the regex is wrong; the two readings have opposite fixes, which is why this is worth resolving rather than deleting on sight.
- **the checklist's authority field is carried on 22 rows and read by no renderer**: BG0463 claim 15, still true. All 22 CHECKLIST rows carry an `authority` field and the only read anywhere in the tree is an assertion in test_sprint_report.py. A field that only its own test reads is indistinguishable from a field nobody needs, and it costs every future editor a decision about what to put in it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Consolidation opened |
