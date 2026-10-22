# BG1029: critic record splits a verdict's findings on every ';', so reviewer prose with a semicolon is refused as an untagged finding

> **Status:** Superseded
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-12T11:56:22Z

## Summary

Seen on a consuming project's RUN-01M4EMNN (2026-10-12): four of four independent verdicts were refused by `critic.py record --from-verdict` and had to be edited by the author before they would record. The return contract asks for 'semicolon-separated findings' but says nothing against a ';' INSIDE a finding, and reviewers write evidence like '`study_work_mode.json`:69; also in the parent commit' - the fragment after the ';' has no tag and the whole record is refused. BLOCKING items are also parsed as tagged findings, but the contract describes BLOCKING only as 'the subset', so an untagged BLOCKING list is refused too - that half is BG0950 (Open); this bug is the ';'-inside-a-finding half, which BG0950 does not cover. The author editing the reviewer's words to make them record is exactly the hand the independence rule keeps off the verdict.

## Steps to Reproduce

Write a verdict block whose ISSUES has '[new] a (x.py:1); also b; [pre-existing] c' and BLOCKING 'a; b'. critic.py record --from-verdict FILE -> 'record refused: these findings carry no origin'.

## Proposed Fix

Split only on ';' followed by optional space and a tag ('; [regression]', '; [new]', '; [pre-existing]'), so a ';' inside a finding stays prose; and state in `_RETURN_CONTRACT` that each BLOCKING item repeats its tag (or derive BLOCKING's tags from the matching ISSUES item).

## Acceptance Criteria

- [ ] **AC1** A finding whose text contains ';' records as one finding
  - **Verify:** manual record a verdict with a ';' inside a tagged finding and an untagged BLOCKING list per the contract - it records unedited
- [ ] **AC2** The return contract states how BLOCKING items are tagged, and a block following it records unedited

## Triage

- Superseded by BG0950: its AC3 already required a semicolon inside one finding to be handled, and on 2026-10-12 the goal review of the first 6.2 run made it a single requirement (the finding survives, with the reviewer's words unchanged). This bug's evidence (four of four verdicts refused and hand-edited in a consuming project) is folded into BG0950, which is in that run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Filed |
| 2026-10-12 | Claude (a consuming project's RUN-01M4EMNN) | Scoped against BG0950: the BLOCKING-tag half is BG0950's; this bug is the ';' inside a finding. |
| 2026-10-12 | Claude Opus 5.5 (triage) | Superseded by BG0950, which now carries this evidence and a non-disjunctive criterion |
