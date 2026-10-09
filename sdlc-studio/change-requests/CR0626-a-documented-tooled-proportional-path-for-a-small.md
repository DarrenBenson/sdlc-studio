# CR-0626: A documented, tooled proportional path for a small change, so a one-file fix keeps the parts that catch defects and drops the rest

> **Status:** In Progress
> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson (2026-10-09)
> **Decomposed-into:** EP0286
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-philosophy.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/help/bug.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md
> **Evidence:** Operator-relayed assessments of three consuming projects' runs, 2026-10-08, each unprompted: 'Overkill for small changes: for a one-file fix this' (agent-fleet, 1,200 minutes against a 720-minute appetite); 'overkill for a one-line fix or exploratory work' (homelab, about 2.4M tokens for 21 points); 'A one-file fix does not need this loop. A release that someone else will trust does.' (sdlc-studio-lens). All three named the same three parts as where the value was: executable checks that fail at base, mutation, and the author never recording its own review. This repository fast-tracks single bugs by operator ruling (D0350, D0351) with no documented shape.
> **Date:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T11:37:44Z

## Summary

No reference or help page says what a small change may skip. Agents either run the full sprint loop (registers, indexes, charter, goal review, report, signature) for a one-file fix, or improvise a fast-track per ruling. Define the proportional path: a single unit with an executable criterion that fails at base, a light-tier independent review, and the terminal transition - without a run, goal review, report or signature - and say when a change stops qualifying (more than one unit, production runtime, security or contract surface).

## Impact

Agents and operators pay the sprint loop's full cost for changes where its extra parts catch nothing, and learn to see the skill as overhead.

## Acceptance Criteria

- [ ] A reference page states the small-change path: what it keeps, what it skips, and the conditions that disqualify a change from it
- [ ] The path is runnable end to end with shipped commands, each named in the toolchain runbook, with no step done by hand

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Raised |

## Amigo Consult

_Consulted 2026-10-09: Dani Okafor (engineering, lead), Lena Marsh (product), Sam Eriksson (qa). Settle before building._

- Review tier: confirm the derived tier, not the CR's 'light-tier' wording (panel recommends it). The path then drops ceremony, not scrutiny, and in this repository most path units will take a full review.
- Cut line if 6.2 is tight: do not cut the check story while the terminal story ships, or the close-owed exemption is open to any change. The panel's smallest safe cut moves the one-production-file and open-run-overlap refusals into the start story, and defers protected surfaces and diff growth. Take all of the check story (recommended), or that cut?
- Accept that a path unit's review findings never reach a lessons pass? Panel: accept, as the price the CR asks for; the page says so.
- A run awaiting signature shuts the path for every change, because any commit moves the tree `sprint sign` checks. A project that leaves runs unsigned for days has no small path meanwhile. Panel: right; the page says so. Confirm?
- If G10's CR0622 is in 6.2, merge `small_change.protected` into `review.second_seat.paths` now, rather than shipping two lists and merging later?
