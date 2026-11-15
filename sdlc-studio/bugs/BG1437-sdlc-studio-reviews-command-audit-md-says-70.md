# BG1437: sdlc-studio/reviews/command-audit.md says 70 scripts while the tree holds 71, since evidence_pack.py landed, and no check refuses the stale count

> **Status:** Open
> **Severity:** High
> **Points:** 1
> **Affects:** sdlc-studio/reviews/command-audit.md, tools/tests/test_lean_release_verify.py, changelog.d/BG1437.md
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1268, qa-seat-BG1268-r1 ([pre-existing])
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T02:32:40Z

## Summary

Regenerating `sdlc-studio/reviews/command-audit.md` with `command_audit.py --check-tools --write` at HEAD moves '70 scripts' to '71 scripts': the extra script is `scripts/evidence_pack.py` (US1155, US1156). Nothing in the commit hooks or the suite read the stale count, so the committed audit drifted silently.

## Steps to Reproduce

Run `command_audit.py --check-tools --write` at HEAD and diff command-audit.md: the script count moves from 70 to 71.

## Proposed Fix

Regenerate the audit, and add a check (in the suite or the budgets lane, like docgen surface --check) that refuses a committed audit out of step with the tree.

## Acceptance Criteria

- [ ] **AC1** Given HEAD, when `command_audit.py --check-tools` output is compared with the committed `sdlc-studio/reviews/command-audit.md`, then they are identical, so US0251's AC2 and the release-verify tests pass at the push boundary. Fails on: the committed audit still counting 70 scripts.
  - **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/command_audit.py --check-tools | diff - sdlc-studio/reviews/command-audit.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-15 | Claude Opus 5.5 (run twelve) | Raised to High and re-scoped: the release-verify test (US0251 AC2, tools/tests/test_lean_release_verify.py) already refuses a stale audit at the push boundary and is red now, so the fix is regenerating the audit; the criterion names that check |
