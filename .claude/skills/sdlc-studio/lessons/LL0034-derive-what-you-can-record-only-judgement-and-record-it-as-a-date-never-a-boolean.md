---

id: LL0034
title: Derive what you can; record only judgement - and record it as a date, never a boolean
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** Three kinds of state, and each has exactly one honest representation.

DERIVED state must never be stamped. Whether a unit is groomed (does it declare the files it touches and a size?) is computable from the artefact, so compute it. A stamp creates a fact that can be true in the stamp and false in the file, and under a gate somebody will set the stamp to get past the gate.

JUDGEMENT cannot be derived, so it must be recorded - but a BOOLEAN is satisfiable by reflex. 'Triaged: yes' is the same defect as a gate that checks a file EXISTS rather than what is in it: it is satisfied by touch, and under pressure it becomes a tick nobody thought about.

Record judgement as a DATE, and derive its staleness from the world moving underneath it. A triage decision ('this is not a duplicate, it is still wanted') is a judgement made against a SNAPSHOT: it was true when it was made and says nothing about what was filed an hour later. So it does not expire after thirty days - it expires the moment something is filed that could invalidate it. A date can be compared against the world; a boolean cannot.

The test for any status field: can this be true in the record and false in reality? If yes, either derive it or give it a date that the world can falsify.

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
