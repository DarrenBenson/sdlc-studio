# US0622: a repair closing fewer findings than the REJECT raised is reported PARTIAL and names the outstanding ones

> **Status:** Ready
> **Delivers:** CR0506
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0205
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator deciding whether a rejected unit is really answered
**I want** a repair that closes only some of the findings reported as PARTIAL, naming the rest
**So that** a repair cannot be claimed wholesale over a rejection it only half answered

## Notes

Delivers criterion 3 of CR0506. This is the guard on US0620's record: without it, the route back
to covered is opened by recording any repair at all, which would be a worse gate than the one
being replaced - it would convert every REJECT into an APPROVE for the cost of one command.

Not hypothetical. Of the 18 units measured on RUN-01KYPZ1G, two carried residue that was still
open and knowingly held - `BG0401` and `BG0406`. A wholesale claim over those two would have
recorded them as answered while the defects sat open.

The comparison must be per finding and derived, never a count. LL0015 - a guard that only catches
the total case is not a guard - so a repair naming three of five findings is PARTIAL even when
somebody writes "all findings repaired" in its own text.

## Acceptance Criteria

### AC1: a repair covering some findings is PARTIAL and names the outstanding ones

- **Given** a REJECT raising five findings and a repair closing three
- **When** the repair is read
- **Then** it is reported PARTIAL and names the two outstanding findings individually, so the
  reader learns which are still open rather than that some are
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PartialRepairTests::test_a_repair_covering_some_findings_is_partial_and_names_the_residue

### AC2: completeness is derived per finding, never taken from prose

- **Given** a partial repair whose own text claims every finding is closed
- **When** the completeness is computed
- **Then** it is still PARTIAL, because the verdict is derived by matching each recorded closure
  against each raised finding - a claim in the repair's prose carries no weight
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PartialRepairTests::test_completeness_is_derived_per_finding_not_read_from_prose

### AC3: a repair closing every finding is COMPLETE, and that is what US0621 reads

- **Given** a repair closing all five
- **When** the completeness is computed
- **Then** it is COMPLETE, and that is the state the three-way coverage predicate accepts as
  repaired - so the positive control sits beside the refusal and PARTIAL cannot be the only
  reachable answer
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PartialRepairTests::test_a_repair_closing_every_finding_is_complete_and_counts_as_repaired

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-03 | Claude Opus 5 | Groomed against CR0506 criterion 3, with the positive control made its own criterion so PARTIAL is not the only reachable verdict |
