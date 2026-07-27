---

id: LL0049
title: A long agent task with no output schema can stall silently - check the transcript's mtime, do not wait for a notification
tags: [agents, orchestration, reliability, review]
added: 2026-07-27
origin: RUN-01KYHVWK closing review, 2026-07-27: two bare review agents stalled silently; the schema-bearing workflow reviewers all completed.
---

**Lesson.** Two review agents launched as bare agent tasks stalled on this run: one at 841KB of transcript, one at 405KB, each then idle for 12 and 24 minutes with no result and no error. Nothing surfaced - no failure notification, no partial output. The work simply never arrived, and waiting on a completion signal that will never come is indistinguishable from waiting on a slow agent.

The correlation is stark and worth acting on before it is fully explained: on the same session, 20-plus agents run inside workflows - each forced to finish through a structured-output tool call - all completed, while both bare agents with free-form final text stalled. The plausible mechanism is that a schema gives the agent a terminating action, where free-form completion after a very long tool-use sequence has no such anchor. Treat that as a working hypothesis rather than a proven cause; treat the observation itself as reliable.

Two practical rules. Run any long or wide agent task through a workflow with an output schema, which also gets you typed results instead of prose to parse. And detect the stall by looking: the transcript file's size and modification time say whether an agent is thinking or dead, and a result marker says whether it finished. An absent verdict read as a pending one is the same failure as the audit's dead-vote problem, one layer down.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}

<!-- Optional. A lesson is DEMOTED in the ranking once a shipped test or gate makes its
class mechanically impossible: it has done its job, and must not crowd out one that can
still bite you. Demoted, never deleted – the history is why the guard exists. Name the
guard and the ranking stops shouting about it. -->

**Guard.** {{the test or gate that now makes this class impossible, e.g. tests/test_x.py}}

<!-- ===== OPERATIONAL LESSONS ONLY (deploy / incident / DR) – delete if not applicable =====
Real operational lessons are narrative, not aphorism: what actually happened, in order,
and what to DO at 3am. A one-line rule does not survive contact with an outage.
-->

**Incident.**

{{What happened, in order. The trigger, what looked fine and wasn't, and the moment it
became visible. Dates and artefact ids (CR/BG/RFC). Say what MISLED you – the thing that
looked healthy is usually the lesson.}}

**Runbook.**

{{The tickable procedure. Written to be followed under pressure by someone who did not
witness the incident.}}

- [ ] {{step – be specific about what "done" looks like}}
- [ ] {{step}}
- [ ] {{the go/no-go check – how you KNOW it worked, from the running system and not from
      a green build}}

**Decay.**

{{Operational detail rots faster than the rule does. State what to re-verify before
trusting this: file:line citations are point-in-time, hostnames change, a flag gets
renamed. Say what is durable and what is a snapshot.}}
