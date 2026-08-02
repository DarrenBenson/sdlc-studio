# BG0483: claim-drift reads append-only ledgers as prose, so verdict rows are matched against the code they name

> **Status:** Fixed
> **Verification depth:** functional (the defect's own shape as the fixture, with a positive control beside it)
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_spec_claims.py, tools/tests/test_precommit_claim_drift.py, tools/tests/test_check_spec_claims.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

`_PROSE_SUFFIXES` admits any .md file, so append-only LEDGERS are read as prose making claims about the change. sdlc-studio/reviews/critic-verdicts.md is the worst case: every row carries a reviewer id containing the word `critic`, which now shares a subject token with any diff touching critic.py, and each row carries integers (ids, dates) that can collide with a replaced literal.

Observed on the commit that shipped the BG0479 repair: three CLAIM-DRIFT lines against critic-verdicts.md rows, each quoting a US0560/US0561/US0562 verdict beside `if len(cells) == 7:`. The rows are records of judgements somebody made; they assert nothing about how the code behaves, so they cannot be in drift with it by construction.

The BG0479 shared-subject rule reduced the lane's yield sharply but does not help here, because the collision is on a real token rather than a bare digit.

## Steps to Reproduce

1. Touch .claude/skills/sdlc-studio/scripts/critic.py in a diff that replaces an integer literal.
2. Commit.
3. The claim-drift lane reports against sdlc-studio/reviews/critic-verdicts.md rows.

## Proposed Fix

Exclude append-only ledgers from the prose corpus - the verdict logs, evidence logs and signoff records under sdlc-studio/reviews/, and any file whose body is a table of records rather than narrative. A ledger row is a record of an event, not a claim about behaviour, so it is not a thing a diff can contradict. Then re-run the replay and record the new yield, because this changes the measured number the blocking decision will read.

## Acceptance Criteria

### AC1: an append-only ledger is not read as prose

- **Given** a diff touching `critic.py` alongside a row appended to the verdict log
- **When** the drift lane runs
- **Then** nothing is reported from the ledger, because a verdict row records a judgement somebody made and asserts nothing a diff could contradict
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::LedgerExclusionTests::test_a_verdict_ledger_is_not_read_as_prose
- **Verified:** yes (2026-08-02)

### AC2: ordinary paperwork in the same diff still fires

- **Given** a changelog fragment in that same diff stating a replaced value
- **When** the lane runs
- **Then** it is still reported, so excluding ledgers does not become excluding paperwork - which is the whole point of the lane
- **Verify:** pytest tools/tests/test_precommit_claim_drift.py::LedgerExclusionTests::test_ordinary_prose_in_the_same_diff_still_fires
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Filed |
