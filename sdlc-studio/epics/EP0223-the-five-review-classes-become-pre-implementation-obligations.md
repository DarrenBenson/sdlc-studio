# EP0223: The five review classes become pre-implementation obligations, and two of them become detectors

> **Status:** Draft
> **Derived Point Total:** 21
> **Parent:** CR0504
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0504. Delivers the work CR0504 requested.

## Story Breakdown

- [ ] [US0712: The doctrine names each of the five classes as a pre-implementation obligation with its attesting instances](../stories/US0712-the-doctrine-names-each-of-the-five-classes.md)
- [ ] [US0713: A divergent-reader DETECTOR reports a new read of a shared field that does not use the established idiom](../stories/US0713-a-divergent-reader-detector-reports-a-new-read.md)
- [ ] [US0714: A self-agreeing test is REFUSED where an assertion reads its expected value from the code under test](../stories/US0714-a-self-agreeing-test-is-refused-where-an.md)
- [ ] [US0715: A new gate lane must carry the declared-inventory guards its sibling lanes carry](../stories/US0715-a-new-gate-lane-must-carry-the-declared.md)
- [ ] [US0716: The design rung records a SHAPE CENSUS for any parser or matcher a unit adds, counted before implementation](../stories/US0716-the-design-rung-records-a-shape-census-for.md)

## Acceptance Criteria (Epic Level)

- [ ] Each of the five classes is named in the doctrine as a pre-implementation obligation with the instances that attest it, so an author meets them before writing the code rather than meeting a reviewer who found them.
- [ ] The two mechanisable classes are DETECTORS, not checklist items: a divergent-reader check (a new read of a shared field or ledger that does not use the idiom every other reader of it uses) and a promise check (a docstring or shipped reference asserting a behaviour no code path implements). A checklist that only a diligent author reads is what the current five instances already got.
- [ ] The self-agreeing-test class is refused where it can be refused: an assertion that reads its expected value from the code under test is reported, because reference-review.md already names this class and one shipped anyway with a docstring claiming the opposite.
- [ ] A new gate lane is required to carry the guards its sibling lanes carry - a declared-inventory membership check over the baseline files and over each lane's own flags - so the ratchet-lane gap cannot recur silently.
- [ ] The design rung's output records the SHAPE CENSUS for any parser or matcher the unit adds: the real corpus's spellings, header forms and duplicate names, counted before implementation. Where the census contradicts the story's stated counts, the story is corrected rather than the census discarded - as it was for the supersession spellings, which is the one case in this batch that went right.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
