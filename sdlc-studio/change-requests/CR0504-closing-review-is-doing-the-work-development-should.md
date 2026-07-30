# CR-0504: closing review is doing the work development should have done, and the same five defect classes recur every sprint

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/lessons/_index.md, .claude/skills/sdlc-studio/scripts/critic.py, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (operator-directed, from the EP0169/EP0172/EP0175 review round); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

Measured on the 2026-07-30 batch: 11 units, 47 points, every one delivered with full suites green, mutation evidence recorded and a per-unit Evidence section. Five independent reviewers then returned REJECT on all five groups - 14 MAJOR findings, one of which was a wrong number already committed to the tracked index. The reviews cost roughly 700k tokens and about 75 minutes of wall-clock. Almost none of the 14 needed a reviewer to find: they needed a census of the real corpus, a grep for the existing idiom, or a reading of the code against its own docstring. This is the same pattern the prior retros record, so the problem is not reviewer quality or author diligence, it is that the checks are positioned at the CLOSING gate rather than at the point the code is written. FIVE classes account for all 14, each attested two or three times in this one batch. (1) A NEW READER OF A SHARED FIELD DIVERGES FROM THE EXISTING IDIOM: the epic census compared the Epic field whole while transition, `verify_ac`, sprint, `ac_scope` and mutation all extract the id first; the supersession parser scraped ids from parentheticals while `decomposed_ids` strips them twenty lines below; `audit_cost`'s register folds last-row-wins while `run_row` takes the first. (2) A TEST THAT CAN AGREE WITH THE CODE BY CONSTRUCTION: the repo-wide epic sweep compared the index against the census that had produced it, and its own docstring claimed the opposite. (3) PROSE PROMISES WHAT THE CODE DOES NOT DO: `resolve_affects`'s docstring names the installed skill dir it never consults; the waiver key was documented directional and was not; two shipped documents promised a corrupt-file protection whose state was computed and never read. (4) NO SHAPE CENSUS BEFORE WRITING A PARSER: the dead-flag detector collapsed same-named functions in five modules that already have them, the epic header matched one literal spelling, the loading-guide checker skipped a whole table. Where a census WAS taken - the eleven supersession spellings - it found the specification's count wrong and shaped the implementation correctly. (5) A SIBLING LANE HAS THE GUARD AND THE NEW ONE DOES NOT: the lens-signature lane asserts its own flags and the ratchet lane does not, though the ratchet lane is the one whose defect motivated that guard.

## Impact

Who: every sprint run, and the operator's confidence in a green gate. What breaks: a delivered-and-green unit is not evidence of a working unit, so the closing review becomes the first real test rather than the last check - which is the most expensive place to find a defect and the place where finding one stalls a close. Three concrete costs measured on this batch: a wrong story count reached the permanent record and its justification cited a broken census; 47 points sat blocked at Review pending a repair round nobody had planned; and the reviews spent about 700k tokens re-deriving facts a ten-minute census would have produced before the code was written.

## Acceptance Criteria

- [ ] Each of the five classes is named in the doctrine as a pre-implementation obligation with the instances that attest it, so an author meets them before writing the code rather than meeting a reviewer who found them.
- [ ] The two mechanisable classes are DETECTORS, not checklist items: a divergent-reader check (a new read of a shared field or ledger that does not use the idiom every other reader of it uses) and a promise check (a docstring or shipped reference asserting a behaviour no code path implements). A checklist that only a diligent author reads is what the current five instances already got.
- [ ] The self-agreeing-test class is refused where it can be refused: an assertion that reads its expected value from the code under test is reported, because reference-review.md already names this class and one shipped anyway with a docstring claiming the opposite.
- [ ] A new gate lane is required to carry the guards its sibling lanes carry - a declared-inventory membership check over the baseline files and over each lane's own flags - so the ratchet-lane gap cannot recur silently.
- [ ] The design rung's output records the SHAPE CENSUS for any parser or matcher the unit adds: the real corpus's spellings, header forms and duplicate names, counted before implementation. Where the census contradicts the story's stated counts, the story is corrected rather than the census discarded - as it was for the supersession spellings, which is the one case in this batch that went right.

## Recommendation

Sequence it so the two detectors land before the prose: the classes documented without them are the state this CR exists to fix. The divergent-reader detector is the highest-value single item - three of the 14 MAJORs and the only committed data defect are that class, and it is mechanically checkable by comparing the readers of a named field across the scripts tree. Worth ruling during refine whether this supersedes or absorbs the existing design-rung work rather than adding a sixth ceremony; the prior retro on the design rung recorded that a rule RESTATED is not a rule DERIVED, which is the failure mode a documentation-only version of this would repeat.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (operator-directed, from the EP0169/EP0172/EP0175 review round) | Raised |
