---

id: LL0046
title: The antidote's own author vibe-coded: check the contract BEFORE acting, not after the gate refuses
tags: [process, discipline]
added: 2026-07-22
origin: RUN-01KY3MFX
---

**Lesson.** This skill's description is 'the antidote to vibe coding'. In RUN-01KY3MFX its author vibe-coded repeatedly, and every instance has one shape: ACTING BEFORE ESTABLISHING THE CONTRACT. Ten repair rounds were written by reading a finding and immediately editing - no plan, no review of the approach, no goal of passing - and every round from 3 to 10 found a defect the previous repair created. A reference path was written from memory with the wrong prefix SIX times, twice inside artefacts about that very defect. A CHANGELOG block was inserted without reading the section structure, orphaning the existing bullets under a new heading. A retro Batch field was written as an id RANGE without checking the parser's contract, publishing a velocity row wrong by three orders of magnitude. `verify_ac` was run over the whole workspace for nine minutes without checking whether a scoped form existed. A `-k` selector printing NO TESTS RAN was nearly read as a pass. In every case the answer was one command away and the cost was paid later at a much higher price. AGENTS.md already says it: read the scripts catalogue BEFORE hand-doing a mechanical task. The failure was not ignorance of the rule - the rule had just been written down, and once was re-broken minutes after being ruled on in a decision of record. Speed felt free and was not.

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
