---

id: LL0019
title: except Exception does not catch a cancellation - a lock released only there leaks on every shutdown
tags: [asyncio, python, shutdown, locks, bug-class]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** A background task took a DB lock by setting status='syncing', and released it in an  recovery block. asyncio.CancelledError is a BaseException, so a graceful shutdown - which is exactly what delivers a cancellation into an in-flight task - sailed straight past that handler. The status stayed 'syncing'. Nothing anywhere reset it, and the guard that reads it refused the project for ever.

The app shipped by container redeploy, so every deploy was a chance to permanently brick a project.

Two rules fall out. (1) Cleanup that releases a lock must catch BaseException and re-raise, or use try/finally. (2) A lock with no expiry and no reaper is a trap: any status that BLOCKS an operation needs an answer to 'what clears this if the holder never returns?' - and a SIGKILL runs no handler at all, so the answer has to live at startup.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
