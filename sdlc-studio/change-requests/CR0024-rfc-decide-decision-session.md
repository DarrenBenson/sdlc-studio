# CR-0024: `rfc decide` - the multi-RFC decision session

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** scripts/rfc.py (new), reference-rfc.md, help/rfc.md, SKILL.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The skill has a per-RFC lifecycle (`rfc create/list/review/accept/close`) but no
**batch decision session**: triaging the whole Draft backlog into decision briefs
and recording accept/defer/withdraw across them at once. That session was run by
hand (8 RFCs digested via sub-agents). Make it a first-class function -
`rfc decide` - the front-of-pipe analogue of the autosprint tranche-audit (CR0021):
groom the RFC backlog before any of it becomes delivery work.

## Problem

`rfc review` flags ages and stale open-decisions but produces no per-RFC decision
brief (core decision, options + leaning, what acceptance spawns, recommended
disposition), and there is no deterministic digest of RFC decision-readiness. Every
backlog-wide RFC decision is therefore improvised.

## Proposed Changes

### Item 1: `rfc decide` workflow (decision session)

**Priority:** High **Effort:** Low

Add a `decide` action to `reference-rfc.md` (and `help/rfc.md`): select Draft/In
Review RFCs, emit a decision brief per RFC from its own Design Options / Open
Decisions / Recommendation, present for a batch operator decision, then per RFC
route to the existing `rfc accept` (Decision + spawn CRs), defer (stay Draft, record
the trigger), or `rfc close` (withdraw/supersede). The adversarial judgement stays
model-instructed.

### Item 2: Deterministic readiness digest `scripts/rfc.py decide`

**Priority:** High **Effort:** Medium

A new `scripts/rfc.py` `decide` subcommand emits a JSON digest per Draft RFC: open
decisions (total + still-Open count), workstream count, has-recommendation, status,
and a `ready_for_decision` flag (Draft + has recommendation + no open decisions).
The mechanical inputs to the session; parallels `audit.py` / `review_prep.py`.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/rfc.py | RFC decision-readiness digest | New |
| reference-rfc.md | `decide` action (decision-session workflow) | Modified |
| help/rfc.md | document `rfc decide` | Modified |
| SKILL.md | note the new action (no new type) | Modified |

### Breaking Changes

None. A new action + helper; the existing rfc actions are unchanged.

## Acceptance Criteria

- [x] `rfc.py decide` reports, per Draft RFC, the open-decision count (total + Open), workstream count, has-recommendation, and a `ready_for_decision` flag.
- [x] An RFC with unresolved Open decisions or no recommendation is `ready_for_decision: false`; a Draft with a recommendation and no Open decisions is true.
- [x] The digest emits JSON and is unit-tested.
- [x] `reference-rfc.md` and `help/rfc.md` document the `rfc decide` decision-session workflow (briefs -> batch accept/defer/withdraw).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (rfc-decide) | Complete - US0021: scripts/rfc.py decide digest + reference-rfc.md/help decide action; critic-approved (verified vs real RFCs) |
| 2026-06-20 | Darren Benson | Raised - the manual multi-RFC decision session should be a defined skill function (parallels tranche-audit) |
