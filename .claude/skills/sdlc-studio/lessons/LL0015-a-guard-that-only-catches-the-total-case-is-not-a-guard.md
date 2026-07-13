---

id: LL0015
title: A guard that only catches the total case is not a guard
tags: [defence, data-loss, bug-class, review]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** A sync engine had a guard: 'source returned no documents - refusing to delete existing documents'. It fires when the incoming manifest is COMPLETELY empty, and it duly fixed the High-severity bug it was written for.

Every PARTIAL failure walked straight past it. One unreadable file was dropped from the manifest, the deletion loop read absence as 'deleted upstream', and the document was destroyed while the file sat intact on disk - with the sync reporting success.

When you write a defence against 'the source went wrong', ask what the 1% version of that same failure does. The total case feels like the dangerous one; the partial case is both likelier and quieter.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
