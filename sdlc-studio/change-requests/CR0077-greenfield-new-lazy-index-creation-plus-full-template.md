# CR-0077: greenfield new - lazy index creation plus full-template scaffolds

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

The deterministic `new` cascade (`scripts/artifact.py`, CR0045) is sound, but it
under-serves a **greenfield** start - the case where an agent is creating the very
first epic and stories from scratch. Two gaps push agents to abandon the tool and
hand-author artifacts, losing the wiring the tool exists to provide.

## Problem

Evidence from an agent starting a brand-new project (verbatim): *"artifact.py only
generates minimal scaffolds without creating index files, so I'll need to author the
artifacts using full templates and manage the index files myself. The tool's main
value is providing collision-free ID allocation... I'm going to author everything by
hand with complete templates for maximum quality and control."*

Two distinct gaps:

1. **No index → no indexing.** `_header_cells()` returns `None` when
   `<dir>/_index.md` does not yet exist, so `new` writes the artifact but reports
   `indexed=false` and skips the row. On greenfield there is no index yet, so the
   *first* artifact of every type is never indexed and the agent must hand-build the
   index - exactly the friction CR0045 set out to remove. The index **templates**
   already ship (`templates/indexes/<type>.md`); `new` simply never instantiates them.

2. **Minimal scaffold vs full template.** `_render()` emits a terse inline scaffold.
   The rich `templates/core/<type>.md` (the authoring guidance) is never wired in, so
   an agent wanting that structure bypasses `new` entirely - and loses the id
   allocation, index row, and epic cross-link in the process. The minimal scaffold is
   a deliberate "tool wires, agent fills" choice and should stay the default; the fix
   is an **opt-in** richer scaffold, not a default change.

> These two primitives are the deterministic substrate for **RFC0019** (the authoring
> autosprint - a guided PRD -> epics -> stories loop).

## Proposed Changes

### Item 1: Lazily create the index when missing

**Priority:** High
**Effort:** 1

When `new` finds no `<dir>/_index.md`, instantiate it from
`templates/indexes/<type>.md` (resolved relative to the skill, as `_render` already
resolves nothing external today - add a skill-root locator), then append the row as
normal. Result: the first artifact of a type is indexed like every subsequent one.
`--dry-run` reports `would_create_index: true`. Keep idempotent: never clobber an
existing index.

**Why this is the headline.** A greenfield agent re-tested the tool and confirmed `new`
*does* wire the parent epic and *does* maintain the index when one exists - the **only**
gap is "won't create an index from nothing". But that one gap, hit on the empty-project
first run, emits a silent `indexed=false` that the agent over-generalised to "the tool
doesn't do indexes", and then hand-built 200+ lines of index by hand. The fix is as much
about not teaching the wrong lesson as about the index: once `new` auto-creates, the
misleading first-run signal disappears. Pair with a docs note in `reference-scripts.md` /
`--help` making the one-call behaviour (id + slug + file + index row + epic wiring)
salient (see CR0081).

### Item 2: Opt-in full-template scaffold

**Priority:** Medium
**Effort:** 2

Add `--template full` (default stays `minimal`). With `full`, seed the file from
`templates/core/<type>.md`, still stamping the provenance header
(`Created-by: sdlc-studio new`) and the deterministic metadata block so `validate`
and provenance checks behave identically. Placeholders (`{{...}}`) remain unresolved
in both modes, so `conformance`/`validate` treat the two identically (CR0056) - the
only difference is how much structure the agent gets for free.

## Acceptance Criteria

- [x] `new --type epic` (or any type) in a directory with no `_index.md` creates the
      index from `templates/indexes/<type>.md` and appends the row; `indexed=true`
- [x] index creation is idempotent (re-running `new` never rewrites an existing index)
      and `--dry-run` reports `would_create_index` without writing
- [x] `new --type story --template full --epic EPxxxx` seeds the file from
      `templates/core/story.md` with the provenance header and metadata block intact
- [x] `--template minimal` (the default) is byte-identical to today's output
- [x] `validate` and the provenance/conformance checks pass on both scaffold modes
      (placeholder handling unchanged from CR0056)
- [x] unit tests cover: first-artifact-of-type indexing, idempotent re-run, both
      template modes; CHANGELOG `[Unreleased]` entry in the same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Both items confirmed by a greenfield agent's grounded re-test; root cause refined to the misleading empty-project first-run signal |
