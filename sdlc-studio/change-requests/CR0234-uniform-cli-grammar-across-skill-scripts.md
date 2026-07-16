# CR-0234: Uniform CLI grammar across skill scripts

> **Status:** Complete
> **Size:** S
> **Priority:** P3
> **Type:** Improvement
> **Date:** 2026-07-11
> **Created-by:** sdlc-studio file

## Summary

Follow-on to CR0210 (Complete), which unified id-list forms, target selection and
recorder field names but did not cover flag PLACEMENT. Today's residuals: status.py
rejects a global '--root .' (root exists only per-subcommand, unlike
validate.py/reconcile.py/artifact.py which accept it uniformly); and when
transition.py set refuses '--author' without the verdict pair, the error does not
mention `transition annotate` - the verb CR0209 shipped for exactly that identity
stamp - so an agent that has not memorised the catalogue re-derives it the hard way
(observed today: the RFC0029 acceptance stamp was skipped, then recovered later via
annotate).

## Acceptance Criteria

- [ ] Every skill script accepts --root at the same position (global, valid before or after the subcommand)
- [ ] transition.py set's all-or-none verdict error names `transition annotate` as the path for identity-only stamps
- [ ] The CR0210 conformance sweep extends to flag placement (--root, --format) across every script's argparse tree
- [ ] A repeated single-value flag never silently discards an earlier value: `sprint.py plan --crs Proposed --crs Deferred` must either merge both statuses or refuse, not drop the first without a word
- [ ] The conformance sweep flags any repeatable-looking flag whose argparse action silently overwrites (the `store` vs `append` mismatch), across every script

## Impact

Each of these costs an agent a wrong turn that it must detect and recover from unaided. The
`--crs` case is worse than friction: it produced a **silently wrong sprint plan** (two CRs
missing from the batch, no warning), which is a planning tool lying about the plan. Cheap to
fix, and the class is exactly what the CR0210 conformance sweep exists to catch.

**Effort:** S

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Raised |
| 2026-07-13 | Darren | Two live instances hit while planning the v4.1 sprint, both added as ACs. (1) `sprint.py plan --crs Proposed --crs Deferred` silently kept only the last value and produced an 11-unit plan that omitted the two Proposed CRs - a silent-wrong-answer bug, not just grammar. (2) `transition.py set --author X` refused with the all-or-none verdict error and did not name `annotate`, exactly as this CR predicted. |
