---

id: LL0047
title: A verifier the staleness sweep cannot resolve is one whose test can vanish unnoticed
tags: [verification, acceptance-criteria, tooling, staleness]
added: 2026-07-27
origin: Round-one adversarial review of the discovery-backlog refine, 2026-07-27: all 21 acceptance criteria in one proposed group were authored as shell unittest invocations, caught by reading verify_ac.py rather than by running them.
---

**Lesson.** The executable-AC checker answers two different questions, and only one of them survives the choice of verb. Running a verifier tells you whether it passes NOW. Resolving its selector tells you whether it still points at anything at all. `verify_ac.selector_resolves()` decides that second question by COLLECTION, and collection is only attempted for verbs in `_COLLECTABLE`, which is `{"pytest"}`. Every other form - `shell`, `grep`, `manual` - returns None, meaning unanswerable, and unanswerable is correctly never reported as stale. So a `shell` verifier is permanently invisible to the sweep that exists to catch a rotted stamp.

That is not hypothetical. Four Done stories carried verifiers naming a test file a later rename had deleted; the stamps read `Verified: yes`, drift detection reported zero, and nothing noticed until an adversarial audit read the files by hand. A `shell python3 -m unittest ...` line and a `pytest path::Class::test` line can run the identical test today and differ completely in whether their rot is detectable tomorrow.

The rule: prefer a collectable node id for any verifier that can be expressed as one, and reach for `shell` only when no node id could express the check - then say in the criterion why, so a reader knows the staleness sweep is blind there by choice rather than by accident. Before adopting a verifier form across a batch of new work, check which questions the tooling can still ask about it. A batch authored in an unanswerable form buys a whole tranche of undetectable rot at once.

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
