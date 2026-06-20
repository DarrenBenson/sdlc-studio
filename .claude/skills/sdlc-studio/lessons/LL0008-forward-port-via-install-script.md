---
id: LL0008
title: Forward-port a skill via its install script, not per-file copy
tags: [process, skill-dev, sync, dogfood]
added: 2026-06-20
origin: determinism sprint - manual per-file cp to the installed skill copy each unit
---

**Lesson.** When a repo dogfoods a skill against its own source, sync the working
source to the installed copy with the skill's **install script** (`install.sh
--local`), not hand-picked `cp` commands per file. A manual copy list silently
misses a file the moment a unit touches more than you remember.

**Why / what it cost.** Across a multi-unit sprint I forward-ported with per-file
`cp` each time and only caught drift with an end-of-sprint `diff -rq`. One forgotten
file would have meant the operator reloading a half-old skill - the exact failure
the forward-port exists to prevent. The install script copies the whole tree
deterministically; the diff then only confirms.

**How to apply.** After a green unit, run the install/sync target (`install.sh
--local`) and a `diff -rq <source> <installed>` (excluding `__pycache__`/`.local`)
as the verification, rather than reconstructing the changed-file set by hand.

**Generalises to.** Any "edit here, runs from there" setup - a skill, a plugin, a
dotfile, a vendored library - where the deployed copy must track the source and the
sync is currently a remembered list of files.
