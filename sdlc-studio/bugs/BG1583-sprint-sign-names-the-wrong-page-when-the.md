# BG1583: sprint sign names the wrong page when the later run has also closed, and three of US1290's guards have no test

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py, changelog.d/BG1583.md
> **Evidence:** sdlc-studio/reviews/verdicts/US1290/1d42d95f5aae-72f7cc40.txt and b9e0f15856ad-b543e9a9.txt
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T03:20:36Z

## Summary

The QA seat's two rounds on US1290 (run sixteen, APPROVE in round 2) carried two non-blocking findings: when a run waits and a later run has closed too, sign's refusal names the later run's page instead of the one asked for; and three guards US1290 added are exercised by no test.

Reproduced at cecc9dfe7 (2026-11-24), in throwaway copies:

- The wrong page. `_committed_run_to_sign` returns this checkout's own state whenever it holds a run with a report, before it looks for the tracked record the named report belongs to. With run A closed and awaiting RPT0001 in its tracked record, and a later run B in the same checkout whose state records RPT0002, `sprint sign --report RPT0001` exits 2 with `sign REFUSED: RPT0001 is not this run's report - <B> records RPT0002. Sign the page the close filed.`, sending the signer to B's page.
- Guard 1. In `run_state.open_run`'s archive branch, `_disjoint(state, batch)` replaced with `batch is not None` survives test_run_open_across_checkouts.py, test_lean_awaiting_signature_status.py, test_evidence_annex_run_record.py, test_lean_tracked_run_record.py, test_lean_sign_seals_once.py, test_lean_report_integrity.py and test_two_backlogs.py. With it, an overlapping re-plan over a closed run awaiting its signature archives that run and mints a new one (probed: the re-plan of US0101 over RUN-LEAN0001 left a fresh run id in the live state).
- Guard 2. Dropping `run_state.put_back(root, beside)` from `cmd_sign`'s refused take-up branch (`except run_state.RunStateError`) survives the same sign modules and test_lean_sign.py. With it, a refused adopt deletes the open run's live state.
- Guard 3. `status.awaiting_signature_lines` returning `[]` for an unreadable tracked record survives test_lean_awaiting_signature_status.py, test_status.py and test_run_open_across_checkouts.py.

## Steps to Reproduce

1. In one checkout, close run A (it files its tracked record awaiting RPT0001) and commit.
2. Plan a later run B there over a disjoint batch, and close it too, so the live state awaits RPT0002.
3. Run `sprint.py sign --report RPT0001 --principal <operator>`: it is refused naming B's report as the page to sign.
4. For each guard above, apply the mutant in a throwaway copy and run the named modules: they stay green.

## Proposed Fix

When this checkout's own closed run records a different report from the one named, and a tracked record awaits the named one, take that record up by the US1290 path (set the held run aside, seal, put it back byte for byte) instead of returning the held state. Pin each guard with a test beside a positive control. Guard 1 and guard 3 need no code change.

## Acceptance Criteria

- [ ] **AC1** Given run A closed and awaiting RPT0001 in its tracked record, and a later run B closed in the same checkout so its live state records RPT0002, when `sprint sign --report RPT0001` runs, then A's tracked record is sealed over RPT0001 and B's live state is byte for byte as it was, still awaiting RPT0002. Fails on: rc 2 with `RPT0001 is not this run's report - <B> records RPT0002. Sign the page the close filed.`, which sends the signer to B's page.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_sign_seals_the_named_waiting_run_while_a_later_run_awaits_too
- [ ] **AC2** Given a closed run awaiting its signature in this checkout, when `sprint plan --write` names a batch overlapping its batch, then the live state still holds the waiting run's id and nothing is archived; a disjoint batch (the control) archives it and opens a new run id. Fails on: the mutant `batch is not None` in place of `_disjoint(state, batch)` in `open_run`'s archive branch surviving every test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_an_overlapping_plan_never_archives_a_run_awaiting_its_signature
- [ ] **AC3** Given a later run open in this checkout, a waiting tracked record, and `run_state.adopt_tracked` raising `RunStateError` (stubbed, as a lock or write failure raises it), when `sprint sign` names its report, then it exits 2 and the later run's live state is byte for byte as it was. Fails on: dropping `run_state.put_back(root, beside)` from the refused take-up branch surviving every test, which leaves the open run's state deleted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_open_across_checkouts.py::RunOpenAcrossCheckoutsTests::test_a_refused_take_up_puts_the_open_run_back
- [ ] **AC4** Given a tracked run record that cannot be parsed, when `status.awaiting_signature_lines` reads the project, then it returns one line starting `Awaiting signature: UNREADABLE` naming the record, and a readable record (the control) returns its sign command. Fails on: a mutant returning `[]` for the unreadable record surviving every test, so status reads a possible waiting run as none.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_awaiting_signature_status.py::AwaitingSignatureStatusTests::test_an_unreadable_record_is_named_not_read_as_none

## Impact

A misleading refusal, and guards that could be removed with the suite still green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced the wrong-page refusal and all three surviving mutants at cecc9dfe7; Steps and Proposed Fix made concrete; four executable criteria; Affects drops test_sprint.py and adds test_lean_awaiting_signature_status.py |
