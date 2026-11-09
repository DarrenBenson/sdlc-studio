# Maya Okafor

> A specific person, not a type. The Secondary is served fully, but never at the Primary's expense.

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Secondary |
| **Role** | Solo founder-engineer building a SaaS product |
| **Context** | Works in a terminal with an AI coding agent; long sessions, frequent context resets |

## Who They Are

Maya is a former senior engineer who left to build her own product. She writes the code and owns
every decision, with an AI coding agent as her pair. She has shipped enough to distrust
"vibe-coding": she has watched an agent confidently rewrite the wrong thing, lose the thread after
a context reset, and leave the docs lying about what the code does. She wants the agent on rails -
a real lifecycle she can trust to run without her watching every step.

## End Goals

*What they are trying to accomplish, most important first. The design is judged against these.*

1. Ship real features through a disciplined lifecycle (spec -> story -> implement -> verify), not ad-hoc edits
2. Never lose the thread - know the true state of the work after any session, reset, or compaction
3. Drive a whole batch of work to "done" autonomously, pausing only when a decision is genuinely hers
4. Keep specs, code, and tests in sync so the documentation never quietly drifts from reality
5. Keep the process small enough to serve the work - every check earns its keep, and one that catches nothing is retired

## Experience Goals

*How they want to feel while using it.*

- In control - she sets the goal and the guardrails; the agent does not surprise her
- Able to trust the loop enough to step away and come back to honest, green progress
- Unburdened by ceremony - the process earns its keep, it does not become the work

## Behaviours & Context

- **Environment:** a terminal and an agent (Claude Code); a single repo she owns end to end
- **Frequency:** daily, in long working sessions that often outlast a single context window
- **Proficiency:** strong engineer, fluent on the CLI; new to running a *formal* lifecycle and happy to let the tool hold that discipline
- **Gate:** `/sdlc-studio gate` in her own repository, which states a run's cost against a
  declared budget and names the lane that dominated it

## Frustrations

*What trips them up with the current tools or status quo.*

- Agents that vibe-code: plausible output, wrong target, no trace of what changed or why
- Status that goes stale the moment she looks away - she cannot tell what is really done
- Heavyweight process tools built for big teams: forms, boards, and ceremony she has no time for
- A sprint that ships but cannot say what it cost - tokens burned, estimate held or blown - so
  she cannot tell whether the process is earning its keep or quietly eating her budget

## Scenario

*A short narrative of this persona using the product to reach an End goal.*

Maya has a backlog of accepted change requests and a free afternoon. She runs
`/sdlc-studio sprint --crs Proposed --goal done`, approves the triage plan it shows her, then steps
away. The loop drives each unit - decompose, test, verify, an independent review, a green commit -
and pauses once to ask a real scoping question. She comes back to a reconcile showing zero drift
and the sprint report the close filed: what shipped, what it actually cost (rework included,
priced from her own rates), and whether the estimate held. She reads it and signs the run once,
with `sprint.py sign`, which moves the batch to its terminal statuses. Nothing drifted; nothing
surprised her.

## Boundaries

- **[Abena Osei](abena-osei-head-of-engineering.md) is Primary for the shipped skill**, the
  interface Maya uses (D0436). Maya is served fully, but never at Abena's expense. She is less well
  served on her End goal 3, driving a whole batch to done autonomously, because owner fields,
  evidence packs and budget views add process a solo builder did not ask for (D0443 narrowed D0436's
  list to that one goal).
- **[Rowan Achterberg](rowan-achterberg-skill-maintainer.md) is Primary for this repository's own
  tooling**, which does not ship and which Maya never sees. His want is met there, never by adding
  a step to her run.
- A unit is judged against the Primary of the interface its Affects touch. A unit touching both
  touches a shipped path, so it is Abena's; a story minted with no `--persona` names her too, as the
  Primary the persona index lists first.

| A unit touching | Is judged against |
| --- | --- |
| The shipped skill | Abena Osei |
| Repository tooling | Rowan Achterberg |
| Both interfaces | Abena Osei |

---

- **Primary:** see `abena-osei-head-of-engineering.md` - Maya is served, but never at Abena's expense.
- **Negative persona:** see `trevor-hale-enterprise-pm.md` - who we are deliberately not designing for.
- **Customer / Served:** for Maya, the buyer and the user are the same person; no separate Customer persona is needed.
