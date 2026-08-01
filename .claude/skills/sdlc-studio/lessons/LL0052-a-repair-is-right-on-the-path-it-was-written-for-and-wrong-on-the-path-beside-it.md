---

id: LL0052
title: A repair is right on the path it was written for and wrong on the path beside it
tags: [testing, mutation, review, repair]
added: 2026-08-01
origin: sdlc-studio
---

**Lesson.** Observed twice independently in one sprint, by different seats, on different units.

Round 3 named it: *each repair is behaviourally right on the path it was written for, and silently wrong on the path where its helper is absent, broken, or never ran.* Three examples in one batch: an exit-code contract pinned in python and untested in the shell that consumes it; a preflight whose early returns never reach the gate, reported as a gate that passed; an exception handler falling through to the fail-OPEN direction while every other uncertainty path in the same function returned fail-closed.

Then again on the next unit: a fix to a two-half gate that repaired the signature half and left the evidence half unchecked, so the same silent-loss the bug was filed to end came back through its own repair.

The habit: when repairing a rule, enumerate every path the rule governs BEFORE writing the fix - the other half of the pair, the caller in another language, the branch where the helper is missing, the id form you do not use - and state which of them the fix covers. A repair scoped to the reproduction you were handed will pass its own test and leave the sibling path broken.

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
