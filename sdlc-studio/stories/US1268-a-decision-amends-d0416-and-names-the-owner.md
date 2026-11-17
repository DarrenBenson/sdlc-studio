# US1268: A decision amends D0416 and names the owner of the models and effort review, and the review page lists what RFC0062 still owes

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0715
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/decisions.md, sdlc-studio/reviews/LATEST.md, sdlc-studio/rfcs/RFC0062-token-efficient-delivery-a-sprint-costs-at-most.md, tools/tests/test_rfc0062_owed.py
> **Epic:** EP0354
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A decision amends D0416 and names the owner of the models and effort review, and the review page lists what RFC0062 still owes
**So that** CR0715 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A decision amends D0416 and settles the models and effort review

- **Given** `sdlc-studio/decisions.md`
- **When** the rows after D0506 are read
- **Then** one accepted row names D0416 as the decision it amends, states the release that now carries each of CR0670, CR0672 and the Phase 2 benchmark, and either names the unit that owns RFC0062's models and effort review or drops that review with its reason. Fails on: D0416 left as the standing word on a release that has shipped without them, or the review area still owned by nothing
- **Verify:** pytest tools/tests/test_rfc0062_owed.py::Rfc0062OwedTests::test_a_decision_amends_d0416_and_owns_or_drops_the_models_and_effort_review

### AC2: RFC0062 and the review page name what is still owed

- **Given** RFC0062 and `sdlc-studio/reviews/LATEST.md`
- **When** the RFC's Decomposed-into line and the page's `What is owed` section are read
- **Then** the RFC's list names CR0715, and the owed section names each of US1266 and US1267 for as long as that story is not Done. Fails on: an Accepted RFC whose list omits the request that carries its measurement, or a review page that reads as though nothing of RFC0062 is outstanding
- **Verify:** pytest tools/tests/test_rfc0062_owed.py::Rfc0062OwedTests::test_the_rfc_and_latest_name_the_units_rfc0062_still_owes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
