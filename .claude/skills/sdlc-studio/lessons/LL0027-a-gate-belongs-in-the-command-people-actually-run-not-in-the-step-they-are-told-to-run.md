---

id: LL0027
title: A gate belongs in the command people actually run, not in the step they are told to run
tags: []
added: 2026-07-14
origin: sdlc-studio
---

**Lesson.** A separate grooming, design or review step that is documented but optional is doctrine, and doctrine decays. The design rung here was specified for months to produce a reviewable, estimated backlog and was never once invoked; the identical grooming rule, enforced inside the plan command, was unavoidable on day one and refused three artefacts within a minute of shipping. The same pattern appeared three times in one session: a retro gate satisfiable by touch, a review that was advisory so a stale one reached a close, and a breakdown step nobody ran. If a ceremony matters, put it in the path of the command that cannot be skipped, and make the escape a recorded decision rather than an omission - an absent config must BLOCK, not pass.

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
