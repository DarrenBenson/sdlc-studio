# CR-0389: Nothing reports that the installed skill copy has drifted from the repo, so the operator has to remember to ask

> **Status:** In Progress
> **Decomposed-into:** EP0144
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** tools/forward-port.sh,.githooks/pre-commit,.claude/skills/sdlc-studio/scripts/status.py,AGENTS.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

AGENTS.md documents forward-port.sh as the way to mirror the repo skill tree into the installed copy, but nothing ever says the copy is stale. No gate checks it, the close chain does not check it, `status hint` does not mention it, and the sprint plan does not. The only signal is an operator remembering to ask. Measured this session: the operator asked 'have you forward ported?' during RUN-01KY321Q, it was applied, and then the repair round and the six close commits landed on top - so by the next session 22 files had drifted again, including gate.py, retro.py, sprint.py, mutation.py and eleven test modules, plus a lessons file that did not exist in the installed copy at all. The operator had to ask a SECOND time to surface it. This matters beyond tidiness because the installed copy is what every OTHER project on this machine actually runs: a fix verified green in the dev repo is not in force anywhere until the mirror happens, so the window between a fix landing and the mirror running is a window in which the operator believes a shipped defect is fixed. It is also cheap to detect - `forward-port.sh` already computes the itemised difference in dry-run mode and could exit non-zero when it is non-empty.

## Impact

The operator and any agent working in this repo. The failure is silent and fails open: everything reads green in the dev repo while the installed copy - the one consuming projects load - still runs the old code. Nothing distinguishes 'mirrored' from 'never mirrored since the fix', so the only defence is human memory, which has now failed twice in two sessions with the same operator actively watching for it.

## Acceptance Criteria

- [ ] A drift check exists that exits non-zero when the installed copy differs from the repo skill tree, and names the count of differing files rather than only listing them.
- [ ] The check is surfaced somewhere the operator or agent already looks - `status hint` and/or the sprint close chain - rather than in a command that must be remembered.
- [ ] A machine with no installed copy, or one deliberately pinned, is reported as such and does not fail the check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
