---

id: LL0031
title: Before tuning a coefficient, check that its input correlates with the target at all
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A cost model was recalibrated TWICE - the coefficient moved 5,000 then 600, each time fitted to a fresh sprint of measured actuals, each time failing on the next sprint (3.3x over, then 0.55x and 0.39x under). Both refits were wasted work, and worse than wasted: each produced a number that looked freshly evidence-based and was noise. Nobody had computed the one statistic that decides whether tuning is even the right operation. When it was finally computed, the input correlated with the target at r = -0.006 - and with the underlying quantity at r = -0.001. The predictor was INERT. No coefficient could ever have worked, because you cannot scale zero.

Recalibrating is the reflex when a model misses, and it is the wrong reflex when the model has the wrong INPUT. A miss tells you the output is wrong; it does not tell you whether the fault is the SCALE or the AXIS, and those need opposite fixes - one is a number, the other is a rewrite. The diagnostic is cheap and it is one line: correlate the predictor against the outcome you already measured. High r and a bad ratio means recalibrate. Low r means stop tuning and change what you are measuring.

Corollary, and the thing that made this expensive: a fitted coefficient always LOOKS calibrated, because it was fitted. In-sample it will hug 1.0x whatever the axis is worth. The fit is not the check.

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
