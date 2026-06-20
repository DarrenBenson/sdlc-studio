---
id: LL0007
title: Amend the AC in the same unit when the implementation deviates
tags: [process, acceptance-criteria, critic, honesty]
added: 2026-06-20
origin: determinism sprint - implementation twice silently narrowed a CR's AC
---

**Lesson.** When you deliver something different from what an acceptance criterion
literally says (a sounder design, a narrower scope, a different mechanism), **amend
the AC in the same unit of work** and record why. Do not leave the AC asserting
behaviour the code does not have. The independent critic must explicitly check
**AC-vs-delivered-behaviour**, not just "do the tests pass".

**Why / what it cost.** Twice in one sprint the build deviated and the paperwork
silently went false: a CR said "scripts read the config" but only a loader shipped
(no consumer); a CR said "reads the WF execution table" but the code read Status
instead. Both deviations were *better* engineering, but the AC became a lie a
reviewer would close against without noticing. The critic caught both; nothing
deterministic did. A green test suite over a false AC is the spec-gaming trap - the
oracle passes while the contract rots.

**How to apply.** Deviating from an AC is fine - but in the **same commit**: reword
the AC to the shipped behaviour, add a one-line rationale to the CR/story revision
history, and have the critic's checklist include "does each AC still describe what
was built?". Treat an unamended deviation as a defect, not a footnote.

**Generalises to.** Any spec-driven workflow where acceptance criteria are the
contract and a passing test suite is the gate - the gap between "tests green" and
"contract honoured" is where quality silently leaks.
