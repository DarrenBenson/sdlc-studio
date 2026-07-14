---

id: LL0025
title: A narrow sample can make a variable look constant - widen the range before concluding
tags: [measurement, calibration, evidence, false-conclusion, bug-class, humility]
added: 2026-07-14
origin: BG0131 - a High bug filed on a conclusion drawn from a too-narrow sample
---

**Lesson.** Three units were measured and their token cost came out 42.7k, 46.4k and 46.8k - flat within 9 percent, while their wall-clock varied 240 percent. The conclusion drawn was that the metric did not track work at all, and a High bug was filed saying so. Two larger units then landed at 84k and 98k. The metric tracked work perfectly well. The three samples had simply all sat inside a narrow band of work volume (11-15 tool uses), where a large fixed cost dominates - so the variable component was invisible.

The failure is not 'too few samples'. It is **too narrow a RANGE**. Five samples clustered at one end of the input space tell you almost nothing about the slope; two samples at opposite ends tell you a great deal. Before concluding that a quantity is constant, ask: did I vary the input enough to have SEEN it change? If every sample sits in the same band, a flat output is the expected result whether the relationship is flat or not.

Rules:

1. **Vary the input deliberately before declaring a relationship.** Spread the samples across the range you care about. A conclusion drawn from one cluster is a conclusion about that cluster.
2. **A large fixed cost hides a variable one.** When a fixed overhead dominates, small inputs all produce nearly the same output. That is a property of the measurement, not of the world.
3. **State the range your conclusion covers.** 'Constant across 11-15 tool uses' is honest. 'Does not track work' is not.
4. **Slow down before filing at High severity on an inference.** A measurement that surprises you is more likely to be under-sampled than to be broken.

This is a sibling of [[LL0024]] (a hazard found by calling a private helper directly may already be guarded): both are the same underlying failure - a confident conclusion from evidence that did not actually test it. Three times in one day the same author drew a firm conclusion from insufficient evidence: a false High bug against an existing guard, a 5x calibration claim from N=1, and this. The tell is the same each time - the conclusion arrived quickly and felt satisfying.

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
