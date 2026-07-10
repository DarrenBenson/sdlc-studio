# CR-0215: big-bang v4 documentation pass: every consuming-facing doc tells the v4 story

> **Status:** Proposed
> **Depends on:** CR0216, CR0212, CR0214, CR0213
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Operator-requested ahead of the v4.0 GA tag. The README and consuming-facing docs still read as the v3 line with v4 grafted on: the headline features of the big-bang release (schema v3 ULID identity as the new-project default, the migrate walk, the independence gate, verification-depth tiers, the portable CI gate, retro/review tooling, the CLI grammar) need one coherent pass so a newcomer reads v4 as the product, not a changelog. Includes verifying every version string, upgrade instruction, and feature table against what v4 actually ships.

## Acceptance Criteria

- [ ] README presents v4 headline features accurately (schema v3 default, upgrade walk, gates) with no stale v3-era claims; quick-start works verbatim on a fresh v4 install
- [ ] Upgrade/migration docs (reference-upgrade, help/init, INSTALL surfaces) describe the v2->v3 id switch, its flag, and the operator choice explicitly
- [ ] A sweep of docs/, SECURITY.md, CONTRIBUTING.md and the help/ tree finds no claim contradicted by v4 behaviour (checked against the shipped scripts, not memory)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
