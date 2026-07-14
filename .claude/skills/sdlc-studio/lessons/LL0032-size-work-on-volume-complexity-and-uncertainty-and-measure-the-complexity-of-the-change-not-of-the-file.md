---

id: LL0032
title: Size work on volume, complexity and uncertainty - and measure the complexity of the CHANGE, not of the file
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A cost model built on ONE factor, measured on the wrong object, predicted nothing (r = 0.00 across 16 units). Established story-point practice sizes work on THREE dimensions - the amount of work, the complexity of the work, and the risk/uncertainty in it - and the estimator had only the middle one. Worse, it measured the complexity of the FILE a unit touches rather than of the CHANGE it makes, so a one-line fix in a 2,000-line module scored maximum complexity and did nothing. Measure the delta, not the container.

The signals that carry work rather than code: SIZE OF CHANGE and TEST IMPACT (how many tests must be written or rewritten - close to the definition of blast radius, and mechanically derivable), and CLARITY OF REQUIREMENT (a well-specified unit is fast whatever its size; a vague one is unbounded).

And know the ceiling before chasing it. The empirical literature finds the correlation between human-expert story points and actual effort is medium or LOW in 93% of projects, and that estimator consistency collapses above about 5 points. Per-unit effort prediction is a problem the field has not solved in twenty years, so a per-unit estimate should never set the tone of a plan. What works is RELATIVE sizing plus MEASURED VELOCITY - and the corollary is that a unit too big to size is a planning failure, not an estimation failure: break it down rather than guessing harder.

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
