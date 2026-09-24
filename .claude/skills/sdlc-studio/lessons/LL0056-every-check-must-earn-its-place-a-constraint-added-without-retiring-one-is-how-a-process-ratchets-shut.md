---

id: LL0056
title: Every check must earn its place: a constraint added without retiring one is how a process ratchets shut
tags: [process, gates, ratchet, lean]
added: 2026-09-24
origin: sdlc-studio
---

**Lesson.** **Lesson.** A process that turns each failure into a lesson and each lesson into a gate, and never removes a gate, ratchets: the refusals generate defects in the machinery, those defects become the next sprint, and the work becomes the process. This is the counterweight to LL0027: put a check that matters in the command people run, and prove it matters by its yield. A new check, refusal, baseline, ratchet or hand-maintained pin names the measured yield that justifies it or the constraint it retires. A derived fact is generated, never pinned by hand. Before adding a check, fix the code path that failed.

**Why / what it cost.** On sdlc-studio, 82% of 116 sprint units built or repaired the sprint, review and gate machinery; a bug fix carried about eight evidence obligations; close attempts per run grew from 1 to 13. Two lean sprints then deleted gates wholesale: 242 of 255 plan-review rejections argued over test apparatus rather than code, 636 of 637 depth tiers read the same value, and in one sprint the warning ratchet, verify ratchet, release-notes count pins and filer refusals each cost commit cycles without catching a code defect.

**How to apply.** When proposing any check, state its expected yield and what it retires. Record whether each refusal caught a real defect, and flag a lane with no yield for deletion. When a failure repeats, prefer fixing the path over adding a check; a lesson that graduates names the check it would replace. Re-triage the backlog against the current direction before each plan.

**Generalises to.** Any process, CI pipeline or review regime that learns from failures: quality gates, lint rules, approval steps, compliance checklists.

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
