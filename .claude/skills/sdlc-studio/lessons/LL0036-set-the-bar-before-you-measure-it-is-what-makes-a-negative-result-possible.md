---

id: LL0036
title: Set the bar before you measure - it is what makes a negative result possible
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A model was replaced only because the bar was written down BEFORE the data was looked at: leave-one-out r >= 0.50, must beat the single best raw signal, ratio within 0.5x-2.0x for most units. Nothing cleared it. The best composite reached 0.415 - and even that was flattered, because its coefficients were refitted inside every fold and its features chosen with hindsight. So the per-unit forecast was DROPPED rather than replaced with a mediocre one.

Without a bar set in advance, 0.415 is a success story: it is three times better than what it replaced, and the temptation to ship it is enormous. With a bar, it is a failure, and the honest move is to stop predicting and start counting. 'No predictor exists' is a RESULT, and a tool that says so is more use than one that quotes a number it has never tested.

The corollary: counting is not a worse estimator than modelling. It is the honest one when no signal exists - and here the forecast that gave up on prediction outperformed everything built to predict.

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
