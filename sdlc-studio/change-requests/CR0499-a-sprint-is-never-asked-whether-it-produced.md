# CR-0499: A sprint is never asked whether it produced a SHIPPABLE increment: the release definition-of-done encodes mechanism, not outcome

> **Status:** In Progress
> **Decomposed-into:** EP0221
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01KYNKDP: goal verdict `partial`, 8 stop-ship defects found by independent review, 3 units marked Fixed that deliver nothing - and all four Release DoD clauses would have gone green. `goal_panel` and `judge_defects_against_goal` each have exactly one caller (`sprint.close_goal_judgement`), both wired for the first time in this same run by BG0385; neither reaches `release_cut.tag_check`.
> **Date:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A sprint is supposed to produce a shippable increment. Nothing in this process ever asks whether it did.

The shipped Release definition-of-done has four clauses: the release gate is green, changelog fragments are composed, version strings agree, and a breaking change ships its migration story. Every one asks whether the MACHINERY is green. None asks the two questions that actually decide whether an increment ships:

1. Was the Sprint Goal achieved?
2. Is any open defect a stop-ship against it?

Both questions already have mechanisms. `critic.goal_panel` returns a per-clause verdict from a panel that excludes the author. `critic.judge_defects_against_goal` returns `{blocking, leavable}` judged against the goal's clauses - which IS the stop-ship question, by name. Both had ZERO callers until RUN-01KYNKDP wired them into the close (BG0385). Even now they report at the CLOSE, to inform a sign-off, and nothing carries either answer to the tag.

What actually gates a tag is `release_cut.tag_check`: a gate recorded green, on the commit being tagged, with no delivery unit owing a close. Mechanism, three times.

RUN-01KYNKDP is the evidence. Its goal verdict was recorded `partial`. Independent review then found eight stop-ship defects, five of them guards that fail OPEN, and three units marked Fixed that deliver nothing at all. Every mechanical clause was green: the gate passed, the fragments composed, the versions agreed. A release cut on that state would have been correct by the definition-of-done and wrong by every standard that matters.

A constraint the remedy must state rather than assume: `judge_defects_against_goal` reads OPEN defects from the workspace, so it is only ever as good as what has been FILED. Run before this run's review findings were filed, it reports zero blocking - a clean release verdict over a batch with eight stop-ships.

## Impact

A sprint's whole purpose is to produce a shippable increment, and the release gate is the one moment that claim is tested. Today it tests the machinery instead: green gate, composed fragments, agreeing versions. All three can be true of an increment that missed its goal and carries defects nobody should ship.

This is not hypothetical. RUN-01KYNKDP would have passed every mechanical clause with a partial goal verdict, eight stop-ship defects and three units falsely marked Fixed. The operator caught it by asking the two questions by hand. A process that depends on the operator remembering to ask is the failure mode this project exists to remove - and the answer is worse for a consuming project, which inherits the shipped DoD and has no operator who knows to ask.

The mechanisms are already built and already correct. What is missing is the clause that makes anyone run them before a tag.

## Acceptance Criteria

- [ ] The shipped Release definition-of-done carries a clause asserting the increment is shippable, in the same form and with a check tag like its existing mechanical clauses.
- [ ] The goal half is DERIVED from the recorded sprint goal verdict, never re-asked at release time - so the tag cannot get a softer answer than the close did.
- [ ] The defect half calls `critic.judge_defects_against_goal` with the run's own goal clauses, so the release and the close cannot disagree about which defects block.
- [ ] `release_cut.tag_check` refuses a tag when either half fails, naming which half, the verdict or the blocking defects, and what would clear it.
- [ ] A `partial` or `missed` verdict can still be released as an explicitly RECORDED operator decision, in the shape `file-and-close` already uses - so a knowingly partial release is stated on the record and a silent one is impossible.
- [ ] The defect judgement reports its own LOWER BOUND: when findings exist that have not been filed as artefacts, it says so rather than reporting zero blocking, because an unfiled finding is not an absent one.
- [ ] A project that has adopted no definition-of-done inherits the clause from the shipped template, since the gap is what every consuming project inherits rather than a local omission.

## Steps to Reproduce

1. Read the `## Release` section of `templates/core/definition-of-done.md`: four clauses, all mechanical.
2. `grep -rn 'goal_panel(\|judge_defects_against_goal' --include=*.py .claude/` - one production caller each, both `sprint.close_goal_judgement`, neither reachable from the release path.
3. Read `release_cut.tag_check`: it refuses on a missing gate-green marker, a commit mismatch, and an owed close. It never reads the goal verdict or any defect judgement.
4. On RUN-01KYNKDP: `sprint_goal_verdict` is `partial`; independent review found 8 stop-ship defects; `gate.py --release`, `changelog.py check` and `check_versions.py` are all green.

## Proposed Fix

Add the missing clause and DERIVE both halves from facts the process already records.

1. **The clause.** Add to the shipped Release DoD, in the form its existing clauses use:
   `- [ ] The increment is SHIPPABLE: the Sprint Goal was achieved, and no open defect is blocking against it [check: release.shippable]`

2. **The goal half is read, never re-asked.** Take `sprint_goal_verdict` from the run state. `achieved` passes; `partial` or `missed` does not. Re-asking at release time would invite a second, softer answer from whoever is holding the tag.

3. **The defect half is the close's own judgement.** Call `critic.judge_defects_against_goal` over the open defects with the run's goal clauses - the same function, the same clauses, so the release cannot disagree with the close about which defects block.

4. **`tag_check` refuses on either half**, naming which one and why, alongside its existing three refusals.

5. **A partial increment can still be released - as a RECORDED decision.** A `missed` or `partial` verdict is not a permanent bar; it is the operator's call, taken deliberately and stated, in the shape `file-and-close` already uses for a bounded exit. What must never happen is a partial increment shipping SILENTLY because nothing asked.

6. **State the lower bound.** The defect half can only see filed defects. It must report how many findings are unfiled - or that it cannot tell - rather than reporting zero blocking over a review whose findings are still in someone's head. An unfiled finding is not an absent one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Raised |
