# RFC-0058: Stakeholder feedback shapes the work: when, how often and at what cost the stakeholder personas are consulted

> **Status:** In Review
> **Decomposed-into:** EP0256
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio new
> **Raised-by:** operator request, RUN-01M2JA6J 2026-09-15 ("We need an RFC to increase use of feedback from stakeholders")
> **Size:** L
> **Priority:** High
> **Related:** CR0577 (a stakeholder consult gate), CR0571 (the unchecked ruler, found by a stakeholder consult), RFC0016 and RFC0028 (the persona engine and generated team), doctrine rule 7

## Summary

Stakeholder personas are consulted only when someone remembers. The one consult in RUN-01M2JA6J, run on the operator's prompt, found the batch's most important design gap, which four rounds of seat review had missed. This RFC decides where stakeholder feedback enters the lifecycle, how it is recorded and priced, and what enforces it, so it becomes a routine input rather than an occasional one.

## Context & Problem

The project runs two different kinds of reviewer, and uses one of them almost exclusively.

- **The seats** (qa, engineering, product) judge whether the work is built right: criteria that can fail, mutants that die, a diff that meets its criteria. They are briefed by `critic.py brief`, recorded in the verdict ledgers and enforced by gates at plan, Fixed/Done and close.
- **The stakeholder personas** (`sdlc-studio/personas/`: a founder-engineer, a team lead, an enterprise PM) judge whether the work serves the people it is for. They are reached through `/sdlc-studio consult stakeholders`, whose output is advisory and recorded nowhere a gate reads.

Doctrine rule 7 says to consult before freezing a design and to add the stakeholders when an artefact touches the running system. Nothing enforces it. The evidence from RUN-01M2JA6J:

- The batch's 23 units drew over 60 seat verdicts across up to six plan-review rounds each, and one stakeholder consult, which ran only because the operator asked when personas are consulted.
- That consult, over CR0526's four stories, returned one Reject and two Concerns. All three personas independently found that a stop-ship ruling is not checked against who may rule, so the session that did the work can release its own hold (now CR0571). No seat round raised it.
- It also produced three wording changes folded straight into delivery and seven candidate units. It cost one agent pass: less than a single plan-review round on one unit.

The seats measure correctness against criteria the author wrote. If the criteria encode the wrong intent, every seat approves a well-built wrong thing. Stakeholder feedback is the input that checks the intent, and today it arrives by accident.

## Goals / Non-Goals

**Goals**

- Stakeholder feedback reaches every unit whose intent it could change, at the point where acting on it is cheapest.
- A consult is recorded as an artefact, so its findings can be traced to what they changed and counted.
- The requirement is enforced in a command people run (LL0027), with a sanctioned skip that costs a written reason.
- Its cost is known and proportionate: the yield per consult is measured, as the seat reviews' yield is.

**Non-Goals**

- Replacing the seats. Correctness review stays theirs.
- Giving stakeholder personas a veto. Their verdicts inform; the operator rules (and CR0571 is about exactly who may rule).
- Deciding persona authoring or freshness (RFC0016, RFC0028 own that), beyond naming it as a risk below.

---

## Design Options

### Option A - Gate at plan

**Approach:** `sprint plan` refuses a story batch with no recorded stakeholder consult covering it, naming the uncovered stories. CR0577's shape.
**Pros:** Enforced where the batch is formed; cheap to build; one gate.
**Cons:** Arrives after refine and grooming, when the stories' shape is already set, so feedback costs rework; every story pays, including those a stakeholder would not care about.
**Effort / risk:** S-M. Risk: a gate people satisfy with a rubber-stamp consult.

### Option B - A stakeholder seat in plan review

**Approach:** One persona joins the QA seat on each story's test-plan round, briefed by `critic.py brief --seat stakeholder`.
**Pros:** Reuses the seat machinery (briefs, ledgers, verdict provenance, the round cap); feedback lands beside the criteria it would change.
**Cons:** Multiplies the most expensive loop in the process; a plan review judges test plans, a poor lens for "does this serve the user"; persona verdicts would start holding gates, which drifts toward the veto the non-goals exclude.
**Effort / risk:** M. Risk: round counts rise again.

### Option C - Consult upstream at refine or epic

**Approach:** `refine` (CR to epic and stories) runs a stakeholder consult over the epic and its stories once, before grooming, and records it against the epic.
**Pros:** Cheapest point to change intent; one consult covers a whole epic; findings become criteria rather than rework.
**Cons:** Misses stories filed outside refine and bugs whose fix changes user-facing behaviour; a design can drift after the consult.
**Effort / risk:** M. Risk: an epic-level consult too coarse to reach a story's specifics.

### Option D - Stakeholder acceptance at delivery

**Approach:** Beside the adversarial seats, a persona judges the delivered behaviour through the shipped entry point, "does this do what I needed", before the close.
**Pros:** Judges what was built, not what was planned; catches intent drift during delivery.
**Cons:** Latest and most expensive point to act; findings mostly become new units, not fixes.
**Effort / risk:** M. Risk: overlap with the product seat.

### Option E - Risk-proportional consult

**Approach:** A trigger selects which units must be consulted: the unit touches the running system, changes what a user reads, is refused or is told, originates in a stakeholder concern, or belongs to an epic no consult has covered. Units with no trigger skip without a reason.
**Pros:** Cost follows risk; most bugs (defects against settled intent) skip; the trigger is derivable from Affects and the unit type.
**Cons:** A derived trigger can be gamed or wrong; needs a definition of "user-facing" per project.
**Effort / risk:** M. Risk: the ceremony-proportionality problem this repository already has (route.estimate scores whole files).

---

## Recommendation

**RULED: C + E** (D1, D2 above; the operator did not take A's second gate at plan). The recommendation as written was **C + E, enforced by A**: consult the stakeholders on the epic or CR at refine time, where their feedback is cheapest to act on; require a per-story consult only when an E trigger fires; gate both in `sprint plan` (A), with a sanctioned skip that costs a reason and is reported at the close. Keep D as an optional delivery-time check for units whose intent changed during delivery. Reject B: it puts stakeholder verdicts in the loop that most needs fewer rounds, not more.

Record every consult as an artefact under `sdlc-studio/reviews/` naming the units it covered, each persona's verdict, and a disposition per finding (folded into delivery, filed as an id, or declined with a reason), so the same ledger discipline the seats follow applies here and yield can be measured.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | **RULED 2026-09-16 (operator):** at REFINE, per epic or CR - one consult over the epic and its stories before grooming, where feedback becomes criteria rather than rework. `plan` does not carry a second gate; a unit filed outside refine is reached by D2's trigger instead | Settled |
| D2 | **RULED 2026-09-16 (operator):** RISK-TRIGGERED - a unit is consulted when it touches the running system, changes what a user reads or is told, originates in a stakeholder concern, or belongs to an epic no consult has covered. Derived from `Affects` and the unit type, so most bugs (defects against settled intent) skip without a reason | Settled |
| D3 | What a consult artefact must carry for the gate to count it (units covered, verdicts, per-finding disposition) | Open |
| D4 | **RULED 2026-09-16 (operator):** INFORMS, and the operator rules. A stakeholder Reject holds no gate, but it must be ANSWERED in writing - folded into delivery, filed with an id, or declined with a reason - and an unanswered one is reported at the close. Consistent with D0194: the operator rules, the personas inform | Settled |
| D5 | Persona validity: synthetic personas speak for real users only as well as they were authored; how often they are refreshed against real feedback, and whether a real stakeholder can stand in for a persona | Open |
| D6 | How consult yield is measured (findings per consult, share folded or filed, cost against seat rounds) and when the requirement is revisited | Open |

## Evidence

- `sdlc-studio/reviews/consult-CR0526-stakeholders-2026-09-15.md`: the RUN-01M2JA6J consult and its findings.
- `sdlc-studio/reviews/plan-review-verdicts.md`: the seat rounds the same stories went through.
- CR0571 to CR0577: what that single consult produced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | Claude Opus 5 (authoring session) | Context, goals, five options weighed, recommendation and six open decisions written on the operator's request; filed under an operator-named triage session because the run's finding cap was reached |
| 2026-09-16 | Claude Opus 5 (authoring session) | D1, D2 and D4 ruled by the operator at the RUN-01M2JA6J close: consult at refine per epic or CR, a risk trigger derived from Affects and unit type, and a Reject that informs and must be answered but holds no gate. D3, D5 and D6 remain open for refine. |
