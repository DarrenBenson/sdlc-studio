---

id: LL0033
title: A population average is not a ceiling, and a compulsory estimate is not an estimate
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** Two errors, one root. A large study found human story points correlate only medium-or-low with real effort in 93% of projects, and that finding was written up as 'roughly the industry ceiling' - a claim about what estimation CAN be, from evidence about what it TYPICALLY is. A population average hides its variance: 'most people are poor at this' has never implied 'nobody can be good at it'. Worse, the study cannot separate capability from ENGAGEMENT. An engineer does not want to estimate, they want to write code - so a survey of estimates in the wild measures, to an unknown degree, how much people could be bothered. Low effort and low ability produce an identical correlation.

Do not import a population statistic as a bound on the individual in front of you. If the loop records forecasts and actuals, it can measure THAT person's accuracy directly, and report it back to them - which is also the one intervention known to actually improve human estimation.

The corollary bites anything that makes an estimate MANDATORY. If sizing is a chore, a compulsory size produces a careless one, and a careless number is strictly worse than an absent one because it looks like data and gets averaged into a forecast. A gate that demands a number it never checks teaches people to supply a number that means nothing. Give 'unknown' a first-class value, and check the numbers you demand.

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
