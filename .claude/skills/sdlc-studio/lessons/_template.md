<!--
Template: Cross-project lesson learned
File: lessons/LL{NNNN}-{slug}.md  (lives IN THE SKILL – shared across all projects)
A lesson here is GENERALISABLE engineering/process wisdom that improves decisions
on ANY sdlc-studio project. Project-specific facts belong in that project's memory,
NOT here. Promote a project lesson here only once it clearly generalises.
Keep it tight – a lesson the next decision doesn't read is wasted.

TWO SHAPES. Most lessons are the short engineering/process form: the rule, what it
cost, how to apply it. An OPERATIONAL lesson – deploy, incident, disaster recovery –
is heavier, and that is correct: it is the category with the most expensive failures,
and a team that cannot record it here will record it somewhere the tooling cannot read.
It carries an incident narrative, a runbook you can tick, and citations. Use the
`Runbook` and `Incident` sections below only when the lesson is operational; delete
them otherwise.
-->
---

id: LL{NNNN}
title: {{short title}}
tags: [{{e.g. reconcile, schema, deploy, incident, dr, cross-repo, review}}]
added: {{date}}
origin: {{project + artifact that surfaced it, e.g. my-service RV0001}}
---

**Lesson.** {{the generalisable rule, one or two sentences}}

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
