# BG1568: The triage session cap is keyed on a run that is already closed and signed

> **Status:** Open
> **Supersedes:** BG1067
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1568.md
> **Evidence:** audit AUDIT-2026-11-17, filing step; refusal printed on the 30th filing of the batch
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:30:38Z

## Summary

`file_finding.py` caps a session at 50 filings and keys the counter on the current run. With no run open, the key was RUN-01M7HA6R, a run closed and signed the day before, so findings filed after the release and the first 29 of an audit all counted against a finished run. The filer then refused the remaining 39 audit findings mid-batch, after 29 ids had been minted. The refusal names `SDLC_TRIAGE_SESSION` as the exit, which worked, but a signed run should not be the session a new day's filings are counted in, and a batch should learn of the cap before its first id.

## Steps to Reproduce

1. Close and sign a run, and open no new one.
2. File findings with `file_finding.py` until 50 have been filed since that run opened.
3. The next filing is refused with triage session cap reached, keyed on the signed run.
4. Set `SDLC_TRIAGE_SESSION` to a new name and the same filing succeeds.

## Proposed Fix

When the latest run is closed, key the counter on a session that is not that run, for example the calendar day, and say so in the refusal. Pin it with a test that files past the cap after a signed run.

## Acceptance Criteria

- [ ] **AC1** Given a workspace whose latest run is closed and signed and no run is open, with the session counter at the cap under that run's id, when `file_finding.py file` files a finding with `SDLC_TRIAGE_SESSION` unset, then the finding is filed and the counter is keyed on a session that is not the signed run. Fails on: a new day's filing refused against a finished run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::SessionCapAfterASignedRunTests::test_a_filing_after_a_signed_run_is_not_counted_against_it
- [ ] **AC2** Given a closed run in the run state, when the session key is read, then it is the calendar-day key; given an open run, it is still that run's id; given `SDLC_TRIAGE_SESSION` set, it is still the stated name. Fails on: a closed run's id returned as the key, or the open-run and stated-name sources changing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_a_closed_run_keys_on_the_day_and_an_open_run_on_its_id
- [ ] **AC3** Given the cap reached under the calendar-day key, when a further filing is refused, then the refusal names the key in use and says it is the day because no run is open, and no id is minted. Fails on: a refusal telling the operator to close a run that is already closed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionCapTests::test_the_refusal_names_the_day_key_when_no_run_is_open

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
