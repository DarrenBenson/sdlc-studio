---
id: LL0004
title: Ship the paperwork in the same commit as the code
tags: [process, docs, release, drift]
added: 2026-06-03
origin: per-ship discipline
---

**Lesson.** When a feature ships, update its structured contract (spec feature-inventory row + detail, interface/schema tables, capability list with a `since:` version) **in the same commit as the code** – not as a follow-up. The structured tables ARE the contract; the changelog is the audit trail. Never grow the agent-instructions file (`AGENTS.md` / `CLAUDE.md`) or the project doctrine file with per-ship narrative.

**Why / what it cost.** Deferred "paperwork later" is the single biggest source of index/spec drift; the narrative leaks into files meant to be stable indexes, and the spec stops describing reality.

**How to apply.** The ship checklist includes the doc rows; reconcile right after; a `since:` version on every new capability entry.

**Generalises to.** Any project where a spec/contract document is supposed to track the implementation.
