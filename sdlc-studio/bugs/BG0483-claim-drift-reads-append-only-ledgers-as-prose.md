# BG0483: claim-drift reads append-only ledgers as prose, so verdict rows are matched against the code they name

> **Status:** Open
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

- [ ] The behaviour described is corrected: `_PROSE_SUFFIXES` admits any .md file, so append-only LEDGERS are read as prose making claims about the change.
- [ ] The proposed fix lands, pinned by a test: Exclude append-only ledgers from the prose corpus - the verdict logs, evidence logs and signoff records under sdlc-studio/reviews/, and any file whose body is...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Filed |
