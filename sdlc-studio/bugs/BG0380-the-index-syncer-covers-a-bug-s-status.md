# BG0380: The index syncer covers a bug's status but not its severity, and not an RFC's status at all, so a corrected artefact and its index row disagree with drift_items=0

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (discovery-backlog triage, RUN-01KYKVZM follow-on); agent; skill v5.0.0

## Summary

The index is documented as derived output that must never be hand-authored, and reconcile is named as the thing that syncs it. It does not sync every cell. Measured today: closing 18 RFCs to Complete left every one of their index rows reading Accepted, and correcting BG0370 Medium to High and BG0368 Medium to Low left both index rows reading Medium. In all cases `reconcile detect` reported `drift_items`=0, including under `--scope rfcs`. The separate `reconcile fields` verb, which is not part of detect or apply, syncs TITLES only - it reported 3 rfc, 1 bug, 2 cr and 4 story title drifts and no status or severity drift at all. status.py reads the index, so the discovery backlog count ROSE from 41 to 59 after eighteen items were closed, and every backlog figure reported from the index while this is true is wrong.

## Steps to Reproduce

Close an RFC to Complete, or change a bug's Severity, then run `reconcile.py detect` and `reconcile.py apply` (with and without --scope). Both report `drift_items`=0 and changed 0 rows, while the index row still shows the old value. `reconcile.py fields --type rfc` likewise reports only title drift. Verified today against RFC0001/RFC0009/RFC0038 (file Complete, index Accepted) and BG0370/BG0368 (file High/Low, index Medium).

## Proposed Fix

Derive every index cell the row carries from the artefact, not a subset of them. The row's columns are known per type, so the syncer should iterate the row schema rather than a hand-picked list of fields - the enumerated-list defect this repo keeps re-filing. Fold the fields pass into detect and apply so one command answers 'is the index derived', and make a stale cell a drift item so `drift_items` can never read 0 while a row disagrees with its artefact.

## Acceptance Criteria

No acceptance criterion could be derived from this finding's evidence: none of its prose fields carries fewer than 5 words of substance, so nothing here states what fixed would look like. Whoever picks this up agrees the contract with the author before starting - this is a stated gap, not a criterion to tick.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 (discovery-backlog triage, RUN-01KYKVZM follow-on) | Filed |
