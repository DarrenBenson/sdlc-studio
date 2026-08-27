# CR-0529: the prior-art check is scoped to the reviewer, so an author rediscovers by being rejected what one command would have told them

> **Status:** In Progress
> **Decomposed-into:** EP0229
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/critic.py, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

AGENTS.md already tells a REVIEWER to settle a question by execution rather than impression, naming `git log -S`. Nothing asks the AUTHOR the same question before the work starts, and the corpus is now 637 stories, 513 bugs and 528 change requests - 1,678 records of what somebody believed on the day they wrote it.

Three defects in RUN-01KZ56M6 and RUN-01KZ5YXM were prior-art failures, each caught by a review pass rather than at authoring:

- BG0477's drafted criterion would have reinstated the defect commit 7ef88707 deliberately removed. `git log -S redistribute_note` says so in one command.
- BG0501's filed fix did not fix BG0501: the shared reader it prescribed could not read the field either. One call settles it.
- US0487 added an artefact type without reading `reference-schema.md`, which is a VERSIONED contract; five guards said so afterwards, costing four gate refusals for one doc read.

The fix is narrow on purpose. Bulk reading of the artefact corpus is NOT proposed and is the wrong answer: BG0485 is the counter-example, where its parent BG0402 records `two halves not yet fixed` and reading that artefact would have confirmed the wrong thing with confidence, because the fix had landed four days before the bug was filed and no marker distinguishes a stale record from a current one. Artefacts record belief; code and history record what happened.

## Impact

The cost is paid as review rounds. Each of the three above was found by a seat and returned to the author, so the work was done twice and the second pass carried a REJECT. It is the expensive half of a cheap question, and it scales with the corpus: 1,678 records today, growing every run.

## Acceptance Criteria

- [ ] The toolchain runbook's DELIVER section names the prior-art check as a step, with the command beside the hand-rolled shape it replaces, so an author reading the row for the step they are on meets it before starting rather than after being rejected.
- [ ] The check names BOTH halves, because the three recorded failures split across them: `git log -S <symbol>` for a symbol the author did not write, and the one reference doc governing the surface being changed - US0487's was `reference-schema.md`, a versioned contract, and reading it was worth four gate refusals.
- [ ] The guidance states plainly that an artefact records BELIEF and history records what happened, and that where they disagree the history wins - BG0485's parent asserted a defect that had been fixed four days before the bug was filed, so a rule that sent an author to the corpus first would have confirmed the wrong thing.
- [ ] Reading the artefact corpus in bulk is explicitly NOT the instruction, and the row says so, because 1,678 records cannot be read per unit and the attempt would push authors back to whichever few they happened to pick.
- [ ] Whether `critic.py brief` gains an author-facing form is decided and recorded either way - the claim-inventory machinery already exists and only its audience is fixed, so declining it is a choice that should be visible rather than an omission.

## Recommendation

Two bounded moves, both already half-present. First, add a DELIVER row to the toolchain runbook naming the prior-art check beside the hand-rolled shape it replaces: `git log -S <symbol>` before altering a symbol you did not write, and the one reference doc governing the surface you are about to change. The runbook is read per step and is where an author looks. Second, consider extending `critic.py brief` - which already carries the claim-inventory pass for a reviewer - so the same inventory can be printed FOR the author before the work, since the machinery exists and only its audience is fixed. Explicitly out of scope: reading the artefact corpus in bulk, and any check that treats an artefact's prose as authority over the code.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Raised |
