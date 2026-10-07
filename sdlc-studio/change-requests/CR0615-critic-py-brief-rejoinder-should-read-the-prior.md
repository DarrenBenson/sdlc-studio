# CR-0615: critic.py brief --rejoinder should read the prior verdict from the ledger instead of a hand-written file

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T14:02:00Z

## Summary

Extends [[CR0329]] (Complete), which introduced the file-based `--rejoinder`; this asks that it read the ledger rather than a hand-written copy.

A REJECT answered in round 2 needs `critic.py brief --unit X --seat S --rejoinder FILE`, where FILE is the round-1 VERDICT/ISSUES/BLOCKING block. The reviewer already recorded that verdict with `critic.py record --from-verdict` into reviews/critic-verdicts.md, so the author had to re-type (or copy from a transcript) a verdict the tool already holds - twice in one sprint (homelab US0185, US0186). Hand transcription is where a finding gets paraphrased or dropped between rounds.

## Impact

Orchestrators of multi-round reviews; the rejoinder brief can silently omit a finding that the ledger has.

## Acceptance Criteria

- [ ] `critic.py brief --rejoinder ledger` (or `--rejoinder` with no file) builds the round-2 brief from the unit's latest recorded REJECT for that reviewer, verbatim
- [ ] With no recorded REJECT to answer, the brief refuses and says so
- [ ] A file argument still works, for a verdict not yet recorded

## Proposed Fix

Let --rejoinder take `ledger` (or default to it when omitted with --round 2): load the unit's latest REJECT verdict for that seat from the verdict ledger, and refuse if none exists.

## Triage

- Seen again in this repository on 2026-10-07: BG0962's round 2 needed the round-1 verdict as a file. Hand-saving it, the author first dropped the reviewer's VERIFIED block and reflowed its BLOCKING bullets, and had to restore it verbatim before recording. That is the paraphrase-or-drop risk this CR names. BG0950 (a contract-shaped verdict refused at record) is the other half of the same round trip.
- Criteria added for refinement.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Raised |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: criteria added; this repository's BG0962 round 2 added as evidence |
