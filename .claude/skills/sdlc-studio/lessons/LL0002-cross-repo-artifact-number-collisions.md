---
id: LL0002
title: Cross-repo artifact-number collisions (shared CR/RFC namespace)
tags: [cross-repo, cr, rfc, numbering]
added: 2026-06-03
origin: two repos sharing a single CR/RFC numbering namespace
---

**Lesson.** When two repos share an artifact namespace (e.g. both file bridge CRs), two agents grab the same number concurrently. Before assigning a number, `git fetch` and check the highest on **`origin/main`** – not just the local tree, which may be days stale. On collision, renumber the **unshipped / lower-priority** side, and compare the *contracts* (field names, endpoints), not just the numbers – a same-numbered consumer artifact can diverge from what the producer ships.

**Why / what it cost.** A blind local count produced colliding CR numbers across repos; the deeper risk was a consumer CR's shape silently diverging from the shipped producer API.

**How to apply.** `git ls-tree -r origin/main -- <artifact-dir>/` for the real max; stash-and-pull a stale local checkout before filing; cross-link the two sides.

**Generalises to.** Any shared, monotonically-numbered resource edited by more than one actor without a lock (CRs, RFCs, migrations, ports).
