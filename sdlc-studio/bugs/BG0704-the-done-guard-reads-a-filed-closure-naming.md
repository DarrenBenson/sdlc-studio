# BG0704: The Done guard reads a filed closure naming the unit itself as a repair, and lists repaired findings as outstanding when the only APPROVE is the author's own

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/US0627-delivery-engineering.txt (engineering seat); verdicts/US0627-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md. The second half is the implementer's observation during the US0627 repair, queued in findings/todo.txt. US0627 round-two delivery verdicts (qa brief da60784a5d19, engineering 5c7f8de69d59).
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

critic.py repair accepts a filed closure naming the unit itself, or any id that resolves such as a Done epic, and `coverage_state` reads that as repaired (critic.py:1427, the same at 3f73ab64). The delivered-terminal REJECT guard makes it a one-command route to Done: US0001 filed to US0001, then Done, exit 0. The ledger already holds BG0558 filed to BG0558, and no open bug or CR covers it. When every finding carries a closure but the only APPROVE is the author's own under the same brief, `repair_state` reads none and the refusal lists every finding as outstanding, which misdescribes what is missing. Checking filed ids on every read costs time in sweeps that open no corpus cache (critic.py:1782-1794): over 743 units `coverage_counts` went from 19.8 s to 28.6 s and whole-workspace conformance from 72.9 s to 76.3 s; gate.py and conformance open no cache window, and inside one the cost is zero. Round two of US0627 (4e780dcb) adds three: the close tail derives epics and requests over done and skipped units only (sprint.py:6674), so an epic whose last open child the run abandoned stays at Draft - safe, but no test pins it; the `_batch_unfanned_units` docstring's invariant 'never both and never neither' (sprint.py:6514) is stale now that abandoned units sit in a third list, `_batch_abandoned_units`; and the close's step-1 review-coverage still lists an abandoned unit that carries an unanswered REJECT.

## Steps to Reproduce

1. Record a delivery REJECT on US0001; python3 .claude/skills/sdlc-studio/scripts/critic.py repair --unit US0001 --closed '#1 -> filed: US0001'; transition.py set US0001 Done - exit 0. 2. Close every finding of a REJECT, then record an APPROVE by the unit's own author under the same brief; transition.py set <unit> Done - the refusal lists every finding as outstanding.

## Proposed Fix

Refuse a filed closure whose artefact is the unit itself or is not a bug, CR or story that can carry a finding. When every finding carries a closure and only a self-authored APPROVE follows, say that the missing piece is an independent APPROVE. Open one corpus cache around `coverage_counts` and the conformance sweep.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: critic.py repair accepts a filed closure naming the unit itself, or any id that resolves such as a Done epic, and `coverage_state` reads that as repaired...
- [ ] **AC2** The proposed fix lands, pinned by a test: Refuse a filed closure whose artefact is the unit itself or is not a bug, CR or story that can carry a finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
