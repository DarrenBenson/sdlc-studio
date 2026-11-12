# US1012: A recorded verdict is bound to the bytes of the file its brief issued

> **Status:** Ready
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_verdict_file_binding.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_supersede_by_brief.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1012.md
> **Epic:** EP0280
> **Points:** 5
> **Depends on:** US1011
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

- Release: after 6.3.0, in run ten (D0461); 6.3.0 shipped without it (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: hashing the parsed issues text rather than the file, or normalising line endings or trailing whitespace before hashing
- AC2 must fail on: a directory test (any file under `verdicts/` reads as issued), or hashing whichever file `--from-verdict` names
- AC3 must fail on: the new column named `Verdict` (the migration's `| {name} |` test at critic.py:546 then never adds it, and the parsed key overwrites APPROVE and REJECT), or the ninth cell added to `row_identity`'s digest
- AC4 must fail on: the label 'reviewer-written', which claims a writer nothing has checked (the authoring session can write an issued path itself), or `show` omitting the source
- Checked at HEAD (2026-11-12): `cmd_record` (critic.py:4315) stores only the parsed verdict and issues, with newlines and pipes folded (`_clean`, critic.py:314), so the ledger cannot give back the reviewer's block. No `Source` column or `source` key exists, so no criterion is met.
- The ninth column is `Source`, not `Verdict`: `_TABLE` already has a `Verdict` column. Its cell grammar is fixed here, so stories 4 to 6 parse one format: space-separated tokens, `sha256:<16 hex> <basename>` first; then `session:<id> agent:<id>` (story 5); `self-review:<repo path>` (story 6). `-` means transcribed. Round rulings stay where BG1003 records them, below the table (`_append_ruling`). `show` and story 4 find the file from the cell (`verdicts/<UNIT>/<basename>`), never by scanning.
- One migration widens the ledger once. This story adds `Source` by generalising `_ensure_eighth_column`'s pad-not-rewrite loop. `row_identity` (critic.py:666-677) stays over the original eight cells, because `REVIEW_ROWS` (sprint_report.py:3384-3388) freezes them into signed run records through `freeze_review_rows` (sprint_report.py:3454-3466), and `_row_keys` (critic.py:970) keys the round rulings by them. This repository's ledger has 1,814 rows, all eight cells. The historical plan-review ledger takes nothing new (critic.py:79-82).
- Issued means the path is one `note_brief` recorded. `.local/briefs.jsonl` is per machine, so a file briefed in another clone reads `transcribed`: it fails towards the weaker label. The label claims no writer until story 5 reads one.
- The verdict file is committed with its ledger row. Otherwise a fresh clone's `show` reports every file missing (story 3).
- The changelog names the mixed-version effect: a reader on 6.3.0 or earlier treats every nine-cell row as malformed and skips it (critic.py:650-655), so a teammate on an older install sees no verdicts. That fails closed, as the Tier column did. Correct the stale comment at critic.py:893 ('the row parser reads 6 or 5 cells') and the warning's 'expected 6 or 5' at critic.py:654.
- `provisional_verdict` (the `transition set --verdict` path) and `record_verdict` (`artifact.py close --verdict`) write through `_write_verdict` (critic.py:365) too, so they write the ninth cell, as `-`.
- Keep `record`'s `recorded <ID> <VERDICT> [delivery] round N` line as its prefix and print the transcribed notice on its own line: `sprint lane accept` parses that line (lib/lanes.py:421).
- Existing tests this change reaches: test_critic.py holds the Tier migration (lines 448-457), the pre-Brief widening test (line 2791) and the `show` listings (lines 1770-1788 and 3371-3385, one line per row); test_supersede_by_brief.py seeds ledgers from `critic._TABLE` with eight-cell rows (lines 41-50). test_lean_signed_report_stable.py:695-720 pins `row_identity` over the eight cells and must pass unchanged.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references moved to HEAD, ledger count 1,814, release line set to run ten, Affects gains test_critic.py and test_supersede_by_brief.py, lane accept's parsed line named |
