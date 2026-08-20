---

id: LL0054
title: A test and its mutant authored together share one mental model, so they agree with each other and not with the code
tags: [testing, mutation, false-green, evidence, bug-class]
added: 2026-08-19
origin: RUN-01M0CT8P
---

**Lesson.** The commonest way evidence goes false here is not carelessness. It is ORDER. Writing the test first and then choosing a mutant that kills it produces two artefacts derived from the same picture of the code: if the picture is wrong, they still agree, the mutation run reports KILLED, and nothing has been measured.

Measured on RUN-01M0CT8P: a mutant applied to a CALL SITE died against a test that never exercised the function behind it, so a criterion was recorded delivered while its function still returned the wrong value. A test asserted a substring the message happened to contain elsewhere. A fixture rebuilt the production construction in a private helper, so deleting the entire production change left 916 tests green. Eight of 34 rows recorded as killed did not die on the test their own criterion named.

**Apply the mutant FIRST, against the unmodified tree, and confirm the named test is red before writing a line of it.** The mutant then comes from the CRITERION - the behaviour that must not be allowed to regress - rather than from the test, and the test is written to catch something that has already been observed failing. `best-practices/testing.md` says name the mutant first; this is why, and nothing enforces it.

The paired CONTROL is the other half. Every assertion that a thing works needs its twin: the same call, in the state where it must NOT work. Four successive cuts of one test here passed against a row that had never reached the code under test - `no base ref`, then `no git history here`, then `no ticked criteria found` - and the control caught all three, because it asserted the row must DECLINE without the fix. An assertion about success alone cannot tell a working mechanism from one that never ran.

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
