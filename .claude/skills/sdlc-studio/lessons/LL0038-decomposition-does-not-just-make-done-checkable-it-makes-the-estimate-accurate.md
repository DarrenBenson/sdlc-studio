---

id: LL0038
title: Decomposition does not just make Done checkable - it makes the estimate accurate
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** Four large change requests were sized at filing by a single estimator in one shot: 5, 8, 5, 2 points. Delivered whole, they cost 0.56x of that forecast - every one under-forecast, and the tokens-per-point spread was a wide 2.3x, the fingerprint of bad sizing rather than a wrong rate.

Then two independent estimators, BLIND to the actual cost, decomposed the same four requests into stories and pointed each story. They agreed almost exactly (identical on 3 of 4, one point apart on the fourth), and their decomposed totals were 10, 11, 8, 6.5 - roughly 1.75x the single-shot points. Sum of decomposed points times the unchanged 25,000-per-point rate predicted the batch to 1.00x (887,500 vs 887,704 actual), and the mean tokens-per-point came to 25,404 against a 25,000 seed.

The whole under-forecast was under-SIZING, not a wrong rate. A big unit's own description hides its work; breaking it into the stories you would actually create surfaces that work and the size becomes honest. So the decompose-into-stories rule pays twice: only a story carries executable acceptance criteria (its Done is checkable, not asserted), AND a decomposed estimate is accurate where a whole-unit guess is not.

Method matters as much as scale. A single-estimator one-shot size read off an artefact is a weak input. A relative, decomposed, multi-estimator size - planning poker - is the one that predicts. It converges (independent estimators agree) and it is honest (nobody sees the outcome). N is small and these were LLM estimates, so re-check on real story telemetry - but the batch landing on 1.00x blind is not a coincidence a wrong model produces.

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
