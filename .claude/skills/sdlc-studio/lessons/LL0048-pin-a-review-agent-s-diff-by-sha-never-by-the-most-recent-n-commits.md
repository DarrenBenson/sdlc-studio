---

id: LL0048
title: Pin a review agent's diff by sha, never by 'the most recent N commits'
tags: [review, agents, git, scoping]
added: 2026-07-27
origin: RUN-01KYHVWK closing review, 2026-07-27: operator asked what the diff was and exposed a floating reference in the reviewer brief.
---

**Lesson.** A review brief that scopes the work as 'the two most recent commits' is a floating reference evaluated when the agent runs, not when the brief was written. Any commit landing in between silently shifts the window, and the work under review slides out of it while the agent reports confidently on what remains. There is no error: the agent reads a valid diff, just not the one it was asked to judge.

Caught on RUN-01KYHVWK before it bit, and only because the operator asked what the diff actually was. Three reviewers were running against 'the two most recent commits' while the review record they would feed was sitting uncommitted; committing it would have pushed the 104-file delivery commit out of their window entirely.

The rule: resolve the range to explicit shas BEFORE launching, and put the literal range in the brief (`git show <sha>` or `git diff <base>..<head>`). Then a commit landing mid-review changes nothing about what is judged. The same applies to any agent instruction naming HEAD, 'latest', 'current' or a branch tip: the agent evaluates it later than you wrote it. If the range cannot be pinned, do not commit while the review runs - but pinning is the fix and abstaining is only the workaround.

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
