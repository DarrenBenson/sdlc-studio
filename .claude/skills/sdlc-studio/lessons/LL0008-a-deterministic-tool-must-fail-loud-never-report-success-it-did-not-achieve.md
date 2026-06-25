---
id: LL0008
title: A deterministic tool must fail loud, never report success it did not achieve
tags: [tooling, determinism, false-green, mis-report, bug-class]
added: 2026-06-25
origin: sdlc-studio field-upgrade retrospective, 2026-06-25
---

**Lesson.** **Lesson.** A deterministic helper must never (a) report an action it did not perform, (b) return a clean pass by finding nothing to check, or (c) silently ignore input it could not parse. On any of these it fails loud or reports the gap explicitly. The summary line is a contract: if a human cannot trust it without re-verifying against the file census, the tool has failed even when its exit code is 0.

**Why / what it cost.** One field upgrade hit the whole class at once. reconcile apply printed a status flip and a summary recompute it never persisted (git showed the index unchanged), yet reported clean. validate personas reported well-formed because its flat glob matched zero nested personas - a vacuous pass read as a real one. conformance.adopt_after silently did nothing on a bare-integer value its parser could not read, leaving the gate red with no error. Net effect: the operator could trust no summary line and hand-verified every count against the file census - the opposite of what these tools exist to remove.

**How to apply.** Three checks on every script. After a targeted write, diff the buffer and raise or warn if the edit matched nothing - never print changed for a no-op. Treat an empty match set as nothing-inspected and say so, never as a clean pass. Reject unparseable config loudly instead of coercing it to None or a no-op. Add a failing-first test for each: a claimed-but-unmade edit raises; a found-nothing case does not pass; a malformed cutoff errors.

**Generalises to.** Any deterministic tool whose output a human acts on without re-deriving it - reconcilers, validators, gates, and config-driven checks.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
