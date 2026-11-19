---

id: LL0057
title: Give every subagent a persona: a seated agent beats a generic one
tags: [subagents, personas, review, delegation]
added: 2026-11-19
origin: sdlc-studio D0547
---

**Lesson.** Every subagent an orchestrator spawns, whether it builds, reviews, triages, researches or plans, is briefed with a persona seat card, never as a generic worker. The seat that fits the work frames how the agent weighs evidence and where it pushes back; it never overrides the brief's rules or the acceptance criteria.

**Why / what it cost.** The operator's ruling on sdlc-studio (D0547), made after the orchestrator spawned a release bug triage with a plain task brief. The skill already seated its builders (the engineering seat's work render in the lane brief) and its reviewers (the seat charter `critic.py brief` carries), but every other agent an orchestrator spawned (triage, research, planning, audit finders) got the task and none of the judgement: no stance on what counts as evidence, when to push back, or what its own blind spot is. How much the seat shapes what an agent finds shows in review: on one run a second, differently seated reviewer rejected five of nine high-risk units, and six of its blocking defects were ones the first seat had passed.

**How to apply.** Before spawning any subagent, pick the seat whose lens fits the work (qa for triage and verification, engineering for building and design, product for scope and value) and put its render in the brief: `persona_resolve.py resolve --seat <role> --render build` for an agent that makes something, `--render review` for one that judges. The seat frames the judgement; the brief's rules and the acceptance criteria still govern. A brief with no seat is a defect in the brief, and one agent never holds the build and the review render on the same unit.

**Generalises to.** Any delegation to a model agent: builders, reviewers, triage and audit sweeps, research, planning, goal review, consults and every other fan-out of agents.

**Guard.** None yet: CR0748 asks every brief the skill ships to name a seat and refuse one that does not.
