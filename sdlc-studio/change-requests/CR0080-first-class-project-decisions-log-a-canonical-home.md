# CR-0080: first-class project decisions log - a canonical home for resolved decisions and open questions

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

A greenfield project resolves a handful of load-bearing decisions early (stack choices,
the API contract, scope cuts, answers to the PRD's open questions). These propagate into
every downstream epic and story, and every delegated authoring agent needs them
verbatim, yet there is **no canonical home** for them. The agent who surfaced this scattered them
across `plan.md`, `PRD §11`, and `AGENTS.md` and then pasted them into each of 7
sub-agents. Add a first-class project decisions log the tool knows about, so the
"project spine" lives in one place and feeds the shared context delegated agents read.

## Problem

From a greenfield reflection (verbatim): *"The decisions record had no obvious home. The
four resolved open questions are load-bearing for every downstream artifact, but I had to
invent where they live (I scattered them across plan.md, PRD §11, and AGENTS.md). A
first-class decisions log the tool knows about - and feeds into the handoff context -
would stop that."* And on the fan-out: *"those four resolved open questions are the
project's spine and every agent needed them verbatim."*

There is precedent but no fit: `autosprint` keeps a per-tranche **decisions ledger**
(`scripts/ledger.py` -> `sdlc-studio/decisions/<tranche>.md`), but that is scoped to a
delivery run, not the project-level decisions that authoring depends on. RFC artifacts
hold *design* decisions, not project-setup ones. The gap is a durable, project-scoped
decisions record that exists from the first artifact onward.

**It is not only product decisions - implementation conventions belong here too.**
The implementation reflection confirmed the same gap one layer down: the foundation
tranche set conventions every later story inherits - the `{error, fields}` envelope, the
`lst_`/`itm_`/`usr_`/`tok_` ID scheme, stored-hash (not signed) tokens, forward-only SQL
migrations, pg-mem for tests - but they *"live only in code, the README, the commit
message, and the session plan.md ... `grep pg-mem sdlc-studio/` returns nothing."* So an
autosprint run building the next epic would not know to use the pg-mem harness or the
exact error shape. The decisions home must be **agent-read** (injected into the agent
prompt / handoff context) and cover implementation conventions, not just product
decisions - that *"would have prevented the TOKEN_SECRET-vs-stored-hash divergence
outright."*

## Proposed Changes

### Item 1: A canonical project decisions log

**Priority:** Medium
**Effort:** 2

A single `sdlc-studio/decisions.md` holding resolved decisions as a **structured,
append-only table** (free-form prose was the agent's actual failure mode - scattered
across three files, re-pasted into seven prompts). Columns:

| ID | Decision | Rationale | Status | Supersedes | Date |
| --- | --- | --- | --- | --- | --- |
| D1 | Anonymous-first, accounts in M2 | avoids a sign-up wall | accepted | -- | 2026-06-24 |

A thin `decisions` helper (`decision add` / `decision list`) keeps it append-only and
greppable. Created on `init` (empty header). The autosprint per-tranche ledger stays
as-is; this is the project-level spine it references.

**Open questions stay in the PRD, but a question and a decision are one object at two
lifecycle stages.** Open questions live in `PRD §Open Questions` (where reviewers expect
them); when resolved, the helper **promotes** the entry into the decisions table with a
back-link (`from PRD-OQ3`) and flips its status open -> resolved. One record, two views -
never duplicated as free text in both (that is the drift trap this avoids).

### Item 2: Feeds the delegated-authoring context

**Priority:** Low
**Effort:** 1

When authoring is fanned out to sub-agents (manually or via the authoring loop, RFC0019),
the decisions log is part of the canonical "handoff context" the agents are pointed at -
so resolved decisions are referenced once, not pasted N times. The ~80% of the per-agent
preamble that is identical (PRD path, personas, decisions, the contract, conventions)
collapses to a single reference plus a few epic-specific lines.

## Acceptance Criteria

- [x] `sdlc-studio/decisions.md` template exists with the structured table
      (ID/Decision/Rationale/Status/Supersedes/Date); `init` seeds an empty one
- [x] a `decisions` helper appends an entry and lists by status; entries are append-only
      and survive context compaction
- [x] resolving a PRD open question promotes it into the table with a back-link
      (`from PRD-OQNN`); it is never duplicated as free text in both (one record, two views)
- [x] the log is referenced by the greenfield runbook (CR0081) and named as part of the
      authoring loop's handoff context (RFC0019); no overlap with the autosprint
      per-tranche ledger (`ledger.py`) - the relationship is documented
- [x] the log covers **implementation conventions** (error shape, ID scheme, token
      strategy, migration style, test harness) as well as product decisions, and is
      injected into delegated-agent / autosprint context (`grep` of `sdlc-studio/` finds them)
- [x] docs: help entry + reference pointer; CHANGELOG `[Unreleased]` entry same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Delivered: `decisions.py` add/list/promote, template, `init` seeding, tests. AC4's greenfield-runbook cross-reference is completed in CR0081 (same release); RFC0019 already names the log in its handoff context and the ledger distinction is documented |
