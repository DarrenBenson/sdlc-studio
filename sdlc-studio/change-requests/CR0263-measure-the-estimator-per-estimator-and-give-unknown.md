# CR-0263: Measure the estimator, per estimator - and give "unknown" a first-class value

> **Status:** Complete
> **Priority:** P2
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Depends on:** BG0140, CR0262
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Delivered-by:** claude-opus-4-8

## Summary

The loop records the forecast, the actual, and (CR0261) the model. It does not record WHO estimated a unit, so it cannot tell an operator whether THEIR judgement is any good - it can only quote a population average from the literature, which is a statement about what estimation typically is, not about what any individual can do. That distinction was got wrong in CR0262 and corrected: the empirical finding (medium-or-low correlation in 93% of projects) measures, to an unknown degree, HOW MUCH PEOPLE CARE rather than how well they could estimate if they did. An engineer does not want to estimate; they want to write code. Low engagement and low capability produce an identical correlation and the study cannot separate them.

This does not need assuming. It can be measured. Record the estimator alongside the estimate, and the tool can report per-person accuracy against measured actuals: "your S/M/L calls run at r = 0.61, the auto-estimate at 0.30 - trust yours", and name the classes of unit an individual systematically under-calls. Feedback on your own past calls is the one intervention known to improve human estimation, and here it is nearly free.

THE COERCION HAZARD, which is the urgent half. BG0136 shipped TODAY and made Effort MANDATORY at filing. If estimating is a chore, a compulsory estimate produces a CARELESS estimate - and a careless estimate is strictly worse than none, because it looks like data and is averaged into a forecast. The grooming gate may be manufacturing precisely the noise it exists to remove. Testable, not arguable: compare the accuracy of Effort values recorded BEFORE the gate made them compulsory against those recorded after.

## Impact

Every estimate the project takes, and the credibility of the whole sizing loop. A tool that demands a number it never checks teaches people to supply a number that does not mean anything. A tool that shows you your own hit rate teaches you to estimate - and tells the operator, on evidence, whose judgement to weight.

**Effort:** M

## Acceptance Criteria

- [ ] The estimate records WHO made it, and the accuracy report is segmented per estimator, so a human can see their own hit rate against measured actuals rather than a population average from a study of other people.
- [ ] The report names the classes of unit an estimator systematically under-calls or over-calls, since directional bias is correctable and a raw correlation is not.
- [ ] "Unknown" is a first-class Effort value that satisfies the grooming gate. Nobody has to invent a size to get past a gate, and an honest unknown is never averaged into a forecast as though it were an estimate.
- [ ] The accuracy of Effort values recorded BEFORE the grooming gate made them compulsory is compared against those recorded after, so the coercion hazard is answered with evidence rather than opinion.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
