---

id: LL0055
title: Rehearse the seal before asking anyone to sign, and file-and-defer whatever it surfaces
tags: [sprint, close, signoff, report, gating, verification]
added: 2026-09-20
origin: sdlc-studio
---

**Lesson.** The signature is the only step that re-running something cannot undo, and it is usually the only step nobody has rehearsed. Before handing an operator `sprint sign`, run the WHOLE act on a throwaway copy of the run - close, sign, then check - and only then ask.

RUN-01M2SPNS signed a report that was correct, gate-clear and VALID, and `check` reported it INVALIDATED one second later: the seal writes `ended_at`, the DORA window was bounded by it, so signing widened the window and moved the very figures the signature had just frozen. No run could ever have held a valid signature over its own report. Nine units, two review rounds and 33 passing criteria missed it, because every fixture wrote a signature block WITHOUT ending the run - the one state the real seal always produces. Fixtures agree with each other; only the shipped command disagrees with them.

The general rule: for any irreversible act, the state it CREATES is the state no test has. Build the fixture that reaches it, or rehearse the act itself.

The second half is a discipline, not a check. Once the operator has signed, anything the seal surfaces is FILED AND DEFERRED, never repaired in flight. The same run filed and deferred two findings correctly and then repaired the third in place; that pulled in two review rounds, a repair that twice relocated the defect rather than removing it, and an escalation the operator should never have been shown. The close's fixed point is what makes a close mean anything, and it is worth more than the finding you happen to be looking at.

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
