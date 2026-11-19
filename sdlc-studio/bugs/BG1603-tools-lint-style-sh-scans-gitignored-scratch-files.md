# BG1603: tools/lint-style.sh scans gitignored scratch files, so an untracked note under .local/ blocks a commit that does not touch it

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/lint-style.sh, tools/test_lint_style.py, changelog.d/BG1603.md
> **Evidence:** 2026-11-19: orchestrator, the website run's frictions commit (log .local/web18/commit-skill-fr.log)
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T00:06:20Z

## Summary

lint-style.sh gathers markdown with `grep -r --include='*.md' .`, excluding only `node_modules` (and worktrees for the dunder check), so it reads every gitignored `.local/` folder too. On 2026-11-19 a paperwork commit touching only sdlc-studio/ artefacts was blocked by the jargon and double-underscore checks on an orchestrator's untracked lane briefs and builder rules under .local/web18/, which quote the banned words and a lesson's `__pycache__`.

## Steps to Reproduce

Write a file .local/scratch/x.md containing one of the words the jargon check bans, stage any tracked change, and commit: the pre-commit style lane fails on the untracked, ignored file.

## Proposed Fix

Scan the files git tracks or stages (`git ls-files -co --exclude-standard -- '*.md'`) rather than the whole working tree, so an ignored path is never read.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: lint-style.sh gathers markdown with `grep -r --include='*.md' .`, excluding only `node_modules` (and worktrees for the dunder check), so it reads every...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Write a file .local/scratch/x.md containing one of the words the jargon check bans, stage any tracked change, and commit: the pre-commit style lane fails on the untracked, ignored...
- [ ] **AC3** The proposed fix lands, pinned by a test: Scan the files git tracks or stages (`git ls-files -co --exclude-standard -- '*.md'`) rather than the whole working tree, so an ignored path is never read.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
