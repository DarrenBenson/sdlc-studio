# BG0576: CI on main has been red since before v5.0.0 and both v5 tags were cut over it, because tag-check reads a locally recorded green and never asks the remote

> **Status:** Fixed
> **Verification depth:** functional (executed through the shipped CLI against the real forge: the exact commit v5.0.1 was tagged on is now REFUSED naming 'Lint: failure', a commit CI passed on is ALLOWED, an unknown commit and an unresolvable remote are refused, and a remoteless clone still tags; mutation: 5 declared mutants, all KILLED, restore byte-exact)
> **Created:** 2026-08-13
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py
> **Severity:** High
> **Points:** 3

## Summary

Two failures in `test_verify_ac.MarkdownEvidenceLintTests` have failed the `ci` job on every push since at least 2026-08-11, and both v5.0.0 and v5.0.1 were tagged and released over that red. Nothing in the release chain noticed, which is the part worth fixing: `release_cut.py record-green` stamps a commit from a LOCAL gate run and `tag-check` compares the tag against that stamp. Neither asks the forge whether CI passed on the pushed commit, so a repository can be green on every developer machine, red on the runner, and tagged anyway - which is exactly what happened twice.

The test failures themselves are a second, smaller defect. `_runner_candidates` has two paths: with `rg` present the candidate set is `rg --files`, which SKIPS hidden and ignored files; with rg absent the runner is `grep -rqE`, which genuinely DOES read them, so a hidden `.py` file licenses the directory and is right to. The two tests assert the rg-present behaviour and never declared that dependency, so they pass everywhere ripgrep is installed and fail where it is not. GitHub's ubuntu-latest image does not ship ripgrep.

## Acceptance Criteria

- [x] **AC1** Given a commit whose CI concluded `failure` on the forge, when `tag-check` runs against it, then the tag is refused and the refusal names the failing workflow and its conclusion.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k a_failed_ci_conclusion_refuses
  - **Verified:** yes (2026-08-14)
- [x] **AC2** Given a commit the forge has no CI run for, when `tag-check` runs against it, then the tag is refused - never having been judged is not a green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k never_run_refuses
  - **Verified:** yes (2026-08-14)
- [x] **AC3** Given a forge that cannot be asked (no `gh`, an unauthenticated or failing `gh`, or an unparseable answer), when `tag-check` runs, then the tag is refused rather than passed - "I could not look" must not be reported as "there is nothing wrong".
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k cannot_be_asked_refuses
  - **Verified:** yes (2026-08-14)
- [x] **AC4** Given a clone with no git remote, when `tag-check` runs on a locally green commit, then the tag is ALLOWED - there is no forge to ask, and this is the one pass that keeps AC3's refusal honest rather than universal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k no_remote_is_the_one_honest_pass
  - **Verified:** yes (2026-08-14)
- [x] **AC5** Given an abbreviated commit sha, when the forge is asked about it, then it is resolved to the full sha first - `gh` matches only on the full sha and answers nothing for a short one, which AC2 would otherwise read as a refusal on a green tree.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k abbreviated_sha_is_resolved
  - **Verified:** yes (2026-08-14)
- [x] **AC6** Given a git that cannot answer - absent from PATH, refusing the repository, timing out - when the forge state is read, then it is `unknown` and the tag is refused; a question that could not be asked is not an answer in the reassuring direction.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k git_that_cannot_answer
  - **Verified:** yes (2026-08-14)
- [x] **AC7** Given a repository git will not READ, which reports `not a git repository` verbatim, when the forge state is read, then it is `unknown` - the message is believed only when the filesystem agrees there is no `.git`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k unreadable_repository
  - **Verified:** yes (2026-08-14)
- [x] **AC8** Given a forge `gh` cannot address - GitLab, Bitbucket, self-hosted - when a tag is checked, then it is ALLOWED and the reason says CI was not consulted; a bug fix may not invent a hard GitHub requirement this shipped tool never had.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k forge_gh_cannot_query
  - **Verified:** yes (2026-08-14)
- [x] **AC9** Given an empty commit or a flag-shaped ref, when the forge is asked, then the empty commit is refused and the flag-shaped ref is passed through unresolved rather than executed as an option.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py -k "empty_commit_is_never_asked or flag_shaped_ref"
  - **Verified:** yes (2026-08-14)

## Steps to Reproduce

Reproduce the test half locally without any CI:

1. Build a PATH holding only the interpreter and coreutils, with no `rg`:
   `mkdir /tmp/norg && for b in python3 bash grep sed awk env ls cat cp rm mkdir chmod find sh; do ln -sf $(command -v $b) /tmp/norg/$b; done`
2. `PATH=/tmp/norg python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k "unreadable_decoy or unreadable_subdirectory" -q`

Observed 2026-08-13: both tests FAIL, the same two that fail in CI, at the same assertions. With `rg` on PATH both pass.

For the release-chain half: `gh run list --workflow=lint.yml` shows `ci: failure` on the commits carrying both v5 tags, while `release_cut.py tag-check --commit <sha>` returned `gate green ... matches the tagged commit` for each, because it reads `sdlc-studio/.local/release-gate-green.json` and nothing else.

## Proposed Fix

The test half is fixed here: both tests declare the dependency with `skipUnless(shutil.which("rg"))` and CI installs ripgrep so the skip does not silently take the coverage instead. Not rewritten to pass under either runner - 'a hidden decoy does not license a prose directory' is not a claim about `grep`, and making it pass there would assert something weaker than the criterion.

The release-chain half is now fixed too. `tag-check` asks the forge for the CI conclusion on the tagged commit and refuses anything that is not a success, in the same shape `release_assets.py check` uses for the same question about the same forge. The states are kept apart rather than collapsed: no run at all, a run still in flight, and a forge that cannot be read are each refused with their own reason, and only a clone with no remote passes without an answer - the one case where there is genuinely nothing to ask.

One defect in the fix was found by its own positive control rather than by reasoning: `gh run list --commit` matches on the full sha and answers nothing for an abbreviated one, which the guard would have read as "never run" and refused. The commit is resolved before the forge is asked.

## Impact

A release can be cut over a red CI with every shipped guard reporting green, which is the failure class this repository exists to prevent and has now done twice in two days. The immediate consequence was small - the two failing tests are correct assertions about a soft dependency, not broken product - but the mechanism is indifferent to what is failing. Filed High because it defeats the release gate rather than degrading it, and because the evidence that it defeats it is two tags rather than an argument.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in release_cut.py `forge_ci_state`, report a failed CI conclusion as success | Given a commit whose CI concluded `failure` on the forge, when `tag-check` runs |
| AC2 | in release_cut.py `forge_ci_state`, report a commit the forge never ran as success | Given a commit the forge has no CI run for, when `tag-check` runs against it, then |
| AC3 | in release_cut.py `forge_ci_state`, let a missing gh borrow the no-forge pass | Given a forge that cannot be asked (no `gh`, an unauthenticated or failing `gh`, or |
| AC4 | in release_cut.py `forge_ci_state`, report a remoteless clone as unknown so the guard refuses everything | Given a clone with no git remote, when `tag-check` runs on a locally green commit, |
| AC5 | in release_cut.py `forge_ci_state`, ask the forge about the unresolved (abbreviated) sha | Given an abbreviated commit sha, when the forge is asked about it, then it is |

## Round two

An independent review REJECTED the first repair and was right twice.

**The fix re-created the defect it removes.** `_has_forge_remote` returned a bare bool, so every way git can fail - absent, refusing the repository for dubious ownership, timing out - collapsed into `False`, read as "no forge to ask", and PASSED the tag. A question that could not be asked, answered in the reassuring direction: the exact shape of the original bug. No test could fail on it, because the fixture scripted only success-with-empty-output. The probe is now tri-state.

The first repair of that was itself insufficient, which is worth recording: git prints `not a git repository` VERBATIM for a repository it cannot read - `chmod 000 .git` produces it - so believing the message re-opened the hole one branch along. It is now believed only when the filesystem agrees there is no `.git`.

**The fix made every non-GitHub consumer permanently un-taggable.** `release_cut.py` is SHIPPED, and a GitLab-hosted project could not tag at all, with no config, flag or env override - while the shipped gate documentation states that nothing in it is GitHub-specific and carries a GitLab CI section. A forge this code does not know HOW to ask is not a forge that would not answer, so `unsupported` is now its own state: it passes, for the same reason a remoteless clone does, and the tag says out loud that CI was not consulted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-13 | sdlc-studio | Created via `new` (deterministic) |
