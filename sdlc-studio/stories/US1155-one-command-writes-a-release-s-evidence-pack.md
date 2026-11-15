# US1155: One command writes a release's evidence pack from committed records

> **Status:** Ready
> **Delivers:** CR0692
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/evidence_pack.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_confinement.py, .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py, changelog.d/US1155.md, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/reference-scripts-domain.md
> **Epic:** EP0308
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** one command writes a release's evidence pack from committed records
**So that** every release passes the change board on the evidence the run produced, with no separate write-up

## Acceptance Criteria

- **AC1:** Given committed signed reports, when `release_cut.py evidence-pack --version 6.4.0 --reports RPT0001,RPT0002` runs, then it writes one markdown pack under sdlc-studio/reports/ listing each delivered unit of those reports, and exits 0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::BuildPackTests::test_pack_lists_delivered_units_of_signed_reports
- **AC2:** Given an unsigned or unknown report, when the command runs, then it exits non-zero naming the report and writes no pack.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::BuildPackTests::test_unsigned_or_unknown_report_is_refused
- **AC3:** Given an uncommitted edit to a unit's file or the verdict ledger, when the pack is built, then the pack reads the committed copy and is byte-identical to one built before the edit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::CommittedOnlyTests::test_working_tree_edits_do_not_change_the_pack
- **AC4:** Given a delivered unit, when the pack is built, then its entry states what changed (title and points), which criteria passed (its ticked criteria and their Verify lines) and who reviewed it independently (the latest verdict per seat whose reviewer differs from the author).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_evidence_pack_build.py::UnitEntryTests::test_entry_has_change_criteria_and_independent_reviewer

## Notes

- Serves Abena Osei's End goal 1; delivers part of CR0692 (D0476).
- AC1 must fail on: A pack listing planned or dropped units; units from an unnamed report; no file written.
- AC2 must fail on: An unsigned report packed anyway; a partial pack left on disk; the refusal not naming the report.
- AC3 must fail on: Reading from the working tree; a dirty ledger row appearing in the pack; the build needing the tool's local state (sdlc-studio/.local).
- AC4 must fail on: A reviewer equal to the author counted as independent; every criterion listed as passed whatever its tick; a unit with no verdict shown as reviewed.
- Records to read: signed reports sdlc-studio/reports/RPT*.json (committed; schema 2; fields `signature{principal,signed_at,fingerprint}`, sections[] with key 'delivered' whose rows hold `unit_id`, `unit_points`, `unit_outcome`, `unit_rounds` as {'value': ...} figures). RPT0030.json at HEAD is a worked example; `scripts/sprint_report.py` `read_report` is the reader and sprint.py:10521 `_write_the_signature` writes the signature.
- Verdicts: sdlc-studio/reviews/critic-verdicts.md (committed) via `critic.read_verdicts` (scripts/critic.py:704) and `seat_verdicts` :869; columns unit, verdict, reviewer, author, issues. To read committed copies use `git show <rev>:<path>` (rev default HEAD) rather than the working tree; `read_verdicts` takes a path so you may need a text variant.
- Verify runs are NOT a committed record: `verify_ac` writes sdlc-studio/.local/verify-report.json (gitignored; `verify_ac.py:5273`). The committed evidence of passed criteria is the story's ticked criteria plus its Verify lines and the Done status. State that in the pack; do not read .local.
- `release_cut.py` has changelog-cut, record-green, tag-check and `build_parser` :332; add an evidence-pack verb that delegates to the new `evidence_pack.py` so the logic stays out of `release_cut`. A release is named by --reports for part 1; mapping a git tag range to reports can follow.
- Grouping by risk class and the annex are part 2 (CR0692 AC3, AC4); do not add them. Pack text is consuming-facing: British English, no em dashes, no RPT or D ids in the prose headings.
- New scripts must be listed in reference-scripts.md; `test_confinement.py` and `test_release_cut.py` enumerate `release_cut` verbs or writes, so check them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
| 2026-11-15 | Claude Opus 5.5 (run twelve) | Affects gains the generated command surface, which the new `release_cut.py evidence-pack` verb changes (the builder found five tests that require zero drift) |
| 2026-11-15 | Claude Opus 5.5 (run twelve) | Affects gains reference-scripts-domain.md: doc coverage needs a level-three catalogue heading for the new script, beside release_cut.py's |
