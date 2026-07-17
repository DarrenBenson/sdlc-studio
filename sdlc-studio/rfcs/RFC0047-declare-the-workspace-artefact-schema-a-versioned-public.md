# RFC-0047: Declare the workspace artefact schema a versioned public contract

> **Status:** In Review
> **Decomposed-into:** EP0084
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/reference-config.md

## Summary

The workspace artefact tree is read by external tooling as a de facto interface, but nothing about it is promised: a template, status-vocabulary or index change can silently break every consumer. Declare the artefact format a versioned, self-described public contract (no consumer is ever named; neutrality holds).

## Context

The `sdlc-studio/` workspace was designed as the skill's private working state, and every guarantee about it is currently internal: the templates emit it, `lib/sdlc_md.py` parses it, `validate.py` polices it, `reconcile.py` derives the indexes from it. Nothing outside the skill was ever meant to read it.

That stopped being true. Dashboards, orchestrators and sync tools now parse the artefact tree directly - read-only consumers that browse, search, score and execute against these files. The skill does not need to know who they are (and, for neutrality, must not name them), but their existence changes the format's status: **the artefact tree is an interface, whether or not it is declared as one.** Today a consumer can only vendor its own copy of the field knowledge and chase every skill release, and a routine template or vocabulary change is a silent breaking change downstream.

The pieces of a contract already exist; they are just not gathered or promised:

- an id grammar (numbered and ULID schemes, config-selected) with remote-aware allocation
- a fixed directory layout per artefact type, with `_index.md` as derived output
- header field vocabulary per type (the blockquote fields: Status, Priority, Points, Epic, and so on)
- a status vocabulary with terminal states, and gated transitions (`transition.py`)
- an executable AC DSL (`Verify:` lines, `verify_ac.py` semantics)
- runtime evidence JSON under `.local/` (sprint plan, verify reports, telemetry)
- a schema version concept (the v3 migration exists; `migrate` orchestrates upgrades)

What is missing is a single self-describing document that a consumer can build against, a version stamp it can pin, and a compatibility promise about how the format may change.

## Scope

**In scope:** the on-disk artefact format only - id grammar, directory layout, per-type header fields, status vocabulary and transition gate semantics, the Verify-line DSL, index format, and the compatibility policy for changing any of them. A decision on whether `.local/` runtime JSON is inside or outside the contract (D2).

**Out of scope:** any consumer-specific concern, any push or notification mechanism, any API surface beyond files on disk, and the skill's internal script interfaces (those remain free to change).

## Design Options

- **A) Status quo: the format stays implicit; external tools parse at their own risk and chase every skill release.** Zero cost now; every downstream breakage is deferred cost, invisible from this repo.
- **B) Documentation contract: a self-describing `reference-schema.md`** covering id grammar, directory layout, header field vocabulary per type, status vocabulary and transition gate semantics, the Verify-line DSL, and the derived index format; a schema version stamp plus a compatibility policy (additive = minor, rename/removal = major with migrate support); `validate.py` named as the executable definition. Consumers read one file and pin one version.
- **C) B plus a machine-readable schema descriptor (JSON) that `validate.py` itself consumes**, so the published contract and the enforcement cannot drift - the doc describes the descriptor, the validator loads it, and a consumer can load the same descriptor instead of hand-porting rules.

## Recommendation

B now; C when a second schema version actually ships. The binding rule: `validate.py` is the executable contract, the schema doc versions with the skill, and a breaking artefact-format change requires a major version plus a migrate path.

Two supporting rules worth ratifying with it:

1. **Health judgements stay upstream.** `validate.py`, `audit.py` and `reconcile.py` define what a healthy workspace means. A consumer that re-implements those rules will drift from them; the contract should say plainly that conformance tooling is part of the skill and consumers should run it (or its published descriptor), not rebuild it.
2. **The index stays derived.** `_index.md` is output, not input; the contract documents its format for readers but the write path remains the skill's scripts alone.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Where the schema version stamp lives (config-defaults.yaml key, a workspace marker file, or both) | Resolved (2026-07-17, operator): config key - `schema_version` in the project config, defaulted in config-defaults.yaml; reference-schema.md masthead states the current version |
| D2 | Whether `.local/` runtime evidence JSON (sprint plan, verify reports, telemetry) is inside the contract, a separately versioned annex, or explicitly excluded | Resolved (2026-07-17, operator): explicitly excluded from v1 - reference-schema.md states `.local/` is uncontracted and names a future annex as the path for evidence consumers |
| D3 | Act on this RFC or keep the status quo | Resolved (2026-07-17, operator): act, option B - refined into EP0084 (US0258-US0260) |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | Full draft: context, scope, options, recommendation, decisions |
| 2026-07-17 | sdlc-studio | D1-D3 resolved with the operator; refined into EP0084 / US0258-US0260 via `refine apply` |
