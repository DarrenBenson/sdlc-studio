# BG1521: The tag gate checks the known-issues page but never the release bar, so a tag passes with an open High finding

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** tools/known_issues.py, .githooks/pre-push, tools/tests/test_known_issues.py, tools/tests/test_pre_push_hook.py
> **Evidence:** audit AUDIT-2026-11-17, project profile, code lens, survived 3 of 3 refute votes; observed at .githooks/pre-push lines 71-87 (the `for sha in $tag_shas` loop); tools/known_issues.py `_check` (line 486) and the `bar` mode (line 422)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:01Z

## Summary

The tag path of `.githooks/pre-push` runs only the `check` mode of `tools/known_issues.py` at each tagged commit. That mode compares the page with the Medium and Low corpus and never reads the barred severities. The `bar` mode, which exits non-zero while a Critical or High finding is open, is called by no hook, no `gate.py` lane and no workflow, and it has no `--at` flag, so it could only judge the working tree. The page that `check` certifies states that there is zero open Critical or High finding at the tag, and a recorded decision says the bar refuses the tag, yet nothing in the command people run enforces it. The release bar rests on a per-release story criterion and the operator remembering to run it.

## Steps to Reproduce

1. Read .githooks/pre-push lines 71 to 87: the loop over tagged commits calls `known_issues.py` check with --at and nothing else.
2. Read tools/`known_issues.py`: `_check` (about line 486) never calls `barred_open`, and the bar parser (about line 414) takes no `--at`.
3. Build a fixture workspace with one Open Critical bug and a known-issues page rendered from its corpus.
4. Run `known_issues.py` check with --root on the fixture: it reports the page agrees with the corpus and exits 0, although the page says zero open Critical or High finding.
5. Run `known_issues.py` bar with --root on the same fixture: it reports the release bar is not met and exits 1.

## Proposed Fix

Give the `bar` mode an `--at` flag that judges the bug corpus at a commit, as `check` already does, and call it from the pre-push tag loop beside `check`, refusing the tag when a barred severity is open at the tagged commit. Keep the could-not-run branch distinct from a real refusal. Pin the refusal and a passing control in the known-issues test and in the pre-push hook test.

## Acceptance Criteria

- [ ] **AC1** Given a repository where one commit's bug corpus holds an Open Critical bug and the working tree no longer does, when `tools/known_issues.py bar --at <that commit>` runs, then it reports the release bar is not met and exits 1; `bar --at` a commit with no barred finding open exits 0. Fails on: `bar` rejecting `--at`, or judging the working tree in place of the commit.
  - **Verify:** pytest tools/tests/test_known_issues.py::ReleaseBarTests::test_bar_at_judges_the_corpus_at_the_commit
- [ ] **AC2** Given a tag on a commit that holds an Open High bug and a known-issues page agreeing with its corpus, when the tag is pushed through `.githooks/pre-push`, then the push is refused, naming the release bar and the tagged commit; a tag on a commit with no barred finding open passes the tag loop. Fails on: a tag that passes with a Critical or High finding open at its commit.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::TheTagPathReadsTheReleaseBarTests::test_a_tag_with_an_open_high_finding_is_refused
- [ ] **AC3** Given a tagged commit at which the bar cannot run (an exit status other than 0 or 1), when the tag is pushed, then the hook refuses saying the release bar could not run on that commit, in wording distinct from the bar-not-met refusal. Fails on: a could-not-run reported as an open finding, or let through.
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::TheTagPathReadsTheReleaseBarTests::test_a_bar_that_could_not_run_is_not_reported_as_a_refusal

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
