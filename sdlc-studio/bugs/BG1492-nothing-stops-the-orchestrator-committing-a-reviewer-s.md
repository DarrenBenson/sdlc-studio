# BG1492: Nothing stops the orchestrator committing a reviewer's half-written verdict: git add of the records sweeps in a verdict file still being written

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG1492.md
> **Evidence:** Run fourteen (RUN-01M7GEHM), US1161 accept, 2026-11-15.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:33Z

## Summary

In run fourteen, the orchestrator committed accepted units' records with `git add -A sdlc-studio/` while a reviewer was still writing US1161's verdict, so a half-written verdict (its line citations incomplete) went into a commit. A verdict file being written has no marker the commit can see, and the hooks do not refuse a verdict that `critic.py record` has not yet read.

## Steps to Reproduce

1. Start a reviewer writing a verdict under sdlc-studio/reviews/.
2. Before it finishes, commit the records with git add -A sdlc-studio/.
3. See the partial verdict committed.

## Proposed Fix

Have critic.py write verdicts through a temp file and rename it into place, and have the pre-commit hook refuse a staged verdict file that no recorded review row cites.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In run fourteen, the orchestrator committed accepted units' records with `git add -A sdlc-studio/` while a reviewer was still writing US1161's verdict, so a...
- [ ] **AC2** The proposed fix lands, pinned by a test: Have critic.py write verdicts through a temp file and rename it into place, and have the pre-commit hook refuse a staged verdict file that no recorded review...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
