# CR-0109: Tranche audit (sprint breakdown) should run verify_ac lint + ac_scope, not leave them hand-found

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

The --goal design breakdown grooms readiness via audit.py check (weak-AC, unmet-deps, link-integrity, already-terminal, already-satisfied). But two readiness problems the skill already has deterministic tools for are NOT run, so a field agent re-discovered both by hand: (1) non-executable Verify lines - perf ACs as prose ('curl ... prints < 0.300' against a live API + a non-existent spec), which verify_ac lint (CR0085) is built to flag (hit on US0001, then again across this sprint); (2) cross-epic AC leakage - 5 EP0002 stories carrying EP0005 web-client ACs, which ac_scope (CR0086) is built to flag. Wire both into audit check so the breakdown surfaces them deterministically instead of relying on the agent noticing.

## Acceptance Criteria

- [ ] audit check runs verify_ac lint over the batch's stories and surfaces non-executable/decorative Verify lines as a readiness finding (e.g. weak-verify), reusing scripts/verify_ac.py (no new logic)
- [ ] audit check runs ac_scope over the batch and surfaces cross-epic AC leakage (an AC owned by another epic) as a finding (e.g. cross-epic-ac), reusing scripts/ac_scope.py
- [ ] both are advisory readiness findings (like weak-AC) in the audit output, not hard blocks; reuse the existing scripts; behaviour is documented in reference-audit.md + the reference-sprint.md breakdown step
- [ ] unit tests: a story with a prose Verify line is flagged + a runner-targeted one passes; a cross-epic AC is flagged; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
