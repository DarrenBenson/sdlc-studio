---

id: LL0017
title: A function that only ever appears inside patch() is untested, however many tests cover it
tags: [testing, mocking, coverage, false-green, bug-class]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** Two sprints running, the same shape shipped a HIGH bug: a brand-new function that talks to an external API, where EVERY reference to it in the test suite is a patch(...). Not one test called it.

Both times an independent critic deleted the single line that made the function work - a media-type header; a truncation flag - and the ENTIRE suite stayed green. Both times the consequence in production was severe (a re-sync loop that never terminates; mass deletion of documents).

The check is mechanical and takes ten seconds: grep the test suite for the symbol. If every hit is a mock, the function has no executable guard at all, and its coverage number is a lie about a different function.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
