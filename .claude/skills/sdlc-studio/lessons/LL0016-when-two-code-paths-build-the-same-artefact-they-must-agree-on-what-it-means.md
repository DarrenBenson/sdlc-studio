---

id: LL0016
title: When two code paths build the same artefact, they must agree on what it MEANS
tags: [consistency, data-loss, bug-class, architecture]
added: 2026-07-13
origin: sdlc-studio-lens
---

**Lesson.** A hybrid sync had two fetch paths (a tarball and an incremental Trees+Blobs diff) that each produced a 'manifest of live paths'. They disagreed twice: the tarball excluded symlinks (TarInfo.isfile() is False) while the Trees API reports them as type 'blob'; and one filtered out non-document files (_index.md) while the other did not.

A path that is live under one path and absent under the other gets ADDED as a document by one sync and DELETED by the next, for ever - flip-flopping the corpus and reporting spurious deletions.

Two producers of the same artefact need a shared, tested definition of what belongs in it, not two independently plausible ones.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
