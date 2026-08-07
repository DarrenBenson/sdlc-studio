---

id: LL0053
title: A registered mutant is a claim; clear the ledger and apply them before believing the count
tags: [mutation, evidence, false-green, self-report, bug-class]
added: 2026-08-07
origin: RUN-01KZEF9M, 2026-08-07
---

**Lesson.** Recording a mutant as killed is self-report, and the record is indistinguishable from a measured one once written. In RUN-01KZEF9M an eight-unit batch carried 61 registrations, written in batches as the criteria were authored rather than after each mutant was applied. Clearing all 61 and applying 47 for real took under ten minutes and turned up TWO SURVIVORS that the paperwork had recorded as kills.

Both survivors were the same shape - a test asserting on something the mutant does not decide. One asserted on a sentence composed in the same branch that sets the field the criterion is about, so clearing the field left the sentence standing; the other was a whole-section substring satisfied by words elsewhere in the same document.

Two practices follow. Register AFTER the last edit to a file, because a later edit silently drops every registration on the earlier content. And never register from intent: run a script that applies each mutant, runs the named test, restores from a saved copy, and registers ONLY on a genuine red. The difference between the two is exactly the difference this gate exists to enforce, and an author who skips it is asking a reviewer to discover it instead.

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
