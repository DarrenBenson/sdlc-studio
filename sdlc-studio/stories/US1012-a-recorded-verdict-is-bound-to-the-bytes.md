# US1012: A recorded verdict is bound to the bytes of the file its brief issued

> **Status:** Draft
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1012.md
> **Epic:** EP0280
> **Points:** 5
> **Depends on:** US1011, BG1003
> **Persona:** Maya Okafor

## User Story

**As** the operator who signs the run on the strength of its reviews
**I want** each verdict row to carry the hash of the file its brief issued, that file kept exactly as written and committed with the row, and a transcribed verdict marked as one
**So that** a softened finding or a dropped BLOCKING line between the reviewer and the ledger can be seen rather than taken on trust

## Acceptance Criteria

- **AC1:** Given a block at a path the brief issued, opening with its UNIT and BRIEF lines and carrying prose beyond the VERDICT, ISSUES and BLOCKING fields, when `critic.py record --from-verdict <path>` runs, then the new row's `Source` cell is `sha256:<first 16 hex digits of the file's exact bytes> <file basename>`, and the file is byte-identical afterwards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_an_issued_file_is_hashed_as_written
- **AC2:** Given the same verdict given by `--verdict` and `--issues`, by `--from-verdict -`, from a file outside `sdlc-studio/reviews/verdicts/`, or from `sdlc-studio/reviews/verdicts/US0001/mine.txt`, which no brief issued, when `record` writes it, then the row's `Source` cell is `-` and `record` prints that the verdict was transcribed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_a_verdict_from_no_issued_file_is_marked_transcribed
- **AC3:** Given an eight-column ledger and the row identities a run record froze from it, when `critic.py record` writes the first verdict after the change, then a ninth `Source` column is added, every earlier row is padded with `-` and keeps its cells, the `Verdict` column still parses as APPROVE or REJECT, and every frozen identity is still found among the ledger's rows.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_the_source_column_moves_no_frozen_row_identity
- **AC4:** Given one row recorded from an issued file and one transcribed row, when `critic.py show` runs, then the first row's line reads 'from the brief's verdict file (writer unread)' and names the file, the second reads 'transcribed', and `--format json` carries the same as a field.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py::VerdictFileBindingTests::test_show_says_where_each_verdict_came_from_and_claims_no_writer

## Notes

- Release: 6.2 (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: hashing the parsed issues text rather than the file, or normalising line endings or trailing whitespace before hashing
- AC2 must fail on: a directory test (any file under `verdicts/` reads as issued), or hashing whichever file `--from-verdict` names
- AC3 must fail on: the new column named `Verdict` (the migration's `| {name} |` test at critic.py:502 then never adds it, and the parsed key overwrites APPROVE and REJECT), or the ninth cell added to `row_identity`'s digest
- AC4 must fail on: the label 'reviewer-written', which claims a writer nothing has checked (the authoring session can write an issued path itself), or `show` omitting the source
- Checked at HEAD: `cmd_record` (critic.py:3265) stores only the parsed verdict and issues, with newlines and pipes folded (`_clean`), so the ledger cannot give back the reviewer's block.
- The ninth column is `Source`, not `Verdict`: `_TABLE` already has a `Verdict` column. Its cell grammar is fixed here, so stories 4 to 6 and BG1003 parse one format: space-separated tokens, `sha256:<16 hex> <basename>` first; then `session:<id> agent:<id>` (story 5); `self-review:<repo path>` (story 6); `authorised:<Dnnnn>` (BG1003). `-` means transcribed. `show` and story 4 find the file from the cell (`verdicts/<UNIT>/<basename>`), never by scanning.
- One migration widens the ledger once in 6.2. Whichever of BG1003 and this story lands first adds `Source` by generalising `_ensure_eighth_column`'s pad-not-rewrite loop. `row_identity` (critic.py:599-610) stays over the original eight cells, because `REVIEW_ROWS` freezes them into signed run records (sprint_report.py:3328-3332). This repository's ledger has 1,552 eight-cell rows.
- Issued means the path is one `note_brief` recorded. `.local/briefs.jsonl` is per machine, so a file briefed in another clone reads `transcribed`: it fails towards the weaker label. The label claims no writer until story 5 reads one.
- The verdict file is committed with its ledger row. Otherwise a fresh clone's `show` reports every file missing (story 3).
- The changelog names the mixed-version effect: a 6.1 reader treats every nine-cell row as malformed and skips it (critic.py:594), so a teammate on an older install sees no verdicts. That fails closed, as the Tier column did. Correct the stale comment at critic.py:826 ('the row parser reads 6 or 5 cells').
- `provisional_verdict` (the `transition set --verdict` path) and `record_verdict` (`artifact.py close --verdict`) write through `_write_verdict` too, so they write the ninth cell, as `-`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
