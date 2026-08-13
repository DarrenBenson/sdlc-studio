# BG0576: CI on main has been red since before v5.0.0 and both v5 tags were cut over it, because tag-check reads a locally recorded green and never asks the remote

> **Status:** Open
> **Created:** 2026-08-13
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/release_cut.py
> **Severity:** High
> **Points:** 3

## Summary

Two failures in `test_verify_ac.MarkdownEvidenceLintTests` have failed the `ci` job on every push since at least 2026-08-11, and both v5.0.0 and v5.0.1 were tagged and released over that red. Nothing in the release chain noticed, which is the part worth fixing: `release_cut.py record-green` stamps a commit from a LOCAL gate run and `tag-check` compares the tag against that stamp. Neither asks the forge whether CI passed on the pushed commit, so a repository can be green on every developer machine, red on the runner, and tagged anyway - which is exactly what happened twice.

The test failures themselves are a second, smaller defect. `_runner_candidates` has two paths: with `rg` present the candidate set is `rg --files`, which SKIPS hidden and ignored files; with rg absent the runner is `grep -rqE`, which genuinely DOES read them, so a hidden `.py` file licenses the directory and is right to. The two tests assert the rg-present behaviour and never declared that dependency, so they pass everywhere ripgrep is installed and fail where it is not. GitHub's ubuntu-latest image does not ship ripgrep.

## Steps to Reproduce

Reproduce the test half locally without any CI:

1. Build a PATH holding only the interpreter and coreutils, with no `rg`:
   `mkdir /tmp/norg && for b in python3 bash grep sed awk env ls cat cp rm mkdir chmod find sh; do ln -sf $(command -v $b) /tmp/norg/$b; done`
2. `PATH=/tmp/norg python3 -B -m pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k "unreadable_decoy or unreadable_subdirectory" -q`

Observed 2026-08-13: both tests FAIL, the same two that fail in CI, at the same assertions. With `rg` on PATH both pass.

For the release-chain half: `gh run list --workflow=lint.yml` shows `ci: failure` on the commits carrying both v5 tags, while `release_cut.py tag-check --commit <sha>` returned `gate green ... matches the tagged commit` for each, because it reads `sdlc-studio/.local/release-gate-green.json` and nothing else.

## Proposed Fix

The test half is fixed here: both tests declare the dependency with `skipUnless(shutil.which("rg"))` and CI installs ripgrep so the skip does not silently take the coverage instead. Not rewritten to pass under either runner - 'a hidden decoy does not license a prose directory' is not a claim about `grep`, and making it pass there would assert something weaker than the criterion.

The release-chain half is NOT fixed here and is the larger half. `tag-check` should refuse a tag whose pushed commit has no successful CI conclusion on the forge, in the same way `release_assets.py check` refuses a tag whose Release is missing its assets. Both are the same shape: a claim about the remote that only the remote can answer, currently answered from a local file.

## Impact

A release can be cut over a red CI with every shipped guard reporting green, which is the failure class this repository exists to prevent and has now done twice in two days. The immediate consequence was small - the two failing tests are correct assertions about a soft dependency, not broken product - but the mechanism is indifferent to what is failing. Filed High because it defeats the release gate rather than degrading it, and because the evidence that it defeats it is two tags rather than an argument.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-13 | sdlc-studio | Created via `new` (deterministic) |
