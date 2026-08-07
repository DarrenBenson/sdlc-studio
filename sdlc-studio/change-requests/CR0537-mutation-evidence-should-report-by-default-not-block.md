# CR-0537: mutation evidence should REPORT by default, not block: a surviving mutant becomes a severity-rated bug and the close proceeds

> **Status:** In Progress
> **Decomposed-into:** EP0212
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07. Three review rounds over one 19-unit batch. Round 1 rejected 5 of 6 reviewed units, round 2 rejected 3 of 5, and the repairs cost roughly a dozen commits and as many full-suite runs. Operator's judgement, recorded verbatim: the guard-that-cannot-fail bar is too high, we would not do this in real life; happy to check for mutants but raise bugs and close, with severities, so the operator fixes next sprint or lives with them - speed and decision making rather than constant tail chasing trying to gold plate everything.
> **Date:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The mutation-evidence rule currently BLOCKS. A criterion whose named mutant survives holds the unit, which holds the close, so the run cannot finish until every survivor is repaired. The operator's judgement - is this worth fixing now, next sprint, or ever? - is never asked for, because the gate has already decided the answer is now.

The cost is real and was measured on RUN-01KZCAJX. Three rounds of independent review over one batch, each round finding surviving mutants, each finding producing a repair commit and a fresh full-suite run at roughly eleven minutes apiece. The findings were genuine. What was wrong was that every one of them, regardless of severity, had the same consequence: stop everything.

That is gold-plating enforced by machinery. A surviving mutant on a refusal path that guards a release is not the same fact as a surviving mutant on a line that formats a report, and a gate that treats them identically teaches the operator that the gate's opinion is worthless rather than that the finding matters.

The proposal: keep the check, drop the block. A survivor becomes a filed Bug carrying a severity, the close proceeds, and the operator schedules it or accepts it - which is what a team does in real life, and what every other advisory lane in this repo already does.

## Impact

Every project, on every run. Today the strictest possible reading of test quality is compulsory and unpriced; the operator cannot trade it against delivery even deliberately. This CR moves that decision from the tool to the person, which is the repo's own stated model - human-in-the-lead, the machine reporting rather than deciding.

## Acceptance Criteria

- [ ] `review.mutation_evidence` takes `report` (the DEFAULT), `block`, or `off`, and the resolved value is printed by the close so nobody has to guess which mode a run was held to
- [ ] In `report` mode a surviving mutant is FILED as a bug through the shipped filer - naming the unit, the criterion, the mutant and the test that failed to kill it - and the close PROCEEDS; nothing about the run is held
- [ ] A filed survivor carries a derived severity rather than a uniform one, so triage has something to sort on: a survivor on a refusal or gate path outranks one on a reporting path, which outranks one on prose
- [ ] `block` remains available and behaves exactly as today, so a project that wants the hard bar keeps it by setting one value
- [ ] The retro counts survivors filed, by severity, so the trade being made is visible over time rather than felt
- [ ] Re-filing is idempotent: the same surviving mutant on the same unit does not mint a second bug on the next run
- [ ] One thing still blocks in every mode: a mutant RECORDED as killed that is shown to survive. That is not a quality bar, it is the ledger lying about itself, and this run produced exactly one

## Recommendation

Default to `report`. `off` should exist but should not be the default - the evidence is cheap to COLLECT and expensive only to ACT on, and a project that has switched the check off entirely cannot later tell whether its tests degraded.

The one carve-out to argue for is the last criterion. A surviving mutant is a quality finding and belongs in the backlog. A ledger entry that says `killed` about a mutant that lives is a false measurement, and every figure derived from it is wrong - that should still refuse whatever the mode, because it is not a bar being lowered, it is an instrument being trusted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | Darren Benson | Raised |
