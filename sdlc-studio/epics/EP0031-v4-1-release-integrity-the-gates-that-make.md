# EP0031: v4.1 release integrity: the gates that make the tag trustworthy

> **Status:** Done
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio new

## Summary

{{what this epic groups}}

## Story Breakdown

Delivery order matters: CR0233, BG0110 and CR0229 all extend the same check registry
(`gate.py` `DEFAULT_CHECKS`), and `test_gate.py` asserts the exact check-name set, so their
registry edits are sequenced rather than parallel. The three bugs are independent and can run
alongside.

- [x] [BG0111](../bugs/BG0111-lessons-written-by-lessons-py-are-lost-on.md) - lessons.py writes authored content into the untracked install (data loss); fail loud, make the project tier the default (High; independent - start first)
- [x] [BG0108](../bugs/BG0108-artifact-py-schema-v3-skeletons-fail-their-own.md) - the deterministic creators emit skeletons the deterministic validator rejects; enforce with a create-then-validate round trip across every creator, type and era (independent)
- [x] [BG0109](../bugs/BG0109-file-finding-py-hardcodes-audit-as-the-revision.md) - file_finding.py hardcodes 'audit' as the revision-history author, ignoring --author (Low; independent)
- [x] [CR0233](../change-requests/CR0233-gate-release-one-command-that-cannot-be-misread.md) - gate --release: the standard gate plus the executable-AC pass, one exit code (High; FIRST of the gate three - establishes the lane and the aggregation point)
- [x] [BG0110](../bugs/BG0110-review-lets-a-required-leg-tsd-be-self.md) - a required review leg can be self-downgraded to optional in prose; build the leg-presence gate and the waiver primitive (depends CR0233; four document legs only, CODE excluded - D0022)
- [x] [CR0229](../change-requests/CR0229-engagement-floor-mandatory-planning-when-the-change-is.md) - engagement floor, mechanical half: refuse a Done multi-file unit with no plan/AC artefact (High; depends BG0110 for the waiver/opt-out shape; signal + cutoff settled in D0021)
- [x] [CR0236](../change-requests/CR0236-the-lessons-close-loop-is-doctrine-not-mechanism.md) - the lessons close-loop is doctrine, not mechanism: gate the summary at close and surface it at plan (operator directive; same defect class as BG0111 - a documented intention with no implementation)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Darren | Created via `new` (deterministic) |
