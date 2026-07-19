# CR-0287: TSD denies the blocking CI gates that exist: coverage ('not wired into CI' vs a blocking 80% gate) and security ('no dedicated scanner' vs a blocking bandit step)

> **Status:** Complete
> **Decomposed-into:** EP0071
> **Priority:** Medium
> **Type:** docs
> **Size:** S
> **Affects:** sdlc-studio/tsd.md
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

tsd.md states three times that statement coverage is not collected or gated in CI (lines 175-176, 389-390, 546) while .github/workflows/lint.yml has run a blocking 'Coverage gate (runtime scripts, >= 80%)' step (--fail-under=80, no continue-on-error) since 2026-06-22 (CR0076); the enforced 80% floor vs the stated ~90% target is unreconciled anywhere. The same document says 'No dedicated security scanner is wired' (line 318) and its NFR/quality-gate tables omit bandit, while lint.yml runs bandit as a blocking step over the shipped scripts. The document of record for test strategy misdescribes two enforced gates in the same workflow file - a reader auditing gates from the TSD would conclude both need adding when both already block. Both halves verified 3x by their refute panels; the stale text predates the gates and survived the 2026-07-14 TSD edit.

## Impact

tsd.md states three times that statement coverage is not collected or gated in CI (lines 175-176, 389-390, 546) while .github/workflows/lint.yml has run a blocking 'Coverage gate (runtime scripts, >= 80%)' step (--fail-under=80, no continue-on-error) since 2026-06-22 (CR0076); the enforced 80% floor vs the stated ~90% target is unreconciled anywhere.

## Acceptance Criteria

- [ ] Coverage Targets, Coverage Measurement and the tools table record the blocking 80% CI coverage gate and reconcile the 80% floor with the ~90% aspiration
- [ ] Security Testing and both quality-gate tables record the blocking bandit step with its scope and flags

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
