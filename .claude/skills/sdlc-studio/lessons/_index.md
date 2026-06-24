# Cross-Project Lessons-Learned Registry

Generalisable engineering/process lessons that improve decisions on **any**
sdlc-studio project. Lives **in the skill** (shared across projects), distinct
from a project's own `.local/lessons.md` (transient agentic-wave failure memory)
and from per-project memory (project-specific facts).

> **Recall** relevant lessons before substantive decisions (`/sdlc-studio lessons recall`).
> **Promote** a lesson here (`/sdlc-studio lessons add --global`) only once it clearly
> generalises beyond the project that surfaced it. Keep entries tight.

## All Lessons

| ID | Title | Tags |
| --- | --- | --- |
| [LL0001](LL0001-reconcile-from-file-census.md) | Reconcile from a file census, not from the existing counts | reconcile, indexes, drift |
| [LL0002](LL0002-cross-repo-artifact-number-collisions.md) | Cross-repo artifact-number collisions (shared CR/RFC namespace) | cross-repo, numbering |
| [LL0003](LL0003-config-schema-vs-type-alignment.md) | Config-schema vs type alignment – strict validators strip unknown fields | schema, validation, bug-class |
| [LL0004](LL0004-ship-paperwork-in-the-same-commit.md) | Ship the paperwork in the same commit as the code | process, docs, release |
| [LL0005](LL0005-full-review-set-includes-a-code-leg.md) | The between-releases review set must include a CODE leg | review, release, quality |
| [LL0006](LL0006-deploy-meta-files-gap-class.md) | Deploy meta-files gap – new boot-read file → every deploy path | deploy, packaging, gap-class |
| [LL0007](LL0007-plan-from-value-not-bare-priority-a-ready-story-whose-verifiers-pass-is-already-done.md) | Plan from value, not bare priority; a Ready story whose verifiers pass is already done | sprint, planning, wsjf, personas, conformance |

## Notes

- IDs are global and zero-padded: `LL{NNNN}`. Files: `LL{NNNN}-{slug}.md`.
- A lesson = **generalisable** wisdom (what to do differently next time, anywhere). A project fact (a config path, an incident, a box name) is **memory**, not a lesson.
- This folder ships with the skill, so the seed set is release-curatable; Claudes add to it as they work, and additions are blessed into the next skill release.
- Format: see `_template.md`. Mechanism + recall/promote hooks: `help/lessons.md` + `reference-agentic-lessons.md`.
