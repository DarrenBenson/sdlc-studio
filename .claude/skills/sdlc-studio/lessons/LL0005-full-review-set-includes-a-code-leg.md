---
id: LL0005
title: The between-releases review set must include a CODE leg
tags: [review, release, quality]
added: 2026-06-03
origin: a between-releases review sweep that caught a crash, a deploy gap, and a silent-arg bug
---

**Lesson.** Between releases (or a train of them), run the FULL review set — PRD · TRD · TSD · Persona · **CODE** — ideally fanned out as parallel review subagents, then triage + FIX before new feature work. Mechanical reconcile and doc-only review will **never** find a crash bug, a deploy gap, or an untested hot path.

**Why / what it cost.** A doc-only close-out once passed clean while a real uncaught-EPIPE crash (would have killed every agent), a deploy-rsync gap (fresh box missing scripts), and a silent empty-arg bug sat in the code — all caught only by an explicit CODE leg.

**How to apply.** Each leg = one subagent reading in its own context, returning `[severity · location · problem · concrete fix]`. CODE leg is non-negotiable; HIGH/MED code findings are release-blocking (file them as bugs with `Verify:` lines).

**Generalises to.** Any project that ships frequently and relies on spec/doc review for quality.
