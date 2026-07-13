---

id: LL0013
title: An AC that enumerates the paths it checks silently exempts the path it forgot
tags: [acceptance-criteria, testing, false-green, bug-class]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** An acceptance criterion read 'every ADDED or UPDATED document is written with its blob_sha'. A SKIPPED document is neither - so the AC was fully satisfiable while the feature was broken end to end (every pre-existing row kept a NULL blob_sha for ever, so the feature could never engage for a single real install). 752 tests and four green ACs saw nothing.

State the INVARIANT ('every document ends up with a blob_sha'), never the list of paths you happened to think of. An AC phrased as an enumeration grants an exemption to every case outside it, and the case outside it is exactly the one nobody thought about.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
