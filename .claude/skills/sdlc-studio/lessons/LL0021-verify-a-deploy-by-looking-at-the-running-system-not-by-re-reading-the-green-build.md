---

id: LL0021
title: Verify a deploy by looking at the running system, not by re-reading the green build
tags: [deploy, verification, observability, process]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** A release passed 824 unit tests, a full E2E suite, lint, type-checks and a mutation pass. It deployed cleanly, migrations ran, and /health returned ready:true with the right version. Every gate was green.

Then somebody opened  and noticed one line that should have been there was missing - the background poller's startup message. That thread unravelled a High-severity bug: NO application log line had ever reached stdout, in any environment, ever.

No test could have caught it, because the test fixture supplied the missing machinery (see the caplog lesson). The health endpoint could not catch it, because the app was genuinely healthy - just mute.

So the last step of a deploy is not 'the gate is green'. It is: go and LOOK at the running system, and check that the things you believe should be true are observably true. Read the logs. Trigger the feature. Watch it do the thing. The gap between 'all checks passed' and 'it works' is exactly where the interesting bugs live.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
