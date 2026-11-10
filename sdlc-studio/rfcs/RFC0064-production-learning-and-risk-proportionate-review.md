# RFC-0064: Production learning and risk-proportionate review

> **Status:** Draft
> **Decomposed-into:** CR0695, CR0696
> **Priority:** High
> **Size:** L
> **Author:** Darren Benson (operator); drafted with Claude Opus 5.5
> **Date:** 2026-11-10
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio new
> **Raised-by:** Darren Benson (operator); human; v1
> **Serves:** O10, O12; Abena Osei, End goals 1 and 4; Graham Doyle, End goals 1 and 3
> **Spans:** sdlc-studio (bug and incident records, lessons and failure classes, briefs, the plan, the sprint report and scorecard, the change evidence pack)
> **Related:** RFC0063 (WS4, WS6), RFC0062, EP0287, CR0691, CR0692, CR0693
> **Supersedes / Superseded by:** none

## Summary

What happens in production does not reach the next build, and every change reaches the change board
with the same weight whatever its risk. This RFC proposes three things. Incidents and their root causes
are taken in and turned into failure classes or lessons that agents read. Change failure rate is
measured beside escapes per 100 points. Each unit carries a risk and compliance class that focuses
human review and groups the change evidence pack. Five decisions of form are open; none adds a human
approval on every change.

## Context & Problem

- **Escapes are counted, not learned from.** O12 and RFC0063's WS6 count a defect that escapes to
  production, and the scorecard WS6 plans counts escapes per seat and model. Nothing carries what
  caused an escape back into building. The bug template's Root Cause Analysis section is free text,
  and no field marks a bug as a production escape or ties it to the unit, verdict and release that
  let it through (CR0693).
- **Every change weighs the same.** A change to payments or personal data reaches the change board
  with the same evidence and the same review as a wording fix. Graham Doyle approves from one document
  (End goal 1) and wants fewer surprises in production (End goal 3). A pack that does not separate
  high-risk changes makes him read everything with the same care, or none.
- **Change failure rate is not measured.** The report states cost, rounds and known issues, but not how
  many releases caused a failure in production, so no change to the process can be judged by the
  outcome Graham cares about.
- **The published case.** A published case of agent-driven delivery reported a 31% lower change failure
  rate. It credited reliability, observability and review agents drawing on production incident history,
  together, plus human review focused by risk and compliance class. It is one case, and it credits the
  combination, not any one part. This RFC adopts the measures and the mechanisms to try, not the
  number.

## Goals / Non-Goals

**Goals**

- An incident's root cause reaches the next plan, build and review (O12; Abena Osei, End goal 4).
- Change failure rate is on the report and the scorecard, beside escapes per 100 points.
- Each unit carries a risk and compliance class, and the change evidence pack is grouped by it (O10;
  Abena Osei, End goal 1; Graham Doyle, End goal 1).

**Non-Goals**

- A human approval on every change. Trevor Hale's card excludes it (End goal 2, stated to exclude).
- A gate without a named yield (O5; Abena Osei, End goal 6).
- Sync with an external tracker or incident tool as the system of record. An import may feed the
  record (D1); the committed record stays the source.

---

## Design Options

### Option A - Measure only

**Approach:** Add change failure rate and escapes per 100 points to the report and scorecard; leave
incident learning to retros and review weight uniform.
**Pros:** Small; no new artefact and no brief growth.
**Cons:** Shows the outcome without changing it; a high-risk change still gets the same review as any
other.
**Effort / risk:** S; low.

### Option B - Learn, measure and weight review by risk (recommended)

**Approach:** All three workstreams below: incident intake into failure classes or lessons that reach
briefs or the plan, change failure rate measured, and a risk and compliance class on each unit that
groups the evidence pack and may add review for the high-risk class.
**Pros:** Matches the combination the published case credits; each part serves a named End goal.
**Cons:** Brief growth against RFC0062's budget (D2); a misclassified unit gets less care (D4).
**Effort / risk:** L; medium.

### Option C - Import from an external incident tool only

**Approach:** Read incidents and deploys from the team's existing incident and deploy tools; add no
record of our own.
**Pros:** No double entry for a team that already runs such tools.
**Cons:** A team without one gets nothing, and the record the change board reads would depend on a
system outside the committed tree.
**Effort / risk:** M; medium. D1 keeps an import as one form of the record rather than the whole design.

---

## Recommendation

Option B, built in the order of the workstreams, with each open decision settled before the workstream
that depends on it.

## Open Decisions

| # | Decision | Options | Owner | How it resolves | Status |
| --- | --- | --- | --- | --- | --- |
| D1 | The incident record's form | A new artefact type; an issue triaged with a root-cause section; an import from an external incident tool | Operator | Operator call after the engineering seat's view | Resolved: Decided by the operator (D0457): an incident is an issue with a root-cause section, triaged into escaped bugs naming the release, unit and verdict; no new artefact type; an import may later feed issues -> CR0693 |
| D2 | How a root cause reaches agents | A failure class or lesson injected into briefs; a library queried at plan time. Weighed against RFC0062's context budget | Engineering seat | Measure each option's brief cost on a fixture, then operator | Open |
| D3 | The source for change failure rate | The deploy log plus incidents linked to a release; and who records a deploy | Operator | Operator call | Resolved: Decided by the operator (D0458): a release is the deploy; change failure rate is releases with a linked incident over releases, recorded by the release cut -> CR0695 |
| D4 | Who sets the risk level and compliance flag | Refine proposes and a human confirms; or a declared map of components (payments, personal data) | Operator | Operator call | Resolved: Decided by the operator (D0459): a declared component map proposes the class at refine, the plan flags a disagreeing tag, the operator confirms at plan approval -> CR0696 |
| D5 | What a risk class changes | Grouping in the change evidence pack only; extra review for high-risk units; or both. A human approval on every change stays out (Trevor Hale's card) | Operator | Operator call | Resolved: Decided by the operator (D0460): both; the pack lists high-risk changes first and high-risk units get a second review seat whose yield each retro reports; no approval on every change -> CR0692, CR0696 |

---

## Architecture Impact

| Layer / System | Impact | Change Type |
| --- | --- | --- |
| Bug and incident records | A production escape is marked and linked to its unit, verdict and release; an incident record in D1's form | Enhancement or New (D1) |
| Lessons and failure classes | An escape's root cause becomes a failure class or lesson | Enhancement |
| `critic.py brief`, the lane brief or the plan | Carries the root causes that apply to the unit (D2) | Enhancement |
| `sprint_report.py`, the scorecard | Change failure rate beside escapes per 100 points | Enhancement |
| Refine, the unit header | A risk and compliance class on each unit (D4) | Enhancement |
| The change evidence pack (CR0692) | Grouped by risk and compliance class (D5) | Enhancement |

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Briefs grow and cost per point rises | Medium | High | D2 is weighed against RFC0062's budget; inject only what applies to the unit's Affects |
| A misclassified unit gets less care | Medium | High | D4: a human confirms, or a declared component map; the default is the higher class |
| Ceremony creeps back through the high-risk class | Medium | Medium | D5 keeps a human approval on every change out; each added step names its yield (O5) |
| One published case is read as proof | Low | Medium | Adopt the measures, not the number; judge by our own change failure rate over time |

---

## Phased Plan / Workstreams

| WS | Workstream | Repo | Becomes | Depends on |
| --- | --- | --- | --- | --- |
| WS1 | Incident intake: an incident and its root cause become a failure class or lesson that reaches the next plan, build and review | sdlc-studio | CR0693 (RFC0063 WS6's escape loop) | D2; D1 decided (D0457); EP0280 |
| WS2 | Change failure rate on the report and the scorecard, beside escapes per 100 points | sdlc-studio | CR0695 | WS1; D3 decided (D0458) |
| WS3 | A risk and compliance class on each unit, with the change evidence pack grouped by it | sdlc-studio | CR0696 for the class at refine and the second review seat; CR0692 (RFC0063 WS4's evidence pack) for the grouping | D4, D5 decided (D0459, D0460) |

CR0691 (the engineering seat's reliability and observability checks) is RFC0063's, filed beside this
RFC as the review half of the combination the published case credits.

---

## Decision

> *Filled on acceptance.*

**Outcome:** pending `rfc decide`
**Rationale:** pending
**Spawned CRs:** pending

---

## Related Artifacts

| Kind | ID | Title | Status | Relationship |
| --- | --- | --- | --- | --- |
| RFC | RFC0063 | Human in the lead | Draft | parent direction: WS4 (evidence pack) and WS6 (escape loop) wait on D1, D4 and D5 here |
| RFC | RFC0062 | Token-efficient delivery | Draft | the context budget D2 is weighed against |
| EP | EP0287 | Personas become accountable team members | Draft | the scorecard WS2 extends |
| CR | CR0691 | The engineering seat's brief carries reliability and observability checks | Proposed | sibling: the review half |
| CR | CR0692 | A change evidence pack per release | Proposed | WS3: groups by class, high-risk first (D0460) |
| CR | CR0693 | An escaped defect is traced and its cause reaches the next build | Proposed | WS1; depends on D2 |
| CR | CR0695 | Change failure rate on the report and the scorecard | Proposed | WS2 (D0458) |
| CR | CR0696 | A risk and compliance class on each unit, and a second review seat for a high class | Proposed | WS3 (D0459, D0460) |

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator); drafted with Claude Opus 5.5 | RFC filed from the operator's brief: problem, three options, five open decisions (D1-D5), three workstreams; RFC0063's WS4 and WS6 CRs filed as CR0692 and CR0693 with their dependency on D1, D4 and D5 recorded (D0456) |
| 2026-11-10 | rfc resolve (operator decision) | resolve: D1 - Decided by the operator (D0457): an incident is an issue with a root-cause section, triaged into escaped bugs naming the release, unit and verdict; no new artefact type; an import may later feed issues |
| 2026-11-10 | rfc resolve (operator decision) | resolve: D3 - Decided by the operator (D0458): a release is the deploy; change failure rate is releases with a linked incident over releases, recorded by the release cut |
| 2026-11-10 | rfc resolve (operator decision) | resolve: D4 - Decided by the operator (D0459): a declared component map proposes the class at refine, the plan flags a disagreeing tag, the operator confirms at plan approval |
| 2026-11-10 | rfc resolve (operator decision) | resolve: D5 - Decided by the operator (D0460): both; the pack lists high-risk changes first and high-risk units get a second review seat whose yield each retro reports; no approval on every change |
