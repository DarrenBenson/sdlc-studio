---

id: LL0037
title: A relative Fibonacci estimate predicts cost; a computed metric does not
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** Two days were spent building an absolute cost model from code metrics. The seed scored r = 0.03 against measured cost and the forecast was dropped. A blind experiment then took the SAME 21 units, recovered each as originally filed, stripped the existing size field, and asked three independent estimators to size them in modified Fibonacci points RELATIVE TO EACH OTHER, with no access to outcomes.

Points scored r = 0.68 pooled, and 0.78 on units of 8 or below. They stayed POSITIVE within every sprint, where the best computed signal had flipped sign between cohorts. Twelve of nineteen units landed within 0.75x-1.25x on a flat 25,000-tokens-per-point rate with no fitting at all - against an old estimator that missed every single unit, monotonically. The three estimators agreed exactly on 14 of 21.

Why it works, and why the computed metric could not: a metric measures the CONTAINER (how complicated is this file), while a relative estimate measures the JOB (is this bigger than that one) - and it integrates complexity, uncertainty and effort in a way no single number derived from the code can.

And the scale knows its own limits. A point was a stable unit of cost from 2 to 8 (22k-27k tokens per point) and then broke: the 13s came in at 14k per point, systematically over-estimated - exactly where the literature says estimator consistency collapses. All three estimators flagged them LOW confidence and 'should be split', unprompted. So the rule is not a ceremony bolted on: ANYTHING ABOVE 8 POINTS MUST BE SPLIT, because that is the range in which the estimate is worth having.

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
