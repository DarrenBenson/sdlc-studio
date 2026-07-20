# BG0234: a story AC asserting a repo-wide invariant retroactively un-Dones itself as the repo grows

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/stories/US0112-hygiene-close-fixed-bugs-archive-over-threshold-indexes.md,sdlc-studio/stories/US0115-advisory-lanes-earn-their-signal-mutation-wired-into.md,.claude/skills/sdlc-studio/scripts/conformance.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

US0112 AC2 asserts that reconcile detect emits no archival advisory, and US0115 AC1 asserts that disclosure.py emits zero warnings. Both were true when those stories shipped and are false now: five indexes have grown past `indexes.archive_after`, and there are 19 disclosure advisories. Neither regression was caused by the change that exposed them - a full `verify_ac` sweep at the RUN-01KY03GS close - and neither story is at fault for its own failure. The ACs are scoped to the WHOLE REPOSITORY rather than to the behaviour the story delivered, so any later growth anywhere retroactively un-Dones a shipped story and blocks an unrelated commit through the conformance gate. That is what happened here: a close was refused over debt accrued by other work months later. Related to BG0231, which is the same surface from the other side - there the AC stayed falsely green, here it goes falsely red.

## Steps to Reproduce

Run `verify_ac` over all stories. US0112 AC2 and US0115 AC1 fail. Confirm neither is a defect in the story: reconcile detect reports only archival advisories (167 terminal story rows, 148 cr, 166 bug, all over the threshold), and disclosure.py reports 19 advisory findings, none traceable to those stories. Then run the pre-commit gate on any unrelated change and observe conformance refuse it.

## Proposed Fix

Two parts. First, decide the policy: an AC that asserts a repo-wide invariant is a GATE, not an acceptance criterion, and belongs in the gate configuration where it can be tuned as the repo grows - not frozen into a story whose Done then depends on unrelated future work. Rescope both ACs to the behaviour their story delivered. Second, separate the two failures the conformance gate currently conflates: a unit that never met its bar, and a unit that met it and was later invalidated by drift elsewhere. Only the first should block a commit; the second is a report.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
