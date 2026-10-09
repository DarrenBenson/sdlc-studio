# US1011: A review brief names the file the reviewer writes its verdict to

> **Status:** Draft
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1011.md
> **Epic:** EP0280
> **Points:** 2
> **Depends on:** BG0950
> **Persona:** Maya Okafor

## User Story

**As** the operator who dispatches an independent reviewer for each unit
**I want** every review brief to name the file the reviewer writes its own verdict block to, with the two header lines that file opens with, and the brief's record command to read that file
**So that** I record what the reviewer wrote instead of re-typing or condensing the text it returned

## Acceptance Criteria

- **AC1:** Given a fixture unit and a working directory that is not the repository root, when `critic.py brief --unit US0001 --seat qa --root <root>` runs, then after the unchanged return contract the brief names an absolute path under `<root>/sdlc-studio/reviews/verdicts/US0001/`, with the `UNIT: US0001` and `BRIEF: <file stem>` lines the file must open with, and the record command the footer prints reads that path with `--from-verdict`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_the_brief_names_an_absolute_verdict_path_and_records_from_it
- **AC2:** Given two briefs of the same unit and seat, when both are printed, then they name different verdict paths and print the same fingerprint, and `critic.py record --brief-file` on either saved brief stores that fingerprint.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_two_briefs_share_a_fingerprint_and_not_a_path
- **AC3:** Given a round-1 REJECT recorded from the file its brief named, when the rejoinder brief for round 2 is printed, then it names a new path and never the round-1 file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py::BriefVerdictPathTests::test_a_rejoinder_never_names_an_earlier_rounds_file

## Notes

- Release: 6.2 (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the path printed relative to the working directory (a reviewer in its own worktree then writes out of the recorder's reach); `_RETURN_CONTRACT` parameterised, which breaks `neutrality_violations`' exact strip (critic.py:1904); or the footer still printing `--verdict <APPROVE|REJECT> ...`
- AC2 must fail on: the path or header lines left inside the fingerprinted text, so every brief's fingerprint differs and `rebrief_notice` warns about a scope that has not changed
- AC3 must fail on: a path derived from the unit and seat alone, so the round-2 reviewer overwrites round 1's verdict in place
- Checked at HEAD: the brief prints no path, and the footers print `record --unit X --verdict <APPROVE|REJECT> --brief <fp>` (critic.py:3118 for a rejoinder, :3147 for a first brief).
- `_RETURN_CONTRACT` stays byte-identical. `neutrality_violations` strips it by exact constant (critic.py:1904), as test_critic.py:1080 does. The path and the two header lines go on their own lines after it, and stay out of `brief_fingerprint` as the file-history section does (`reconcile.strip_file_history`).
- The path is `<UNIT>/<fp>-<token>.txt`, unique per briefing. `note_brief` (critic.py:2453) records the issued path beside the fingerprint, so story 2 can tell an issued file from a hand-made one. The header lines (`UNIT:`, `BRIEF: <fp>-<token>`) make every issued file's bytes unique, even for a bare APPROVE. `parse_verdict_block` reads only from the VERDICT line on (critic.py:2646), so the header changes no parse.
- The path is resolved from the main worktree (`git rev-parse --git-common-dir`, as mutation.py:1058-1081 does), so a brief printed inside a linked worktree still names the main checkout. Absolute, because reviewers run in worktrees: the BG0962 QA reviewer's transcript metadata records `spawnedWithWorktree: true`.
- reference-workflow-personas.md:97 describes `--from-verdict` as capturing 'the returned block'; it says the reviewer's own file now.
- Builds first in this epic, after BG0950 (with its AC4). Until then an unedited contract-shaped block in the file is still refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
