# BG0230: a skill test's git call can reach the parent repository, so a polluted GIT_ environment lets the suite rewrite the real repo's index

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/gitutil.py,tools/skill-tests.sh
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The suites build throwaway git fixtures in temp directories and shell out to git, but nothing confines those calls to the fixture. When the ambient environment carries `GIT_DIR` / `GIT_WORK_TREE` / `GIT_INDEX_FILE` pointing at the parent repository, every fixture git call operates on the REAL repo instead. Observed live during RUN-01KY03GS, not hypothesised: a session reproducing BG0222 exported `GIT_INDEX_FILE`=$PWD/.git/index.lock together with `GIT_DIR`=$PWD/.git, and the suites then emptied this repository's index - all 1845 tracked files staged as deletions, with a fixture's 'git commit -qm base' left running against main. No data was lost (the working tree was untouched and git reset restored the index), but a commit in that window would have deleted the repository contents. BG0222 covers the narrower case of the pre-commit hook leaking `GIT_` into the suites. This is the wider one: the fixtures have no containment of their own, so ANY polluted environment - a hook, a CI runner, a developer's shell, or a test of git behaviour itself - reaches the parent repo. Defence belongs at the fixture, not only at the hook, because the hook is not the only source.

## Steps to Reproduce

From the repo root: `GIT_INDEX_FILE`=$PWD/.git/index.lock `GIT_DIR`=$PWD/.git `GIT_WORK_TREE`=$PWD python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests. Observed: git ls-files drops from 1845 to a handful, git status reports the tree staged as deleted, and a stale 252KB .git/index.lock is left behind. Expected: the fixtures operate only on their own temp repos and the parent index is byte-identical afterwards.

## Proposed Fix

Confine the fixtures rather than only scrubbing the caller. Have the shared git fixture helper build its environment explicitly - set `GIT_DIR` and `GIT_WORK_TREE` to the fixture and clear the inherited repo-locating variables - so a fixture git call cannot address the parent repo whatever the ambient environment holds. Add a guard test that runs a fixture under a deliberately polluted environment and asserts the parent repo's index hash is unchanged afterwards; that test is what keeps the containment honest, and it is the assertion this incident would have failed. BG0222's hook-side scrub remains worth doing as defence in depth, but it is not sufficient on its own.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
