# EP0013: Structured authorship and policy enforcement

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new

## Summary

Turns the team-schema conventions into machine-checked structure: typed `raised_by` /
`triaged_by` authorship (persona today, agentic entity later via a resolver swap), the
minimal separation-of-duties rule, evidence-as-schema, one consolidated CI lint that runs
the whole rule set, and a cross-script invariant test tier that guards the cascade seams the
RV0006 review found unprotected. Groups CR0169 (structured authorship), CR0170 (separation of
duties lint), CR0171 (evidence as schema), CR0174 (lint consolidation), CR0185 (invariant
test tier). Depends on EP0012's identity/index guarantees; CR0169 blocks the enforcement CRs.

## Story Breakdown

- [ ] [US0060: Structured raised_by and triaged_by typed references with backfill](../stories/US0060-structured-raised-by-and-triaged-by-typed-references.md)
- [ ] [US0061: Separation-of-duties lint: triaged_by must not equal raised_by](../stories/US0061-separation-of-duties-lint-triaged-by-must-not.md)
- [ ] [US0062: Evidence-as-schema: per-type required evidence, lint-enforced](../stories/US0062-evidence-as-schema-per-type-required-evidence-lint.md)
- [ ] [US0063: Consolidated audit-check command over the team-schema rules](../stories/US0063-consolidated-audit-check-command-over-the-team-schema.md)
- [ ] [US0064: Cross-script invariant test tier over the cascade seams](../stories/US0064-cross-script-invariant-test-tier-over-the-cascade.md)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
