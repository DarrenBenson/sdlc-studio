# CR-0099: goal plan consults the review seats for WSJF inputs and defaults to WSJF order

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

**Estimate: 5 points. Folded in from a planning-run learning (LL0007).** A dogfooded plan was
ordered by the bare `Priority` field, with effort/priority set solo - missing the value/risk
perspective the review seats exist to provide. Sprint planning is a value/effort/risk
judgement. Make `--goal plan` **consult the review seats** for the WSJF inputs - **Product
Owner** for value (+ time-criticality, risk-reduction), **Engineering** for effort (seeded by
the RFC0009 complexity signal), **QA** for risk - and **order by WSJF** by default. Today
`--order wsjf` exists but is thin (priority-primary, complexity as the size tiebreak): it has
the denominator (size) but not the value/risk numerator. This supplies it from the seats.

## Acceptance Criteria

- [ ] `--goal plan` consults the PO/Eng/QA review seats (the existing isolated-subagent
      consult, CR0060) to score value / effort / risk per unit; consult is recorded
- [ ] WSJF = (value + time-criticality + risk-reduction) / size; size seeded by the complexity
      signal (RFC0009); `--goal plan` orders by WSJF by default (overridable to priority/manual)
- [ ] the sprint-plan artifact (CR0091) records the per-unit value/effort/risk + WSJF score
- [ ] degrades gracefully when no personas/seats exist (falls back to the current
      priority+complexity WSJF); `--skip-personas` honoured
- [ ] unit tests cover the WSJF computation + the seat-input wiring; CHANGELOG entry (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
