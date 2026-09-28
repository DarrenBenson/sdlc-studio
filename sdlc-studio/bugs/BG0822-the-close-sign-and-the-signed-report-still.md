# BG0822: The close, sign and the signed report still speak the retired v5 sign-off vocabulary, and the close misstates the outcome sign will write

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/core/sprint-report.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, .claude/skills/sdlc-studio/help/handoff.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_close_output_vocabulary.py, changelog.d/BG0822.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** HEAD 7e53a438 grep: sprint.py 6223-6371 `apply-signoff:`, 8960, 9206, 9297; critic.py:962; sprint-report.md:81; sprint.py:5081 vs SIGNED_OUTCOMES (9212); eval 09 dry-run `from the None verdict`; soak F25/F27
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:24:04Z

## Summary

US0964 cleaned the --help text; the runtime output was left. The close prefixes its tail lines `apply-signoff:` (sprint.py ~6223-6371), naming a flag v6 retired, which is why the soak read `apply-signoff: velocity row recorded` as sign output contradicting help/sprint.md (F27). Its last line says `sign it with: ... --principal "<the reviewer of record>"` (sprint.py:8960), sign's refusals say `the reviewer of record must sit ...` (9206, 9297), critic.py:962 says `held to the sign-off's own rule`, and the report template's Sign-off table heads the operator's signature `Reviewer of record` (templates/core/sprint-report.md:81, sprint-report.html:169). The handoff step says sign `writes the stopped outcome from the partial verdict` (sprint.py:5081) while sign writes `partial` or `missed` (`SIGNED_OUTCOMES)`, and printed `from the None verdict` in eval 09; help/handoff.md lists no partial or missed outcome.

## Steps to Reproduce

Run `sprint.py close --retro RETROxxxx --goal-verdict partial --note x` on a fixture run; read the output's prefixes, its last line and the handoff step's outcome claim; draw the report and read the Sign-off table header.

## Proposed Fix

Rename the tail's prefix to `close:`, the principal hint and refusals to `the operator who signs`, the report table header to `Signed by`; have the handoff step print the outcome `SIGNED_OUTCOMES` maps the verdict to (or `stopped` when no verdict is recorded) and list partial and missed in help/handoff.md.

## Acceptance Criteria

- [ ] **AC1** Given a close run to the end on a fixture, then no stdout or stderr line carries `apply-signoff` or `reviewer of record`, and the report's Sign-off header does not read `Reviewer of record`. Fails on: HEAD
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_output_vocabulary.py::CloseOutputVocabularyTests::test_no_retired_sign_off_words_in_close_output
  - **Verified:** yes (2026-09-28)
- [ ] **AC2** Given a partial goal verdict, when the handoff step reports, then it names the partial outcome sign will write. Fails on: HEAD's `stopped outcome from the partial verdict`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close_output_vocabulary.py::CloseOutputVocabularyTests::test_the_handoff_step_names_the_signed_outcome
  - **Verified:** yes (2026-09-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
