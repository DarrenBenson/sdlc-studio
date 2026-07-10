# CR-0232: engagement floor, prose half: the doctrine states the mandatory planning rule

> **Status:** Complete
> **Verification depth:** functional (prose rule shipped in doctrine rule 16, agent-instructions template, and reference-config key table; grep confirmed no surviving unqualified scale-to-size sentence in sprint/code/SKILL surfaces; guards + 1630 tests green; the rule's wording is the exact discipline the mandated benchmark arm measured)
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

Split from CR0229 per operator so v4 ships consistent with its own published evidence (docs/benchmarks/2026-07-10-v4-rerun.md addendum: mandate took Sonnet 5/5 -> 1/5 escapes and Opus 3/3 -> 0/5 at 1.07-1.18x tokens; judgement-gated engagement was as bad as or worse than no process on both base models). Ship the FLOOR AS PROSE in v4: the doctrine and the shipped agent-instructions template state, as a hard rule rather than judgement guidance, that a multi-file change in a spec-bearing repo requires the planning pass (spec delta naming each interacting existing rule + acceptance criteria, one per interaction) BEFORE code - the exact discipline the mandated benchmark arm proved. Scale-to-size judgement remains for single-file/no-spec changes. A config opt-out (`engagement_floor`: judgement) is named for operators who accept the risk. The mechanical enforcement stays CR0229 (v4.1).

## Acceptance Criteria

- [x] reference-doctrine.md states the engagement floor as a numbered hard rule: multi-file change + spec-bearing repo -> mandatory spec-delta/AC pass before code, with the interacting-rules requirement and the config opt-out named
- [x] templates/agent-instructions.md carries the same rule so every consuming project inherits it; the benchmark report is cited as the why
- [x] reference-sprint.md and reference-code.md plan steps reference the floor where they describe when planning may be skipped (no contradicting scale-to-size sentence survives unqualified)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-10 | Claude (sprint driver) | AC3 note: sprint/code references carried no unqualified skip-planning sentence (grep clean); the floor lives in doctrine + template + config docs |
