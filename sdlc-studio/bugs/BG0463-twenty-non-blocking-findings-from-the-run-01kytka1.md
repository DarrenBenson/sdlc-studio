# BG0463: Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review: stale counts, dead code, unmarked truncation, over-claiming docstrings and three tests whose names promise more than they assert

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Verification depth:** functional
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/critic.py, tools/check_spec_claims.py, tools/check_script_tests.py, tools/tests/test_check_versions.py, tools/tests/test_porting_doctrine.py, sdlc-studio/tsd.md, sdlc-studio/trd.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, tools/tests/test_check_spec_claims.py, tools/tests/test_check_script_tests.py
> **Evidence:** Independent adversarial review of RUN-01KYTKA1, seven tranches, three seats, isolated worktrees. Every item below was reported as explicitly NON-blocking by the seat that found it.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The residue of the batch-boundary review: real defects that no reviewer judged worth holding a unit for. Collected as one carried unit so none is lost, and so the next sprint prices them together rather than rediscovering them one at a time.

Stale countable claims, each gating nothing: `DRIFT_KINDS (14 entries)` and a changelog's "a tuple of 17" against an actual 19; "33 today" against 53 `tools/tests` modules; "all seven close steps" in four places against a ten-step chain; "three of the chain's steps exist to DO something" against five writers; US0465 AC5's sixteen offenders against eleven stories plus one CR actually swept, with EP0010 a declared false positive and five named paths never touched.

Dead or unreachable code: `_RESOLVED_Q_RE` defined and never referenced, so the "moved under Resolved Questions" route works only by omission from the open-questions pattern; `_FENCE_RE` with a single self-reference, while `claims_in()` reads raw text, so a fenced or historical band is reported as a live claim; a blockquote skip in `check_versions.py` made unreachable by the repair beside it; `cycle_drift(root=...)` accepting a parameter it never reads.

Unmarked truncation: drops render `bits[:12]` and covered units `covered[:6]`, both with no "(+N more)" marker, while the sibling scope-creep row appends one. A silent cap reads as "that is all there was".

Over-claiming prose: `check_versions.py`'s "exactly five places"; a test docstring giving a run command that collects zero tests; a "six parents up" comment over `parents[1]`; `authority` as a decorative field no code reads; two spellings of the stop-ship constant; `NON_CEREMONY_VERBS` as a second hand-maintained list already carrying a stale entry.

Contract drift: on a project declaring no personas every reviewer renders "NO DECLARED SEAT", contradicting `seat_for`'s own documented contract that callers distinguish that from a seat-less reviewer; `check_script_tests.py` sweeps `scripts/` and `scripts/lib/` but not `scripts/hooks/`, currently benign; US0455's declared Affects omits a file its commit changed.

Missing regression cover: the batch-level reviewer contribution a comment calls load-bearing is asserted nowhere; the no-op-add carve-out has none; a stop-ship ruling on an already-Fixed finding blocks the close permanently; a US0576 fixture exercises a state the writer cannot produce.

## Steps to Reproduce

Each item was established by execution during the review - census, mutation or direct probe - and is recorded with its file and line in the seat reports for RUN-01KYTKA1. Representative measurements:

```text
DRIFT_KINDS            : claimed 14 / 17, actual 19
tools/tests modules    : claimed 33, actual 53
_CLOSE_CHAIN           : claimed 7, actual 10
_FENCE_RE              : 1 occurrence, its own definition
_RESOLVED_Q_RE         : 1 occurrence, its own definition
cycle_drift(root="/nonexistent") == cycle_drift(None)
grep '["authority"]' scripts/*.py -> no match outside the test
```

## Proposed Fix

Take them as one grooming pass rather than twenty. The counts want deriving, not correcting - each was true when written and none has a guard, which is why they drifted. The dead patterns want deleting with a note on what actually implements the route. The truncations want the marker the sibling row already has.

## Acceptance Criteria

- [ ] Every stale countable claim listed is either derived from the thing it counts or removed, so it cannot drift again silently
- [x] Every dead pattern listed is deleted, with the mechanism that actually implements its route named where it stood
- [x] Both truncated renders carry a `(+N more)` marker, matching the sibling row that already does
- [ ] Each over-claiming docstring and comment states what the code does, and the three tests whose names promise more than they assert are either strengthened to match their names or renamed to match their assertions

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-08-05 | Claude Opus 5 | **Delivered NARROWED under RUN-01KZ79C1, and most of this bug was already repaired.** VERIFIED rather than assumed, item by item: `_FENCE_RE` has no references left, the `covered[:6]` row already carries its marker, and the DRIFT_KINDS counts were fixed by US0458, which made the TRD cite `reconcile.DRIFT_KINDS` instead of restating it - the surviving 'tuple of 17' is in US0458's own changelog fragment, a historical record of that change and not a live claim, so it is left alone. Genuinely still broken and now fixed: the impediments row's `bits[:12]` dropped everything past twelve unmarked while its sibling row marked it (pinned by a fixture-backed test - a dict fixture skipped silently and asserted nothing); `_RESOLVED_Q_RE` was defined and never referenced, so the 'moved under Resolved Questions' route worked by OMISSION while a pattern beside it read as though something enforced it, now deleted with the real route named where it stood; and `cycle_drift` took a `root` parameter it never read, now removed - every caller already passed nothing. NOT delivered: the remaining stale-count and over-claiming-prose items, and the contract-drift and regression-cover halves. This unit stays Open. |
