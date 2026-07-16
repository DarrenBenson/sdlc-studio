# RFC-0043: Definition of Ready and Definition of Done as editable per-project artefacts, enforced by the existing gates

> **Status:** Draft
> **Decomposed-into:** CR0324, CR0325, CR0326
> **Size:** XL
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Introduce DoR and DoD as first-class, EDITABLE per-project artefacts (like the PRD/TRD), with shipped defaults a project can customise, and wire the existing gates to READ them. Agile practice: a Definition of Ready is the shared checklist a backlog item must pass BEFORE it enters a sprint (clear story, ACs specified, dependencies identified, sized and not too complex); a Definition of Done is the checklist work must pass to be called complete (code done, reviewed, tested, documented, deployed) - a yes/no quality gate, non-negotiable, and only as strong as how visibly it is enforced. sdlc-studio already enforces BOTH implicitly but scattered and un-named: DoR ~ the grooming gate (sprint plan refuses a unit with no Affects/Points/ACs) + the two-backlog refusal (a request is not a ready sprint unit); DoD ~ the story->Done gate (executable ACs pass), the author!=reviewer critic APPROVE, and the close gate (retro/review/lessons via gate --require-retro). This RFC makes them explicit, editable, and multi-LEVEL (a story DoR/DoD, a sprint DoD = the close-down, a release DoD = the 5.0.0-cut criteria). It SUBSUMES RFC0042: the sprint-level DoD's close clause IS the un-skippable close-down. Research: atlassian.com/agile DoR & DoD, scrum.org (multiple levels of done; DoD as a gate), mountaingoatsoftware.com (multiple levels), scruminc.com (the team's quality bar). XL - decompose (an RFC to settle the artefact shape + the level model, then CRs per level/gate-wiring).

## Design Options

- **Two editable documents - sdlc-studio/definition-of-ready.md and definition-of-done.md - as the human-readable source of truth (authored like PRD/TRD, shipped defaults), with a machine-checkable SUBSET the existing gates read and enforce (grooming reads the DoR; story-Done + the close gate read the DoD). Multi-level sections (story / sprint / release)**
- **A config-only model: dor/dod checklists in .config.yaml that the gates read - lighter, but not the editable human-authored artefact the operator asked for**
- **Documents only, advisory (no gate wiring) - discoverable but not enforced, which the field evidence says means skipped**
- **Hybrid (recommended): the editable documents are the source of truth AND carry a machine-checkable subset (tagged checklist items) the gates enforce; the human criteria and the enforced criteria live in one file so they cannot drift. Subsumes RFC0042 as the sprint-DoD close clause**

## Recommendation

**The hybrid: editable documents that are both the human source of truth and the machine-checkable
contract.** `definition-of-ready.md` and `definition-of-done.md` are authored per project (shipped
defaults, edited like the PRD/TRD). Each criterion is a checklist item; a subset is TAGGED as
machine-enforceable and mapped to an existing check, so the human intent and the enforced rule live
in one file and cannot drift. The gates read them: DoR at grooming/`sprint plan` (a unit not meeting
the ready bar is refused), DoD at `story -> Done` (executable ACs), the critic gate (independent
APPROVE), and the sprint close (`gate --require-retro`). Non-negotiable by design: when pressure
builds, the sanctioned response is to cut scope, never to weaken the bar - which is why the bar is a
gate, not a checklist. This UNIFIES the currently-scattered implicit gates under two named, editable
artefacts, and SUBSUMES RFC0042: the sprint-level DoD's close clause is the un-skippable close-down.

## Levels (the DoD is not one thing)

| Level | DoR | DoD | Existing gate |
| --- | --- | --- | --- |
| Story/unit | groomed: single-line ACs with Verify, Affects, Points, on-scale | executable ACs pass; independent critic APPROVE | grooming + `transition -> Done` + critic |
| Sprint | the batch is ready (refined, sized, deps met) | the close-down: retro + lessons + review, all green | `gate --require-retro` (RFC0042 makes it un-skippable) |
| Release | the release scope is decided | the release DoD: version bump, CHANGELOG, migration, deploy readiness | `gate --release`, deploy-readiness |

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Artefact shape (editable docs vs config vs hybrid) | Resolved: the hybrid - editable documents carrying a tagged machine-checkable subset |
| D2 | How a criterion tags to an enforceable check | Resolved: check-id registry - [check: <id>] tags resolving through one registered vocabulary; unknown id = loud error; untagged = human-judged (operator, 2026-07-17) -> CR0324 |
| D3 | Defaults vs generated | Resolved: shipped defaults + an init tailoring OFFER derived from the detected stack; the static documents stay the source of truth (operator, 2026-07-17) -> CR0326 |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Filed |
| 2026-07-17 | Darren Benson (operator) / Claude Fable 5 | Decisions resolved at the RFC triage session; workstream CRs spawned (Accepted derives when they resolve) |
