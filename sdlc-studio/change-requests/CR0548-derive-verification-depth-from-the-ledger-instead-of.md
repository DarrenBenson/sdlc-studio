# CR-0548: derive `Verification depth` from the ledger instead of authoring it - the field has been wrong on 5 of 6 units in one batch

> **Status:** Proposed
> **Priority:** High
> **Type:** enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Evidence:** RUN-01M0CT8P delivery review, 2026-08-19: 5 of 6 depth fields false; 8 of 34 recorded kills did not die on their own criterion's test.
> **Date:** 2026-08-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`Verification depth` is prose an author types, and almost everything in it is a fact the tooling already holds: how many criteria there are, how many mutants were declared, which were executed, which survived, whether the evidence went through the shipped entry point. A field nobody types cannot lie, and this one lies constantly - it is the single least reliable record in the workflow while being the one a reviewer reads first to decide how hard to look.

## Impact

A reviewer decides how hard to look from this field. When it overstates, review effort goes to the wrong unit; when it is corrected by hand the correction is as likely to be wrong as the original, which is exactly what happened twice on BG0592. It is also the field the close reads for the `Fixed` gate, so a false depth is a gate satisfied by a sentence.

## Acceptance Criteria

- [ ] Given a unit with a Test Plan and a mutation ledger, when its `Verification depth` is rendered, then every COUNT in it - criteria, declared rows, executed, killed, survived - is read from the ledger and the verify report rather than from prose
- [ ] Given a unit whose ledger says a row was never executed, when the field is rendered, then it SAYS so; a derived field that can only report success is the defect this replaces
- [ ] Given the author's judgement half - the tier, and what was deliberately not covered - when the field is regenerated, then that half is preserved verbatim inside its delimiters
- [ ] Given a hand-edit to the DERIVED half, when the gate runs, then it is refused and named, exactly as a hand-edited `_index.md` is
- [ ] Given BG0592 as it stood on 2026-08-19 - a field claiming shipped-CLI coverage that did not exist - when the field is derived instead, then the claim is absent, because nothing in the ledger supports it

## Steps to Reproduce

Measured on RUN-01M0CT8P, 2026-08-19: an independent QA review found that EVERY `Verification depth` field in the batch except BG0597's made a false factual claim about what had been executed and killed - five of six units. Eight of 34 rows the ledger recorded as `killed` did not die on the test their criterion named. Before that, BG0592's field was wrong FIVE TIMES RUNNING across three review rounds: criterion counts, mutant counts, and a claim of shipped-CLI coverage that did not exist. Each correction was itself written by hand and two were themselves wrong.

## Recommendation

Generate it, and refuse a hand-edit to the derived half the way `_index.md` is refused: the counts are derived output and reconcile syncs them. Keep the judgement half hand-written and clearly delimited, because the tier and the honest statement of what was not covered are the part no tool can supply.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-19 | sdlc-studio | Raised |
