---

id: LL0026
title: A model's fit against the data it was fitted to is not validation, and a forecast re-derived at judgement time is not a prediction
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A calibration loop that recomputes its own past forecasts from the current constants cannot be falsified. Change the constants and every past sprint is retroactively deemed to have predicted something else, so the accuracy ratio always drifts toward 1.0x and the history stops being evidence. Seen here: a 5.2x miss, the entire evidence that drove a recalibration, re-read as 1.57x once the recalibration landed - the error erased by the fix it caused. Record the forecast when it is MADE and judge it against that number. Corollary, and the more common trap: reporting a model's fit against the same data it was fitted to is TRAINING ERROR, not validation. It lands near 1.0x by construction. Here the in-sample fit read 1.09x while the out-of-sample fit on the very next sprint read 0.55x, and the planner was quoting the 1.09x back to the operator as evidence the estimator worked. The number that reassures is the one that cannot be wrong.

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
