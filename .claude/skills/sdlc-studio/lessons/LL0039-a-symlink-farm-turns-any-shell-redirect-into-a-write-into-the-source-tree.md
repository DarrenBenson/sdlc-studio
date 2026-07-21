---

id: LL0039
title: A symlink farm turns any shell redirect into a write into the source tree
tags: [safety, tooling, review]
added: 2026-07-21
origin: RUN-01KY321Q closing review
---

**Lesson.** Building a throwaway working directory with `ln -sf <src>/*.py .` and then redirecting onto one of those names - `git show <rev>:<path> > file.py`, or any `> file`, `tee`, or `cp` - follows the symlink and OVERWRITES THE SOURCE. In RUN-01KY321Q's closing review this silently reverted two delivered units in the live working tree; it was caught by `git status`, restored from HEAD and disclosed, but nothing about the command looked dangerous and the directory had been built specifically to keep work away from the live tree. This is the L-0158 class arriving by a new route: the isolation was believed rather than verified. Copy the files instead of linking them when anything will be written, or link into a directory you only ever READ from. If a sandbox is meant to be isolated, prove it: write a probe through the intended path and confirm the source is unchanged BEFORE doing the work that matters. Related failure from the same incident: three diagnoses were announced from a `git diff` before the state was established, and the first was closest - a diff taken while another process is mid-edit describes a moment, not a fact.

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
