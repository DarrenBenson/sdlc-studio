---
id: LL0011
title: A gate that fails on CI but passes locally is an environment gap until proven otherwise
tags: [ci, debugging, environment, fail-loud]
added: 2026-06-27
origin: sdlc-studio
---

**Lesson.** When a check is red on CI but green locally, reproduce the CI environment (shadow the missing module, strip the absent tool) before trusting the stated symptom. EP0010's coverage gate was reported as 'coverage below 80% from skipped suites'; reproducing the no-PyYAML runner showed the real cause was 8 test failures + 2 errors (config tests that raise without PyYAML), which made coverage run exit non-zero before the threshold was ever read. Coverage was a healthy 82%. Fix the cause, not the symptom.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
