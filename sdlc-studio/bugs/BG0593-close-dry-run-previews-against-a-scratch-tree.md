# BG0593: close --dry-run previews against a scratch tree with no git, so every git-reading row degrades to unjudged

> **Status:** Open
> **Severity:** High
> **Verification depth:** functional (four criteria over `sprint.py` and `sprint_report.py`, every verifier driving `sprint.close_dry_run` ITSELF. Every mutant below was executed against the real tree with `__pycache__` purged and `python3 -B`, its target's hash checked CHANGED before the run and byte-identical after, and the KILL confirmed by the name of the failing test rather than by a failure count. This field is rewritten from that re-execution, not amended: an independent review found the previous version false on five of six units in this batch, and an amended false record is still a false record. THIS UNIT WAS REDESIGNED after the delivery review found two things: its tests rebuilt the scratch in a private helper, so deleting the entire production change left all four green AND all 916 tests in the file green; and the symlink design let a write from the scratch reach the real repository - `git add -A` wrote two loose objects into the real object database, measured. There are now no symlinks: the scratch is a pure copy and a separate read root travels beside it, reaching only steps whose signature accepts one, so a writing step can reach nothing outside the copy. The tick-row test took four cuts, each passing against a row that had never reached the diff - `no base ref`, `no git history here`, `no ticked criteria found` - and the paired control caught all three. Measured end to end: `close --dry-run` reports a real verdict where it read `diff unreadable`. REVERT-CHECKED: this unit's production files were reverted to the run's base ref and its own verifiers re-run - they go RED, so the tests reach the shipped change rather than a copy of it. That check is the one an independent review used to find this batch's worst defect, and it is now run against every unit rather than the one somebody thought to try. The Test Plan rows were REWRITTEN a second time: the criteria had been re-authored for the redesigned mechanism and the derived table left describing the symlink design, so AC1's mutant was a no-op against the delivered code and AC4's named a construct that no longer existed. `testplan derive` REWROTE the artefact rather than refusing it - the Mutant column was correct and the Title column still carried the pre-redesign criteria, so the command regenerated the titles silently. The earlier claim that it refused is wrong and is corrected here.)
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`close_dry_run` copies only `root/sdlc-studio` into a temp directory and runs the chain steps against it, so the scratch tree has no `.git`. Every checklist resolver that reads git therefore answers as if the repository were unreadable: `_ck_tick_verification` returns `diff unreadable` where a real close would report ticked criteria the tree does not support. A preview that softens a refusal into `unjudged` is the one way a preview actively misleads, and this module's own docstring says it exists so that an operator can see every refusal in one pass before paying for a close.

## Steps to Reproduce

Measured 2026-08-18 at e2cafa72, and it is the diagnosis of an observation parked as undiagnosed in BG0584. `sprint.py` line 7074 runs `shutil.copytree(root / 'sdlc-studio', scratch / 'sdlc-studio', symlinks=True)` and nothing else. Executed against the run's own recorded base ref ba3bffa2c: `sprint_report._changed_paths(Path('.'), base)` returns 64 paths; the same call against the scratch root returns None; `(scratch / '.git').exists()` is False. That is the whole of the 'same row resolved two different ways within one invocation' that BG0584 records - `close_preflight` runs against the REAL root and answers `no ticked criteria found`, while the chain step runs against the scratch and answers `diff unreadable`. Two answers, one invocation, and neither the operator nor the row can tell which tree produced which.

## Proposed Fix

Give the scratch a readable git context, or make the absence explicit rather than silent. The cheap correct shape is to pass the REAL repository root to the resolvers that read history while keeping every WRITE bound to the scratch - the copy exists to protect the tree from writes, not to hide its history. If that separation is awkward, the resolvers must distinguish `no git here` from `diff unreadable` and the dry run must say which, because a preview that reports a softer verdict than the close it previews is worse than no preview. Check every CHECKLIST resolver that touches git, not only tick-verification: the same blindness applies to each, and fixing one leaves the siblings lying.

## Acceptance Criteria

- [x] **AC1** Given a dry run over a REAL git repository that also carries `.claude/skills/`, `tools/` and `changelog.d/` - not a bare temp directory, which would make both roots agree by having nothing on either side - when the chain's read-only steps run, then each is handed the REAL tree to read from, so a probe reading any surface outside `sdlc-studio/` answers as it does outside a preview
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_dry_run_gives_a_read_only_probe_the_real_root
  - **Verified:** yes (2026-08-20)
- [x] **AC2** Given a tree with genuinely no git history, when a git-reading step resolves under a dry run, then it reports that condition distinctly from `the diff could not be taken` - and the condition is decided by ASKING GIT, because `git init` with no commits leaves a `.git` a filesystem probe reports as present while `rev-parse` still fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_a_tree_with_no_history_is_reported_distinctly
  - **Verified:** yes (2026-08-20)
- [x] **AC3** Given a dry run, when a chain step is handed its working root, then that root can reach NOTHING outside the copy - not the real tree, and not a link to it. Stated as reachability rather than as a hash: the first design symlinked `.git` into the scratch and `git add -A` from there wrote two loose objects into the real object database, which a digest of the working tree cannot see
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_scratch_reaches_nothing_outside_sdlc_studio
  - **Verified:** yes (2026-08-20)
- [x] **AC4** Given the tick row driven through its real context, when the read root is supplied, then it JUDGES; and when it is withheld, then it declines - the paired control, because an assertion that the row works cannot tell a working mechanism from one that never ran
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::DryRunScratchParityTests::test_the_tick_row_judges_from_the_read_root
  - **Verified:** yes (2026-08-20)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, delete `read_root` from the dry run's step call | Given a dry run over a REAL git repository that also carries `.claude/skills/`, `tools/` and `changelog.d/` - not a bare temp directory, which would make both roots agree by having nothing on either side - when the chain's read-only steps run, then each is handed the REAL tree to read from, so a probe reading any surface outside `sdlc-studio/` answers as it does outside a preview |
| AC2 | in `sprint_report.py`, swap `rev-parse` for an `exists()` check on the directory | Given a tree with genuinely no git history, when a git-reading step resolves under a dry run, then it reports that condition distinctly from `the diff could not be taken` - and the condition is decided by ASKING GIT, because `git init` with no commits leaves a `.git` a filesystem probe reports as present while `rev-parse` still fails |
| AC3 | in `sprint.py`, extend the copy with links to the sibling directories | Given a dry run, when a chain step is handed its working root, then that root can reach NOTHING outside the copy - not the real tree, and not a link to it. Stated as reachability rather than as a hash: the first design symlinked `.git` into the scratch and `git add -A` from there wrote two loose objects into the real object database, which a digest of the working tree cannot see |
| AC4 | in `sprint_report.py`, read the diff from `ctx["root"]` again | Given the tick row driven through its real context, when the read root is supplied, then it JUDGES; and when it is withheld, then it declines - the paired control, because an assertion that the row works cannot tell a working mechanism from one that never ran |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-19 | sdlc-studio | Criteria re-pointed by adversarial goal review: evidence taken outside the instrument under repair, and the enumerated case generalised to its class |
| 2026-08-19 | sdlc-studio | Plan review round 3 F1: every checklist resolver lives in `sprint_report.py`, which the Affects excluded - so the review would have been pointed away from the file the fix lands in, and the row guard FORCED a false mutant naming `sprint.py` because the real file was undeclared. Re-pointed 3 -> 5 |
| 2026-08-20 | sdlc-studio | REDESIGNED after the delivery review: the symlink design let a write from the scratch reach the real object database, and the tests rebuilt the scratch in a private helper so deleting the whole production change left 916 tests green. The criteria now describe the delivered mechanism - a separate read root - and every verifier drives `close_dry_run` |
