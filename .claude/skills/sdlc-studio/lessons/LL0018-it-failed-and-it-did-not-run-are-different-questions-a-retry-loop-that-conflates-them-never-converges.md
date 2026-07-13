---

id: LL0018
title: 'It failed' and 'it did not run' are different questions; a retry loop that conflates them never converges
tags: [retry, idempotence, status, bug-class, convergence]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** A sync set status='error' whenever ANY file failed - correct, it had not fully succeeded. A poller advanced its watermark only on status='synced'. So a repo with one permanently-undecodable file could never advance: it re-synced on every tick, for ever, and never converged, while sitting permanently at 'error'.

The status field answered 'was everything perfect?'. The retry loop needed 'is a retry worth anything?'. They are not the same question, and a single field cannot serve both.

If a caller decides whether to RETRY based on a status, that status must distinguish 'the work did not happen' (retry is meaningful) from 'the work happened and this is as good as it gets' (retry is an infinite loop). Give the caller an explicit completed/ran flag rather than making it infer intent from a health field.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
