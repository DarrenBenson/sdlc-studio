# EP0287: Personas become accountable team members: a review standard that blocks a failing card, a committed memory, a learning loop from the verdict ledger, and End goals checked at the close

> **Status:** Draft
> **Parent:** CR0634
> **Parent:** CR0629
> **Parent:** CR0633
> **Parent:** CR0632
> **Derived Point Total:** 92
> **Parent:** CR0631
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0631. Delivers the work CR0631 requested.

## Story Breakdown

- [ ] [US1052: The persona standard names every rule a card is held to, and persona_review check reports each card against it](../stories/US1052-the-persona-standard-names-every-rule-a-card.md)
- [ ] [US1053: persona_review briefs another seat to review a card against the standard and records its verdict against the card's bytes](../stories/US1053-persona-review-briefs-another-seat-to-review-a.md)
- [ ] [US1054: The shipped product card names no Primary, so a project's copy of it passes the standard after an upgrade](../stories/US1054-the-shipped-product-card-names-no-primary-so.md)
- [ ] [US1055: A persona card that fails the standard is refused at every entry point that resolves it, naming each failed rule and its remedy](../stories/US1055-a-persona-card-that-fails-the-standard-is.md)
- [ ] [US1056: The goal review refuses to brief from a traced persona card that fails the standard](../stories/US1056-the-goal-review-refuses-to-brief-from-a.md)
- [ ] [US1057: Sprint plan names each blocked persona card with its remedy and each card owed a review, and the release cut names the owed reviews](../stories/US1057-sprint-plan-names-each-blocked-persona-card-with.md)
- [ ] [US1058: persona_memory.py keeps each persona's evidenced learnings in a committed memory file beside its card](../stories/US1058-persona-memory-py-keeps-each-persona-s-evidenced.md)
- [ ] [US1059: A persona's brief carries its own live learnings, capped and ranked, and never another persona's](../stories/US1059-a-persona-s-brief-carries-its-own-live.md)
- [ ] [US1060: A learning past its horizon is reported at the close until it is revalidated or retired, and the persona review reports memory problems](../stories/US1060-a-learning-past-its-horizon-is-reported-at.md)
- [ ] [US1061: A unit's review record names the seat that built it, so an author's repairs can be scored](../stories/US1061-a-unit-s-review-record-names-the-seat.md)
- [ ] [US1062: retro.py seats scores each seat on its own verdicts and authored units from the ledger](../stories/US1062-retro-py-seats-scores-each-seat-on-its.md)
- [ ] [US1063: The seat record reads each verdict's source and the operator rulings that name the seat](../stories/US1063-the-seat-record-reads-each-verdict-s-source.md)
- [ ] [US1064: The seat record charges a later bug to the approval that missed it, by the narrow rule](../stories/US1064-the-seat-record-charges-a-later-bug-to.md)
- [ ] [US1065: Each seat writes its learning in its own words from a brief carrying its record, and it is recorded as proposed](../stories/US1065-each-seat-writes-its-learning-in-its-own.md)
- [ ] [US1066: Another seat approves or rejects each proposed learning against its evidence and its card](../stories/US1066-another-seat-approves-or-rejects-each-proposed-learning.md)
- [ ] [US1067: The close lists every learning about to go live on the retro, with what it addresses and who approved it](../stories/US1067-the-close-lists-every-learning-about-to-go.md)
- [ ] [US1068: A learning reaches a brief only once a signed close has listed it, and one the operator strikes at the signature never does](../stories/US1068-a-learning-reaches-a-brief-only-once-a.md)
- [ ] [US1069: The close runs each traced persona's executable End goal Verify and records the result beside the goal verdict](../stories/US1069-the-close-runs-each-traced-persona-s-executable.md)
- [ ] [US1070: The sprint report shows each traced End goal's result beside the goal verdict](../stories/US1070-the-sprint-report-shows-each-traced-end-goal.md)
- [ ] [US1071: The plan runs the traced End goals once, so the close can say which turned green in the run](../stories/US1071-the-plan-runs-the-traced-end-goals-once.md)
- [ ] [US1072: The close records each traced persona's served-goal outcome in its memory, with its run](../stories/US1072-the-close-records-each-traced-persona-s-served.md)
- [ ] [US1073: A user persona writes its learning from its usage evidence, approved by a seat, and the goal review carries it](../stories/US1073-a-user-persona-writes-its-learning-from-its.md)
- [ ] [US1074: A generalisable seat learning is promoted into the skill source's shipped amigo card, and refused into an installed copy](../stories/US1074-a-generalisable-seat-learning-is-promoted-into-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A new or changed persona card that fails the standard is refused by `persona_resolve` until fixed, naming each failed rule
- [ ] The persona review runs on every card change and once per release, recorded with the reviewing seat and the outcome

### From CR0632

- [ ] A persona's brief carries its own approved learnings, capped and ranked, and never another persona's
- [ ] A learning past its horizon is reported at the close until it is revalidated or retired

### From CR0633

- [ ] A retro proposes, for each seat that reviewed in the run, the evidence of its verdicts against outcomes, and records the learning that seat wrote with the approving seat
- [ ] A learning the operator strikes on the signed retro never reaches the persona's brief

### From CR0629

- [ ] Given a Sprint Goal that traces to a persona whose End goal carries an executable Verify, when the run closes, then the goal verdict records that Verify's result beside the seats' `done_means`, and a red result is reported by name rather than read as met.

### From CR0634

- [ ] A user persona's memory records a served-goal outcome as evidence with its run
- [ ] Promoting a persona learning writes only to the skill source checkout and is refused into an installed copy

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
