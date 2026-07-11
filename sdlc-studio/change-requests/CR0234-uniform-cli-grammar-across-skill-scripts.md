# CR-0234: Uniform CLI grammar across skill scripts

> **Status:** Proposed
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-11 | audit | Raised |
