---

id: LL0030
title: A plausible story fitted to a real pattern is not a finding - test it against the data already on disk
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A forecasting model missed badly on consecutive sprints. The explanation recorded at the time was that the standard of work had risen beneath it - a story that fitted every observation and was WRONG. One correlation, computable from telemetry already sitting on disk, refuted it: the cost per action was flat across all three sprints, so nothing about the work had changed. The real cause was that the predictor itself was inert (r = 0.00 against both cost and work), which no amount of recalibration could fix. The trap is specific and seductive: a narrative that explains the data feels like a diagnosis, and it survives because nobody asks what number would prove it false. Before recording WHY something failed, ask what measurement would refute the explanation, then check whether that measurement is already in reach. It usually is.

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
