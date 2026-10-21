# BG1104: A message-only amend runs the whole-workspace gate at commit, because the hook's gate lane reads an empty staged diff as no diff to scope to

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_pre_commit_amend_scope.py, changelog.d/BG1104.md
> **Evidence:** 2026-10-20: amending fb662466's message only (adding Refs trailers, giving fd16f28a), the hook ran `gate.py --root .` for about 11 minutes at load average 11-13. Re-run under cProfile on the same clean tree: gate cost 330.0 s, conformance 280.2 s 'scope: there was no diff to scope to ... so the WHOLE workspace was judged (1086 unit(s))'. The original commit, fb662466, passed the same lane in seconds. The profile puts 125 s in critic.read_verdicts, called once per unit (812 times), and 130 s in 257 verify_ac collection subprocesses.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T16:29:31Z

## Summary

The pre-commit hook's gate lane runs `gate.py --root .`, which scopes its diff-scoped lanes (conformance, validate) to `changed_paths`. `git commit --amend` with nothing newly staged leaves the index equal to HEAD, so the change set is empty. The lanes then judge the whole workspace and say 'there was no diff to scope to (a clean tree, or the git probe could not answer)'. A commit that changes only its message pays the full conformance scan: 330 s profiled on a quiet workstation, and about 11 minutes under load. The commit before it, staging the same content, passed the same lane in seconds.

## Steps to Reproduce

Make a commit, then run `git commit --amend -F <message>` with nothing staged: the hook's gate lane takes minutes, and `gate.py --root .` on the same clean tree prints conformance judged over the WHOLE workspace (1086 units).

## Proposed Fix

Have the hook pass the commit's own staged change set to the gate lane, so an empty staged diff judges nothing new and says so. Keep the whole-workspace scan for an unanswered probe (None), never for an empty answer.

## Acceptance Criteria

- [ ] **AC1** A commit that stages nothing new over HEAD runs the hook's gate lane over no unit, and names that scope
  - **Verify:** pytest tools/tests/test_pre_commit_amend_scope.py::PreCommitAmendScopeTests::test_a_message_only_amend_judges_no_unit
- [ ] **AC2** `gate.py --root .` run outside the hook on a clean tree still judges the whole workspace, so a committed story with an invalid status still fails it
  - **Verify:** pytest tools/tests/test_pre_commit_amend_scope.py::PreCommitAmendScopeTests::test_a_clean_tree_outside_a_commit_is_still_judged_whole

## Impact

Each message-only amend costs one to eleven minutes for no new judgement. That pushes authors towards `--no-verify` or towards leaving a message uncorrected, such as one missing its `Refs:` trailers.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
