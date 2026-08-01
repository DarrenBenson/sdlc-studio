---

id: LL0050
title: Name the mutant before writing the test, in its docstring
tags: [testing, mutation, evidence, vacuous-test, review]
added: 2026-08-01
origin: sdlc-studio
---

**Lesson.** Five reviews in one sprint returned REJECT and the production code was right in most of them. That distinction is the finding: it was an EVIDENCE problem, not a code-quality one, and the two need different remedies. The dominant class - about two thirds of every finding - was a test that passes identically whether the feature is present or absent.

EIGHT mechanisms produced one, named separately because each needs a different habit to catch:

1. Bypassing the surface under test - a hand-built `argparse.Namespace`, so a required-flag defect was invisible.
2. Asserting text the code under test supplies for free - a `def` line containing the call site's own string.
3. Using a fixture shape the product cannot produce.
4. Using a TYPE that lacks the state being tested.
5. Asserting an exception type where two different guards raise the same one.
6. Testing the helper rather than the caller - five times in one sprint, against a project whose own recorded scar says a library test is not a lane test.
7. Applying an assertion to a whole file, so an unrelated sentence satisfies it.
8. A positive control written against an input already in the passing state.

Every one is visible ON THE PAGE, before any mutation run, if the question is asked in the right order: state in the docstring the production change the test must fail on, then write the test to fail on it. If the mutant cannot be named, there is nothing to test yet.

Two smaller classes are structural and a design review does catch them, which is worth knowing because it is cheap: a guard placed in the library while the unguarded read stayed in the command, and a reader changed to require a key no writer emits. One question each - which surface does the user actually invoke, and who writes what I am reading. The honest limit is that such a review addresses those classes and cannot see a test that does not exist yet, so it is not a general cure.

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
