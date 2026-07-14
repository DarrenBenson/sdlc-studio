---

id: LL0035
title: A signal that flips sign between cohorts is not a predictor, whatever its pooled correlation says
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A candidate predictor scored r = +0.45 pooled across three sprints and was recommended on that basis. Split by sprint it runs +0.72, -0.34, +0.87. It REVERSES DIRECTION. The pooled figure was a between-cohort artefact: later sprints touched more files AND cost more, for unrelated reasons, and the correlation was measuring that coincidence rather than any causal link.

The sibling trap, from the same data: scoring a MISSING value as zero turns 'when this field was invented' into a predictor. The mere PRESENCE of an Effort field scored r = +0.43 against cost - because the field only existed on later, larger units. The calendar will happily correlate with anything that grew over time.

Before trusting an average ACROSS groups, compute it WITHIN each group. If the sign flips, or if the signal is really 'which cohort is this', there is no predictor there - only a coincidence that a pooled statistic is too coarse to see.

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
