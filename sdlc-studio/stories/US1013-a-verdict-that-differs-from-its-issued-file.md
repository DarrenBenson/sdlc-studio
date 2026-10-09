# US1013: A verdict that differs from its issued file, or was recorded before, is named

> **Status:** Draft
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py, .claude/skills/sdlc-studio/reference-review.md, changelog.d/US1013.md
> **Epic:** EP0280
> **Points:** 3
> **Depends on:** US1012
> **Persona:** Maya Okafor

## User Story

**As** the operator who signs the run
**I want** `record` to warn when what it records differs from the issued file, refuse a file recorded before or headed for another unit, and `show` to name a file changed or missing since it was recorded
**So that** the hash on each row is compared by something, instead of being stored and never read

## Acceptance Criteria

- **AC1:** Given an issued, unrecorded file for US0001 and a block recorded for US0001 with `--brief <fp>` by `--from-verdict -` or by `--verdict` and `--issues`, when `record` runs, then a block that drops or changes a finding is written as transcribed with a warning naming the issued file and the first finding that differs, and a block with the same findings in the same order, reflowed only, is written with no warning.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_a_transcription_that_differs_from_the_issued_file_warns_and_a_reflow_does_not
- **AC2:** Given bare `VERDICT: APPROVE` / `ISSUES: none` / `BLOCKING: none` blocks for US0001 and US0002, each at its own issued path under its own header, when both are recorded, then both rows are written; and given a file whose hash an earlier row carries, or whose UNIT or BRIEF line names another unit or another issued file, `record` refuses with exit 2, names the earlier row or the mismatch, and writes nothing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_a_replayed_or_misheaded_file_is_refused_and_bare_approves_are_not
- **AC3:** Given one recorded issued file edited afterwards and another deleted, when `critic.py show` runs, then it names the first as changed since it was recorded and the second as missing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_drift.py::VerdictDriftTests::test_show_names_a_verdict_file_changed_or_missing_since_it_was_recorded

## Notes

- Release: 6.2 (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: comparing the verdict word only, so a dropped BLOCKING finding passes silently; or comparing raw text, so every transcription warns, because `_clean` folds newlines (critic.py:262)
- AC2 must fail on: no header check, so a copy of another unit's verdict file records as this one's; or the replay test made on the path rather than the hash
- AC3 must fail on: `show` re-hashing the file and comparing it with itself, or testing only that the path exists
- This is CR0619 AC2's second half. The comparison is made on the parsed findings, in order: a whitespace reflow is not a difference, a dropped finding is.
- Re-briefs share a fingerprint (story 1 AC2), so several issued files can match one `--brief <fp>`. The comparison is made against every issued, unrecorded file for that unit and fingerprint. It warns unless one matches, and the warning names the newest.
- The replay refusal is not in the CR. It became sound once the brief stamped each file with its UNIT and BRIEF lines (panel's preference over dropping it): 203 of the 1,552 ledger rows are bare APPROVEs, whose bodies are byte-identical across units, and the header makes each issued file's bytes unique.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
