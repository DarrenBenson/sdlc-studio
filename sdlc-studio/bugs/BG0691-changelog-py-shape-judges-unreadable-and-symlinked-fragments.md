# BG0691: changelog.py shape judges unreadable and symlinked fragments differently in its two modes, and its git-failure refusals are unpinned

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/changelog.py, .claude/skills/sdlc-studio/scripts/tests/test_changelog.py, .githooks/pre-commit, AGENTS.md, changelog.d/BG0662.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0662-delivery-engineering.txt (engineering seat); verdicts/BG0662-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Working-tree mode (changelog.py:143) raises a traceback on a non-UTF-8 fragment and names none of the others, while the --staged mode refuses the same fragment cleanly with exit 2; compose already raised the same traceback before the shape verb existed. A symlinked fragment passes the working-tree check and compose, but shape --staged refuses it, because it judges the link blob rather than the target (changelog.py:118). The refusals on a git failure have no test: a mutant returning [] on a failed git listing (changelog.py:110) and one returning 0 on StagedReadError (changelog.py:393) both survive the four test modules the change touched, so a later edit could let the lane pass on a git failure with the suite green; only hand-run Coverage Rulings stand behind them. The skip for files nested below changelog.d (changelog.py:115) is unpinned too. The '59 of 119' figure in the pre-commit hook comment (.githooks/pre-commit:260), AGENTS.md:84 and changelog.d/BG0662.md is off by one: the shipped shape verb reports 60 of 119 at f763a89a, the bug's own evidence commit.

## Steps to Reproduce

1. In a throwaway repo, write a changelog.d fragment holding an invalid UTF-8 byte; python3 .claude/skills/sdlc-studio/scripts/changelog.py shape exits with a traceback. git add it; changelog.py shape --staged exits 2 naming the file. 2. Replace a valid fragment with a symlink to a copy of it; shape and compose pass; shape --staged refuses. 3. In a copy, make the git listing at changelog.py:110 return [] on failure; run `test_changelog.py` and the other touched test modules - green. 4. git worktree add at f763a89a and run changelog.py shape - it reports 60 of 119.

## Proposed Fix

Read fragments through one reader in both modes that refuses an undecodable file with exit 2 and names every bad fragment. Judge a staged symlink by its target, or refuse symlinks in both modes. Add tests that fail when a failed git listing or a StagedReadError reads as success, and one for the nested-file skip. Correct the figure to 60 of 119 in the hook comment, AGENTS.md and the fragment.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Working-tree mode (changelog.py:143) raises a traceback on a non-UTF-8 fragment and names none of the others, while the --staged mode refuses the same fragment...
- [ ] **AC2** The proposed fix lands, pinned by a test: Read fragments through one reader in both modes that refuses an undecodable file with exit 2 and names every bad fragment.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
