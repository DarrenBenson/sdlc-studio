# US1011: A review brief names the file the reviewer writes its verdict to

> **Status:** Ready
> **Delivers:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_verdict_path.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_author_self_check.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/reference-scripts-review.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/US1011.md
> **Epic:** EP0280
> **Points:** 2
> **Depends on:** BG1030
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

- Release: after 6.3.0, in run ten (D0461); 6.3.0 shipped without it (D0355 breakdown G6, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: the path printed relative to the working directory (a reviewer in its own worktree then writes out of the recorder's reach); `_RETURN_CONTRACT` parameterised, which breaks `neutrality_violations`' exact strip (critic.py:2204); or the footer still printing `--verdict <APPROVE|REJECT> ...`
- AC2 must fail on: the path or header lines left inside the fingerprinted text, so every brief's fingerprint differs and `rebrief_notice` warns about a scope that has not changed
- AC3 must fail on: a path derived from the unit and seat alone, so the round-2 reviewer overwrites round 1's verdict in place
- Checked at HEAD (2026-11-12): the brief prints no path (critic.py holds no `verdicts/` string), and both footers print `critic.py record --unit X --verdict <APPROVE|REJECT> --brief <fp> --tier <tier> ...` on stderr (critic.py:4157-4162 for a rejoinder, critic.py:4195-4200 for a first brief). No criterion is met. AC2's same-fingerprint half already holds, because the brief is deterministic (test_critic.py:2779); its different-path half does not.
- `_RETURN_CONTRACT` stays byte-identical. `neutrality_violations` strips it by exact constant (critic.py:2204), as test_critic.py:1080 does. The path and the two header lines go on their own lines after it, and stay out of `brief_fingerprint` as the file-history section does (`reconcile.strip_file_history`).
- The path is `<UNIT>/<fp>-<token>.txt`, unique per briefing. `note_brief` (critic.py:3236) records the issued path beside the fingerprint, so story 2 can tell an issued file from a hand-made one. The header lines (`UNIT:`, `BRIEF: <fp>-<token>`) make every issued file's bytes unique, even for a bare APPROVE. `parse_verdict_block` reads ISSUES and BLOCKING only after the VERDICT line (critic.py:3605), so the header changes no parse.
- The path is resolved from the main worktree (`git rev-parse --git-common-dir`, as mutation.py:1066-1093 does, dropping an inherited `GIT_DIR` first because git hooks set it; lib/lanes.py:112 reads it too), so a brief printed inside a linked worktree still names the main checkout. Absolute, because reviewers run in worktrees: the BG0962 QA reviewer's transcript metadata records `spawnedWithWorktree: true`, as a QA reviewer's `.meta.json` still does under Claude Code 2.1.318.
- reference-workflow-personas.md:97 describes `--from-verdict` as capturing 'the returned block'; it says the reviewer's own file now.
- The strip belongs in `brief_fingerprint` itself, not only in `cmd_brief`: `sprint lane land` saves the brief's whole stdout (lib/lanes.py:217-221), and `lanes._brief_of` (lib/lanes.py:322-331) and `resume_brief._approved` (lib/resume_brief.py:167) fingerprint that saved text. Keep the `review tier:` and `brief fingerprint:` stderr lines unchanged: lib/lanes.py:224-225 parses them.
- Existing tests this change reaches: test_critic_author_self_check.py:94 asserts stdout is exactly `critic.brief()` plus a newline; test_lean_brief_handover.py:66, test_lane_land.py:236 and test_lane_accept.py:101 and :279 fingerprint a printed or saved brief; test_critic.py holds the neutrality tests (lines 1064-1140) and the fingerprint tests (lines 2752-2789 and 2941).
- Builds first in this epic, after BG1030. Until then an unedited contract-shaped block carrying prose after `BLOCKING: none` is still refused. BG1030 AC3 adds a RULINGS line after the rejoinder's contract; the path lines go after that.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Release note stale: the story says 'Release: 6.2' but D0382 (2026-10-20, supersedes D0381) sets the path to the 6.2.0 tag as run three plus run four's doc refreshes only, so this lands after 6.2.0; re-tag when a run takes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G6 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-12 | Claude Opus 5.5 (engineering seat) | Re-groomed at HEAD for run ten: line references moved to HEAD, release line set to run ten, Affects gains five existing test modules that pin the brief's stdout and fingerprint, the fingerprint strip placed in `brief_fingerprint` for the saved-brief readers |
