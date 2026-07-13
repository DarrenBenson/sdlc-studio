# EP0032: v4.1 run-close and agent DX

> **Status:** Draft
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio new

## Summary

{{what this epic groups}}

## Story Breakdown

CR0223 is the keystone: it builds the run-state object that does not exist today (run state is
currently scattered across seven files that nothing joins), and CR0225 is built on it. The
other three are independent and parallel.

- [ ] [CR0223](../change-requests/CR0223-the-handoff-guide-a-first-class-remaining-work.md) - the handoff guide: a generated remaining-work artefact at run close (KEYSTONE - builds the run-state object; every input is already machine-readable, so this is a join, not new instrumentation)
- [ ] [CR0225](../change-requests/CR0225-appetite-bounded-unattended-runs-a-budget-circuit-breaker.md) - appetite-bounded runs: wall-clock + unit-count breaker fired at unit boundaries (depends CR0223; rescoped per D0020 - tokens are an advisory forecast, not a gate)
- [x] [CR0224](../change-requests/CR0224-multi-repo-context-the-repo-map-and-census.md) - cross-repo Depends-on resolution: lift blocker_sweep's manifest resolver into a shared helper (rescoped per D0019; the PVD-wide edge list went to RFC0030) (independent)
- [ ] [CR0234](../change-requests/CR0234-uniform-cli-grammar-across-skill-scripts.md) - uniform CLI grammar; scope grew with two instances hit while planning this sprint, one of which silently produced a wrong sprint plan (independent)
- [ ] [CR0235](../change-requests/CR0235-a-lighter-planning-tier-for-story-epic-templates.md) - a planning template tier between minimal and full, so a planning story is not forced past 170 lines (independent)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Darren | Created via `new` (deterministic) |
