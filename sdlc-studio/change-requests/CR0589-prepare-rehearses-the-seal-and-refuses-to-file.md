# CR-0589: PREPARE rehearses the seal, and refuses to file a report that cannot survive being signed

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-09-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

PREPARE files a report and declares it signable without ever proving that signing it leaves it valid. Nothing in the close exercises the SEAL, so the one act the whole page exists for is the only path never taken before the operator is asked to take it.

RUN-01M2SPNS signed a correct, gate-clear, VALID report and `check` reported it INVALIDATED one second later. The seal writes `ended_at`, the DORA window was bounded by it, so the act of signing widened the window and moved the figures it had just frozen (BG0718). No run could ever have held a valid signature over its own report. Nine units of delivery, two review rounds and 33 passing criteria did not see it, because every fixture wrote a signature block WITHOUT ending the run - the one state the real seal always produces.

The rule that would have caught it already exists in this project's doctrine: exercise every claim through the shipped entry point before asking for review. The earlier form of this very defect was found exactly that way, by running `sign` then `check` end to end on a throwaway tree, and it is recorded in the run's own scar file. It was not repeated for the final seal because nothing made it repeat. A rule stated and not gated holds until the first session in a hurry, which is LL0027, and this is the second time that lesson has been paid for by the same page.

## Impact

Every operator of every consuming project, on the single act the tool asks them to perform. A signature is the one step that re-running something cannot take back, and it is currently the only step whose outcome is unrehearsed.

The failure mode is silent and total: the page reads VALID when signed and INVALIDATED immediately after, so the artefact the whole report-of-record mechanism exists to produce - a page a reader can trust BECAUSE it re-derives - is worthless, and the operator finds out after committing their name to it. The cost of the guard is one throwaway-tree rehearsal per close, paid by the machine. The cost of its absence was paid by an operator who asked, correctly, whether the sign-off had been too early.

## Acceptance Criteria

- [ ] PREPARE rehearses the whole seal before it files: the run is copied to a scratch tree, the real `sprint sign` is run there against the real report, and `sprint_report check` is run on the result. The rehearsal drives the shipped commands, not their library functions - a library call cannot see the wiring, which is what let `stamp_tokens` ship with a test as its only caller and every run report a cost of zero.
- [ ] A page that does not re-derive after the rehearsal REFUSES the close, naming each figure that moved and the section it belongs to, so the operator is told what the seal would break rather than that something is wrong. The refusal leaves the run open and writes no report, because a page that cannot survive its signature is not a page.
- [ ] The rehearsal is reported as a PASSED hold by its own name on the clean path, beside the three holds PREPARE already names, so a close that skipped it is visible rather than inferred from silence.
- [ ] The scratch tree is discarded whether the rehearsal passes or fails, and the real run state, the real report and the real artefacts are byte-identical afterwards to what they were before - a rehearsal that mutates the thing it rehearses is a seal, not a rehearsal.
- [ ] The guard is proved against the defect that motivated it: a tree carrying the pre-BG0718 window behaviour is refused by the rehearsal, and the repaired tree passes. A guard demonstrated only on a tree that was already correct has not been shown to refuse anything.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Raised |
