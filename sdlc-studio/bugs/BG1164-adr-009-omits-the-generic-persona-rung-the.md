# BG1164: ADR-009 omits the generic persona rung, the TRD gh-caller scan reads only a literal argv, and sprint's fetch-failure reason is garbled

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1164.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1101 APPROVE by qa-seat-US1101-r1 (brief 496f017ba165).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T07:57:22Z

## Summary

qa-seat-US1101-r1's APPROVE of US1101 (2026-11-01) left two low findings and noticed one older one. (1) ADR-009's resolution order in sdlc-studio/trd.md ends 'then the shipped default, then no card', but `persona_resolve.py`:196 returns `default_card(role) or generic_schema()`, so the generic amigo-template comes before None. That rung is reachable only by an in-process caller with an extra role. (2) `_runs_gh` in tools/tests/`test_lean_trd_refresh.py` recognises only a literal "gh" argv[0], so a caller written `subprocess.run([GH_BIN, ...])` passes with no table row (mutant M13 survived). (3) Pre-existing: against an unreachable origin, `sprint.origin_drift`'s reason reads 'fetch from origin failed: and the repository exists.', the last line of git's stderr, from sprint.py `_git_failure`.

## Steps to Reproduce

1. Read ADR-009 against `persona_resolve.py`:196.
2. Add `GH_BIN = "gh"` and a call through it to a script in a throwaway worktree, then run `test_every_gh_caller_is_listed`: green.
3. Run `sprint.origin_drift` against an unreachable origin and read the reason.

## Proposed Fix

Name the generic rung in ADR-009. Resolve a module-level string constant used as argv[0] in the scan. Have `_git_failure` keep git's first meaningful stderr line, not its last.

## Acceptance Criteria

- [ ] **AC1** ADR-009 names the generic schema rung before 'no card'.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py
- [ ] **AC2** A gh caller whose argv[0] is a module constant equal to "gh" fails `test_every_gh_caller_is_listed` until the table lists it.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py
- [ ] **AC3** An unreachable-origin fetch failure's reason names git's actual error line.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py

## Impact

One TRD sentence is imprecise, one scan can miss an indirect caller, and one refusal reason reads as nonsense.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
