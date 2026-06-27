---
id: LL0012
title: A new private helper that shadows a module-level name silently breaks every existing caller
tags: [python, refactoring, naming, testing]
added: 2026-06-27
origin: sdlc-studio
---

**Lesson.** Before defining a same-named helper in a shared module, grep the module for the name. In EP0010 a new reconcile._row_id(line) shadowed an existing _row_id(cells, status_col, id_col); the new tests passed but the full suite surfaced 58 downstream failures. Python takes the last definition, so the collision is invisible at the new call site. Run the FULL suite, not just the new test, after touching a shared module.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
