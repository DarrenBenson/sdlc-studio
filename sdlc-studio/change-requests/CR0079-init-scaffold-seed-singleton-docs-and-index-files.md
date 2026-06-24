# CR-0079: init becomes executable - create the folder structure, indexes, and singleton docs

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Feature

## Summary

`init` is **documentation, not an executable** - `help/init.md` describes what a project
needs (config, directory tree, agent-instructions, indexes) but no script writes any of
it, so a greenfield agent does the whole checklist by hand. Make `init` a deterministic
command that creates the full folder structure, seeds the config and agent-instructions
from templates, pre-creates the per-type `_index.md` files (which alone dodges the
empty-project index trap - see CR0077), and **optionally** (`--scaffold`) seeds the
singleton docs (`prd`/`trd`/`tsd`/`personas`). The greenfield agent called a real init
*"the single biggest greenfield win"*.

> This is the step *before* **RFC0019**'s authoring loop runs - it leaves a fresh tree
> index-complete with a PRD ready to decompose.

## Problem

Confirmed by a greenfield reflection (verbatim): *"No init script - it's a manual
checklist. I hand-made `.sdlc-studio.yaml`, `sdlc-studio/.config.yaml`, the directory
tree, AGENTS.md/CLAUDE.md/copilot-instructions.md. help/init.md describes outputs but
there's no init that writes them. A one-shot init (detect stack, copy agent-instructions
templates, seed config, create the empty index files - which would've dodged my whole
index problem) is the single biggest greenfield win."*

Verified: there is no `scripts/init.py`; `init` is a model-interpreted prose workflow.
Every building block already ships - `templates/config.yaml`,
`templates/agent-instructions.*`, `templates/indexes/*`, `templates/core/*` - nothing
instantiates them deterministically. The empty directory tree (no `_index.md`) is also
what produces the misleading `indexed=false` first-run signal CR0077 fixes; seeding the
indexes here closes it from the other side.

## Proposed Changes

### Item 1: Deterministic `init` - structure, config, agent-instructions, indexes

**Priority:** High
**Effort:** 3

A `scripts/init.py` (with `--detect` for stack inference and `--force`) that:

1. creates the full directory tree (`epics/`, `stories/`, `plans/`, `test-specs/`,
   `bugs/`, `workflows/`, `change-requests/`, `rfcs/`, `retros/`, `decisions/`,
   `reviews/`, `.local/`);
2. seeds `.sdlc-studio.yaml` / `sdlc-studio/.config.yaml` from `templates/config.yaml`
   with detected stack + style;
3. copies `templates/agent-instructions.*` to `AGENTS.md` / `CLAUDE.md` /
   `copilot-instructions.md` if absent, filling known placeholders;
4. pre-creates every `<dir>/_index.md` from `templates/indexes/*` with zero rows and
   zeroed counts (**reuse the CR0077 index helper** - no duplicate logic).

Idempotent: never overwrites an existing file (report and skip). The model-driven
`init` prose becomes a thin wrapper over the script.

**Config is detect-then-confirm, not silent auto-write.** Config is load-bearing
(coverage gates, release strategy, test frameworks, contract anchors) and greenfield
detection is a guess - on an empty repo there is no `package.json` to read, so a wrong
auto-written guess is worse than a 10-second look. `init --detect` prints the
detected/defaulted config as a **diff and asks once** (`[Y]`/edit); `--yes` skips the
prompt on a brownfield repo with an unambiguous stack. The **non-judgement** steps -
creating the directory tree, copying agent-instructions, seeding the empty index files -
need no confirmation; just do them.

### Item 2: `--scaffold` seeds the singleton docs

**Priority:** Medium
**Effort:** 2

With `--scaffold`, copy `templates/core/{prd,trd,tsd,personas}.md` to
`sdlc-studio/*.md`, filling the project-name / date / style placeholders init knows and
leaving the rest as `{{...}}`. **Leave high-judgement narrative fields obviously empty**
(`{{problem_description}}` etc.) so a confident-sounding default is never mistaken for a
real decision (the greenfield agent's explicit caveat). PVD is multi-repo and stays out
of the default scaffold.

## Acceptance Criteria

- [x] `init` creates the full directory tree, config, and agent-instructions files
      deterministically; re-running never overwrites (reported and skipped)
- [x] config is presented as a diff for one confirmation (`[Y]`/edit; `--yes` skips on an
      unambiguous brownfield stack); the directory tree, agent-instructions, and empty
      indexes are written without a prompt
- [x] every per-type `_index.md` is created with zero rows and zeroed counts, sharing the
      CR0077 index helper (no duplicate logic) - depends on CR0077
- [x] after `init`, the first `new` of any type reports `indexed=true` (the empty-project
      trap is closed)
- [x] `init --scaffold` seeds `prd`/`trd`/`tsd`/`personas` from `templates/core/*` with
      known placeholders filled and high-judgement fields left visibly empty
- [x] scaffolded singletons pass `validate` (placeholder handling per CR0056)
- [x] unit tests cover: tree+config+indexes created, idempotent re-run, `--scaffold`
      singletons; help/init.md updated; CHANGELOG `[Unreleased]` entry same commit (LL0004)

## Dependencies

### CR Dependencies

| CR | Title | Status | Required Before |
| --- | --- | --- | --- |
| [CR-0077](CR0077-greenfield-new-lazy-index-creation-plus-full-template.md) | greenfield new - lazy index creation plus full-template scaffolds | Proposed | Item 2 (shared index helper) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
