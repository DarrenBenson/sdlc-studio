# RFC-0032: Close the learning loop: retros and lessons must drive review, audit and the backlog

> **Status:** Draft
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

SDLC Studio records what it learns and then does not read it back. The registry holds 21 cross-project lessons and the workspace holds 23 retros, and the write side is well gated (gate.py blocks a sprint close without its retro, recomputes the lessons summary, and enforces the Review-by horizon). But only ONE consumer reads any of it: sprint plan injects the still-valid lessons digest into the plan. Review does not read lessons. Audit does not read lessons. And no retro finding has ever become a Bug or a CR - `file_finding.py` is wired to review and never to retro, so a retro finding is prose that nothing acts on. The gate checks the retro FILE exists, not that a single thing in it was dispositioned. BG0122 is the proof: install.sh exited 0 having done nothing, which is precisely LL0008 (a deterministic tool must fail loud, never report success it did not achieve) and LL0009 (silent misleading failure outranks loud failure), and the test gap is precisely LL0020. The lesson that predicted the bug was already written. Nothing in the process made anyone read it. Ten lessons already carry a bug-class tag - a ready-made review checklist that nothing loads. This is the inspect-and-adapt cycle that agile retrospectives exist to create: we built inspect and skipped adapt. It must hold for every consuming project, not just this repo.

## Design Options

- **Advisory recall: review and audit load bug-class lessons as lenses; findings are the agent's to weigh. Cheap, no new gate, but a lens that can be ignored tends to be.**
- **Gated disposition: every retro finding must be filed as a Bug/CR or explicitly declined with a reason, enforced by a new gate leg. Teeth, matching the repo's fail-loud doctrine, but it can block a close on judgement calls.**
- **Both, staged: recall first (read side, no teeth), disposition second (write side, with teeth) once the recall lens has proved its worth in practice.**

## Recommendation

Both, staged - but the open decisions are the operator's: whether the disposition gate BLOCKS or warns; how many lessons are injected and at what token cost (the plan digest already caps at 20); whether recall filters on the bug-class tag or the full set; and how a consuming project with an empty registry bootstraps without the loop feeling like dead ceremony.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Does the retro-finding disposition gate **block** a sprint close, or only warn? Blocking matches the repo's fail-loud doctrine and is the only thing that stops a finding rotting in prose; but a finding can be a judgement call, and a gate that blocks on judgement invites the agent to file noise to get green. | Open |
| D2 | Does `review`/`audit` recall the **`bug-class`-tagged** lessons only (10 today, a tight checklist) or the **full set** (22 and growing)? The tag already exists; the full set is more complete but costs tokens on every review and dilutes the lens. | Open |
| D3 | What is the **token budget** for injected lessons, and what happens when the registry outgrows it? `sprint plan` already caps its digest at 20 (`PLAN_DIGEST_MAX`) and elides the tail. Recall needs the same answer, and "elide the tail" silently drops the oldest lessons - which may be the load-bearing ones. | Open |
| D4 | How does a **consuming project with an empty registry** bootstrap? Day one it has no lessons and no retros, so every recall is empty and every disposition gate is vacuous. Does it inherit the skill-tier lessons as a starting lens, and does the loop stay silent until it has something to say, so it never reads as dead ceremony? | Open |
| D5 | Is the loop **doctrine or opt-in**? The engagement floor (v4) was mandated on measured evidence that judgement-gated process is skipped. The same argument applies here - but it is a claim we should measure, not assume. | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
