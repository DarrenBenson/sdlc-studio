# EP0026: Gate integrity: the meta-layer verifies itself

> **Status:** Draft
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new

## Summary

The meta-layer must verify itself: RV0007 proved six breaking commits reached `main`
through gaps BETWEEN green gates (a disabled hook, dark CI, an always-warning advisory lane, a
gate that passes when a check crashes). This epic makes the guard chain self-checking and makes
running it cheap for agents. RFC0027 sequences it FIRST: it is what lets the two later epics
trust their own green. Runs pre-tag per the operator's backlog-clear-before-v4 directive.

## Story Breakdown

Unit roster (bugs fixed directly; CRs decompose via `cr action` at execution - stories land under this epic):

- [ ] [CR0202](../change-requests/CR0202-detect-a-disabled-commit-gate-nothing-verifies-core.md) - detect a disabled commit gate (hooksPath advisory in gate/status)
- [ ] [CR0203](../change-requests/CR0203-make-the-mutation-gate-earn-its-lane-wire.md) - mutation gate: wire a bounded run into sprint close, or remove the lane
- [ ] [CR0204](../change-requests/CR0204-normalise-the-eleven-test-files-with-mid-file.md) - normalise the eleven mid-file `__main__` test guards (36 hidden classes)
- [ ] [CR0209](../change-requests/CR0209-one-unit-close-verb-batch-gate-reporting-a.md) - unit-close orchestrator + batch gate reporting + metadata-stamp verb
- [ ] [BG0085](../bugs/BG0085-sprint-plan-origin-drift-preflight-silently-dies-for.md) - sprint plan origin-drift preflight silently dies for --order manual
- [ ] [BG0090](../bugs/BG0090-gate-py-fail-open-a-check-that-raises.md) - gate.py fail-open: a raising blocking check reads as PASS
- [ ] [BG0094](../bugs/BG0094-plan-review-resolves-stories-with-a-case-sensitive.md) - plan_review case-sensitive story glob: unclearable false block
- [ ] [BG0095](../bugs/BG0095-the-provenance-external-stamp-that-gates-shell-verifiers.md) - Provenance: external stamp has no writer on the ingest path
- [ ] [BG0096](../bugs/BG0096-ci-never-runs-gate-py-although-the-pre.md) - CI never runs gate.py despite claimed parity

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
