---
id: LL0001
title: Reconcile from a file census, not from the existing counts
tags: [reconcile, indexes, drift]
added: 2026-06-03
origin: recurring index drift in a multi-artifact project
---

**Lesson.** When reconciling an index against files, rebuild it from a full on-disk **census** and detect three drift classes — status mismatch, **missing row** (a file with no index row), and orphan row (a row with no file) — and recompute every Summary count from the census. Never adjust the existing (possibly-drifted) total.

**Why / what it cost.** Indexes repeatedly under-counted because new files were added past the last table row; "the count looks about right" hid files that had no row at all. The banner said one total, the Summary another, the disk a third.

**How to apply.** `glob` the type's files → build the truth set → diff against the index for all three classes → write counts from `len(census)`, not `old ± delta`.

**Generalises to.** Any derived index/registry/dashboard fed by a directory of source-of-truth files.
