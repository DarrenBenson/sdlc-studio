# CLAUDE.md

This project uses the `sdlc-studio` skill for this task, with **model-tier routing
enabled** (`sdlc-studio/.config.yaml`). Use the skill to drive the work: create/derive the
minimal relevant specification, plan, implement, verify, and reconcile, scaled to the size
of the ticket in `TICKET.md` (a small ticket does not need a full PRD - use your judgement
on how much of the pipeline a task this size actually warrants, the way the skill's own
doctrine intends). Run `/sdlc-studio help` if unsure how to invoke it.

When you delegate implementation work to sub-agents, consult the routing recommendation
(`python3 .claude/skills/sdlc-studio/scripts/route.py pick --unit <artifact>` - or the
`tier`/`model` fields in a sprint plan) and spawn each delivery worker on the recommended
model tier. Record which tiers actually delivered the work in your final report (e.g.
"tiny:1, medium:2"). If you do the work directly rather than delegating, say so - that is
a legitimate scale-to-size call, not a failure.

Do not skip verification: run the resulting tests before declaring the task done.
