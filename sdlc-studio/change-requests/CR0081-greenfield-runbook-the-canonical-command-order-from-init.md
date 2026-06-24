# CR-0081: greenfield runbook - the canonical path from init through the autosprint handoff

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

There is no single page that states the canonical command order for a greenfield start.
The agent who reflected on it had to **reconstruct** the sequence (`init -> prd ->
personas -> trd -> tsd -> epic -> story -> verify`) from scattered "Next Steps" footers
and the status hint. A one-page greenfield runbook - the start-to-reviewable-backlog
path, in order, in one place - removes that reconstruction every first run.

## Problem

From a greenfield reflection (verbatim): *"Command-order uncertainty. I inferred init ->
prd -> personas -> trd -> tsd -> epic -> story -> verify from scattered 'Next Steps'
footers and the status hint. A greenfield runbook (the canonical order, start to
reviewable-backlog) in one place would beat reconstructing it."*

The per-command "Next steps" hints are good locally but never compose into the whole
path, so a newcomer assembles the map by trial. This is a pure documentation/navigation
fix - the capabilities exist; the route through them is not written down.

## Proposed Changes

### Item 1: A greenfield runbook page

**Priority:** Medium
**Effort:** 1

Add a single runbook (e.g. `help/getting-started.md` or a section in the SKILL router)
giving the canonical order from empty repo to reviewable backlog: `init` (config + dirs +
indexes + agent-instructions) -> `prd` -> `persona` -> `trd` -> `tsd` -> `epic` ->
`story` -> `reconcile`/`validate`. Each step: the one-line why, the command, what it
produces, and what unblocks next. Note where the authoring loop (RFC0019) collapses the
epic->story span once it lands.

### Item 1b: The implementation handoff and autosprint's cold-start precondition

**Priority:** Medium
**Effort:** 1

The runbook continues past the reviewable backlog into implementation, and must state
autosprint's **implicit precondition**: its loop (implement -> test -> gate -> critic ->
commit-green) assumes a **runnable verification environment** each iteration. On
greenfield that environment does not exist yet - no toolchain, no gate to run - so
autosprint cannot bootstrap itself. The canonical handoff (confirmed by a field agent):

1. Build the **foundation epic by hand** to a green gate - it establishes the buildable/
   testable scaffold and the high-judgement conventions every later story inherits
   (stack wiring, error-envelope shape, ID scheme, migration strategy).
2. Once the gate runs green, hand subsequent epics to `autosprint --epic EPxx --goal done`
   - now there are working tests and a gate for the loop to lean on.

Record this as the rule: **do not invoke autosprint before the quality gate is runnable
and green.** Mirror the precondition into `reference-autosprint.md` (a "Preconditions /
cold-start" note) so it is discoverable from the loop's own docs, not only the runbook.

### Item 2: Make the path discoverable

**Priority:** Low
**Effort:** 1

Link the runbook from the SKILL router and from `init`'s output ("Next: follow the
greenfield runbook"), so the route is one hop from the first command a newcomer runs.

## Acceptance Criteria

- [x] a single greenfield runbook page lists the canonical command order start to
      reviewable backlog, each step with why / command / output / next
- [x] the runbook is linked from the SKILL router and from `init`'s reported next steps
- [x] it names the decisions log (CR0080) and the future authoring loop (RFC0019) at the
      right points in the path
- [x] the runbook states the implementation handoff (foundation epic by hand to a green
      gate, then `autosprint --epic EPxx --goal done`) and autosprint's runnable-gate
      precondition; the precondition is mirrored into `reference-autosprint.md`
- [x] anchor links resolve (`tools/check_links.py`); CHANGELOG `[Unreleased]` entry same
      commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
