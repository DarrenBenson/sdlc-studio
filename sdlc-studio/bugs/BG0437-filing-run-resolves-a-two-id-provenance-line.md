# BG0437: filing_run resolves a two-id provenance line by document order, so the refusal its criterion promises is nearly unreachable

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/backfill_audit_runs.py, .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py
> **Evidence:** Executed by an independent reviewer, who confirmed the current corpus is unaffected.
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch); agent; skill v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`filing_run` returns on the FIRST `run <id>` match, so the Ambiguous refusal is reachable only when no `run <id>` appears at all. The criterion states that a line the prose does not disambiguate is refused rather than resolved by order; that is true for one shape only. `filed by run wf_aaa and run wf_bbb` resolves to `wf_aaa`; `carry-over from wf_aaa, carry-over run wf_bbb` resolves to `wf_bbb` even though the prose calls it a carry-over, because the carried-over pattern matches only the `<id> carry-over` word order; and a third id is silently dropped. Latent on today's corpus - all 108 findings match the two known shapes - but `check` is documented as the standing sweep for future findings and the failure mode is a fabricated provenance. Also `_RUN_ID` is lowercase-only, so `run wf_ABC123` yields None, the finding is dropped from the scan, and `check` reports clean.

## Steps to Reproduce

1. `filing_run('filed by run wf_aaa and run wf_bbb')` -> '`wf_aaa`'.
2. `filing_run('carry-over from wf_aaa, carry-over run wf_bbb')` -> '`wf_bbb`'.
3. `filing_run('run wf_ABC123')` -> None, and `check` reports clean.

## Proposed Fix

Refuse when more than one id survives disambiguation rather than returning the first; match the carry-over marker in both word orders; case-fold the id pattern or refuse a non-matching id loudly.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `filing_run` returns on the FIRST `run <id>` match, so the Ambiguous refusal is reachable only when no `run <id>` appears at all.
- [ ] The proposed fix lands, pinned by a test: Refuse when more than one id survives disambiguation rather than returning the first; match the carry-over marker in both word orders; case-fold the id pattern...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
