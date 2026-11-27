# BG1767: BG1764 did not converge in review: round 2 REJECT findings

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/cost_anatomy.py, .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py, changelog.d/BG1764.md
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T08:06:41Z

## Summary

BG1764 was rejected at round 2, the review cap, by agent-ae57f930a3655e1dd (qa), so it was carried as a known issue rather than reviewed again. Filed at Medium, the carry's default, which the release bar (`review.blocking_priority`) allows. The findings still open: BLOCKING: [regression] `sprint.py cost --anatomy` now exits 1 with a UnicodeDecodeError traceback when any card under `sdlc-studio/personas/seats` or `personas/amigos` is not valid UTF-8, where the base printed the anatomy: the repair's `project_seats` (cost\_anatomy.py:84, called at cost\_anatomy.py:518) reads every card through `critic._declared_reviewers`, which catches only OSError around `read_text(encoding="utf-8")` (critic.py:2907-2908). Executed on a throwaway repo with a one-call session transcript and a seat card holding `# Ren` then byte 0xe9 then `e Smith - Legal`: `python3 sprint.py cost --anatomy --session --transcripts <dir> --root .` printed rc=0 at 15136cad5 and rc=1 "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 26: invalid continuation byte" at fae691d55, with rc=0 at both once the card is removed. The close path degrades too: `run_state._cost_roles` returns "the spend by role could not be read: 'utf-8' codec can't decode byte 0xe9..." in place of the role table. The project already fixed this class as a defect (BG1667, a non-UTF-8 seat card tracebacking `persona_resolve.py`) and waived BG1675 only because a quiet empty read is harmless. Fix inside Affects: read the declared roles in `project_seats` without raising on a card that is not UTF-8 (skip that card, as `sdlc_md.read_text_safe` reads one empty, or fall back to the shipped seats) and pin a non-UTF-8 card leaving `sprint.py cost --anatomy` at rc 0 in `test_cost_anatomy.py`; [pre-existing] `sprint.py lane accept --unit BG0001 --reviewer "agent-a1 (qa)"` already tracebacks with the same UnicodeDecodeError on that card through `critic._declared_reviewers` (critic.py:2907), outside this unit's Affects, and no open bug covers it; RULINGS: Round one's "AC1 holds only for the three shipped seats" is CLOSED. Executed through `sprint.py cost --anatomy --format json` with a `<!-- role: security -->` card under personas/seats and `reviewer="agent-q0 (security)"`: the reviewer row now holds `['agent-q0', 'agent-q3', 'agent-q4']` and other `['agent-a1']` (text table: reviewer 3 agents), where round one left q0 under other. `critic.py brief --seat security` with no card is refused ("no seat card for 'security' - neither the project nor the skill carries one"), so every seat `lane accept` can record is shipped or declared, and `project_seats` covers it. On this repo `project_seats` is the shipped three, so the real ledger reads as in round one. Claim inventory, round two: `project_seats`'s docstring (shipped seats plus every role a card under personas/seats or personas/amigos declares) is TRUE, the author's test declares `legal` under personas/amigos and reads it. The `agent_key` and `agent_roles` docstrings are TRUE. The fragment's new sentences are TRUE: `agent-<id> (security)` reads its id under a declared card, and `qa` and `security` alone read None. The commit message is TRUE except where the regression above bites. Mutation: all 20 author mutants replay killed. Reviewer mutants over the three BG1764 tests, each applied once with caches purged, all KILLED: the anatomy's seats read from the working directory, the seat-alone check case-sensitive, the group check case-sensitive, the declared roles dropped, only the first card's role read, the seat-alone check against the shipped three only, and the reviewer or the author cell read without the seats. `verify_ac.py run --id BG1764 --dry-run` printed ac=1 pass=1 fail=0. In a detached worktree at fae691d55, `test_cost_anatomy`, `test_report_usd`, `test_sprint_handoff`, `test_lean_specs_v63` and `test_lean_docs_v63` ran 54 passed, and `tools/lint-style.sh changelog.d` exited 0.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1764 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1764 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [regression] `sprint.py cost --anatomy` now exits 1 with a UnicodeDecodeError traceback when any card under `sdlc-studio/personas/seats` or `personas/amigos` is not valid UTF-8, where the base printed the anatomy: the repair's `project_seats` (cost\_anatomy.py:84, called at cost\_anatomy.py:518) reads every card through `critic._declared_reviewers`, which catches only OSError around `read_text(encoding="utf-8")` (critic.py:2907-2908). Executed on a throwaway repo with a one-call session transcript and a seat card holding `# Ren` then byte 0xe9 then `e Smith - Legal`: `python3 sprint.py cost --anatomy --session --transcripts <dir> --root .` printed rc=0 at 15136cad5 and rc=1 "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9 in position 26: invalid continuation byte" at fae691d55, with rc=0 at both once the card is removed. The close path degrades too: `run_state._cost_roles` returns "the spend by role could not be read: 'utf-8' codec can't decode byte 0xe9..." in place of the role table. The project already fixed this class as a defect (BG1667, a non-UTF-8 seat card tracebacking `persona_resolve.py`) and waived BG1675 only because a quiet empty read is harmless. Fix inside Affects: read the declared roles in `project_seats` without raising on a card that is not UTF-8 (skip that card, as `sdlc_md.read_text_safe` reads one empty, or fall back to the shipped seats) and pin a non-UTF-8 card leaving `sprint.py cost --anatomy` at rc 0 in `test_cost_anatomy.py`
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [pre-existing] `sprint.py lane accept --unit BG0001 --reviewer "agent-a1 (qa)"` already tracebacks with the same UnicodeDecodeError on that card through `critic._declared_reviewers` (critic.py:2907), outside this unit's Affects, and no open bug covers it
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG1764 AC1 still passes: `cost_anatomy.agent_key` returns the agent id for `agent-<id> (<seat>)` as it does for `agent-<id>` and a bare id, `agent_roles` classes such a recorded reviewer as a reviewer, and a seat name alone still returns None
  - **Verify:** shell python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_cost_anatomy.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Filed |
| 2026-11-26 | orchestrator | Severity Low, not the fixed Medium the carry rule filed (D0645; D0642 bars Medium here for 6.5) |
