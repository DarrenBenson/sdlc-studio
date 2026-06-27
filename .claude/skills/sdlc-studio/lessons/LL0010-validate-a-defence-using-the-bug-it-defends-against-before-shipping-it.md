---
id: LL0010
title: Validate a defence using the bug it defends against, before shipping it
tags: [quality-gate, defence, testing, process, bug-class]
added: 2026-06-27
origin: a second consuming repo L-RV-L2-007 (v1.2.2)
---

**Lesson.** **Lesson.** A self-prevention feature (a quality gate, guard, or validator) must be exercised against the exact failure mode it is meant to catch before it ships - otherwise it can pass review yet be broken on its first real encounter with that failure.

**Why / what it cost.** a second consuming repo v1.2.2 added a Phase A2 env-var diff check to defend against a missing-env-var deploy failure. On its first run it aborted - not because the env var was missing, but because the check's own shell quoting was broken. The defence had never been run against a known-missing-env-var state, so its own bug shipped undetected.

**How to apply.** For any guard/gate/validator, write a one-off smoke run that reproduces the failure mode it defends against and assert the guard fires correctly. Treat "the defence is untested against its target failure" as not-done. Pairs with the retro/close-gate work and [[LL0008]].

**Generalises to.** Any defensive code: input validators, deploy gates, regression guards, assertions, circuit breakers - anything whose value is only realised when a specific bad state occurs.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
