# CR-0083: agent-instructions enforce the deterministic-tooling discipline (never hand-roll IDs or indexes)

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement

## Summary

Every greenfield friction in this batch (CR0077-0082) shares one root cause: **nothing
told the field agent to trust the deterministic tooling, so it improvised** - hand-built
200+ lines of index on a false premise, hand-allocated ID ranges, and hand-coordinated a
7-agent fan-out. Better tools help, but the fix with the widest reach is the instructions
the agent reads at session start. The `templates/agent-instructions.md` starter (shipped to
every consuming project via `init`) should **enforce** the right workflow, not leave it
to be rediscovered. The field agent said as much: *"a note ... would have flipped my
entire approach."*

## Problem

The agent-instructions template onboards every consuming-project agent, but it does not
mandate the tool-first discipline. So an agent forms its workflow from a misleading
first-run signal (the empty-project `indexed=false`, CR0077) and a terse scaffold, and
reasonably concludes it must hand-manage structure. The result is exactly the error-prone,
high-token hand-rolling the deterministic cascade (CR0045) was built to eliminate.

This is the **enforcement** complement to the tooling CRs: CR0077-0082 make the tools
correct; this makes the agent use them.

## Proposed Changes

### Item 1: A mandatory "use the deterministic tooling" section

**Priority:** High
**Effort:** 2

Add an enforced section to `templates/agent-instructions.md` (and its `.CLAUDE.md`
variant), phrased as rules, not suggestions:

- **Create every artifact with `artifact.py new` / `/sdlc-studio` create.** It allocates
  a collision-free ID, writes the file, appends the index row, and wires a story into its
  parent epic. **Never hand-allocate IDs or hand-author `_index.md`** - the file is truth,
  the index is derived.
- **Set up the index files once** (run `init`, or create each `_index.md` from
  `templates/indexes/`) so `new` maintains them from the first artifact. A bare
  `indexed=false` on an empty project means "no index yet", not "the tool does not index".
- **For bulk authoring, fan out only over pre-wired scaffolds** - the tool owns structure
  (IDs, slugs, filenames, links, index); delegated agents fill **content** only.
- **The index is derived: run `reconcile` / `validate` to sync; never hand-copy
  file-owned fields** (story points, titles).
- **Follow the greenfield runbook** (CR0081) for command order.
- **Foundation first, then autosprint.** Build the foundation epic by hand to a green
  gate (it sets conventions every later story inherits); autosprint needs a runnable
  verification environment, so only hand subsequent epics to `autosprint --epic EPxx
  --goal done` once the gate runs green.
- **Record load-bearing decisions in the decisions log** (CR0080), not scattered across
  files.

Phrase each rule against shipped reality; rules that name not-yet-built capabilities
(`init` auto-seeding, `--batch`) activate as CR0077/0079 land.

### Item 2: Dogfood the rule in this repo's own AGENTS.md

**Priority:** Low
**Effort:** 1

Mirror the tool-first rule (a single pointer line) into this repo's own `AGENTS.md`, so
the skill dogfoods the enforcement it ships - consistent with how the repo runs its own
pipeline against its source.

## Acceptance Criteria

- [ ] `templates/agent-instructions.md` (+ `.CLAUDE.md` variant) gains a mandatory
      tool-first section: create via `new`, never hand-roll IDs/indexes, index is derived,
      bulk = fill pre-wired scaffolds, foundation-first-then-autosprint, decisions logged
- [ ] each rule reflects currently-shipped behaviour; capability-dependent rules are
      marked as activating with their CR
- [ ] this repo's `AGENTS.md` carries a matching tool-first pointer (dogfood)
- [ ] no contradiction with the greenfield runbook (CR0081) or `reference-doctrine.md`;
      links resolve; CHANGELOG `[Unreleased]` entry same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
