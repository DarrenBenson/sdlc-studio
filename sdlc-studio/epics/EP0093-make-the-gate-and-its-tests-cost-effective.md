# EP0093: Make the gate and its tests cost-effective: three tests are 53% of the suite

> **Status:** Draft
> **Parent:** RFC0048
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py,.claude/skills/sdlc-studio/scripts/tests/test_telemetry.py,.claude/skills/sdlc-studio/scripts/gate.py
> **Size:** L

## Summary

RFC0048 option B, re-measured 2026-07-21 before planning. The suite is 153.1s over 3,409 tests, and the cost is not spread: THREE tests are 81.2s of it. `test_gate.py`'s two real-wrapper tests both run the full gate over this repo (35.56s and 35.54s) - the same computation twice, the second asserting only that the exit code is 0 or 1. `test_telemetry.py` writes 5,050 records sequentially to prove the evidence log is never rolled (10.12s). `test_sprint.py`'s 19.3s is diffuse at ~100ms per test with no hotspot, so it is a different problem and is not in this epic. Beneath the tests, `run_gate` itself costs 35.6s, 83% of it in three lanes (engagement-floor 11.0s, constitution 10.2s, validate 8.2s) that each re-walk the same ~1,800-artefact corpus independently - a cost the pre-commit hook pays on every single commit, not just in the suite. This epic takes the concentrated wins and leaves the diffuse one. It changes no coverage: every behavioural pin that exists today still exists afterwards, and the one true end-to-end gate execution is kept.

## Story Breakdown

- [ ] [US0284: test_gate's two real-wrapper tests share one gate execution instead of running it twice](../stories/US0284-test-gate-s-two-real-wrapper-tests-share.md)
- [ ] [US0285: The never-rolled evidence-log pin drives an injected cap, not 5,050 real records](../stories/US0285-the-never-rolled-evidence-log-pin-drives-an.md)
- [ ] [US0286: The three heavy gate lanes share one artefact corpus instead of walking it each](../stories/US0286-the-three-heavy-gate-lanes-share-one-artefact.md)
- [ ] [US0287: Set D6's per-commit gate budget against the improved baseline and pin the ratchet](../stories/US0287-set-d6-s-per-commit-gate-budget-against.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
