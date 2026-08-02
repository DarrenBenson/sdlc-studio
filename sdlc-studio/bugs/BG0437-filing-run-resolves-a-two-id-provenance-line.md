# BG0437: filing_run resolves a two-id provenance line by document order, so the refusal its criterion promises is nearly unreachable

> **Status:** Fixed
> **Verification depth:** functional (all four shapes exercised through the shipped function - one id, both carry-over orders, and the two-run refusal - with the single-id control beside it)
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

### AC1: two filing runs are refused, never ordered

- **Given** a provenance line naming two `run <id>` mentions
- **When** the filing run is resolved
- **Then** it is refused naming both, because returning on the first match made the refusal reachable only when NO run id appeared - and a fabricated provenance is worse than an absent one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::FilingRunDisambiguationTests::test_two_filing_runs_are_refused
- **Verified:** yes (2026-08-02)

### AC2: a carry-over disambiguates in both word orders

- **Given** `<id> carry-over` and `carry-over from <id>`, each beside two `run <id>` mentions so the carry-over is what settles it
- **When** each is resolved
- **Then** both yield the filing run, because a pattern that silently matches nothing is how the disambiguation stopped happening. The second word order is DEFENSIVE, not observed: measured over this corpus's `Raised-by` lines, 12 write `<id> carry-over` and none writes `carry-over from <id>`. An earlier draft of this criterion claimed the corpus was half-and-half, which measurement refutes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::FilingRunDisambiguationTests::test_a_carry_over_disambiguates_in_both_word_orders
- **Verified:** yes (2026-08-02)

### AC3: a single id is still the answer

- **Given** a line naming exactly one run, and one naming none
- **When** each is resolved
- **Then** the id and None respectively, so the refusal cannot be satisfied by refusing everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_backfill_audit_runs.py::FilingRunDisambiguationTests::test_a_single_id_is_still_the_answer
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | Claude Opus 5 (independent adversarial review of the EP0169/EP0172/EP0175 batch) | Filed |
