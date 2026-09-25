# US0090: Deterministic plan-review trigger and gate

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0019
> **Persona:** Engineering seat
> **Affects:** scripts/plan_review.py, scripts/critic.py, scripts/transition.py, templates/config-defaults.yaml

## User Story

**As an** orchestrator driving a sprint
**I want** a story with spec-derived ACs to be blocked from implementation until an independent plan-review verdict exists, fired by a deterministic rule
**So that** a mis-pinned AC cannot silently propagate into a faithful build of the wrong plan (the N=5 "bad plan propagates" failure mode)

Closes part of CR0194 (the gate + trigger). Era-gated behind `schema_version: 3`; dormant on v2.

## Acceptance Criteria

### AC1: The trigger fires deterministically on checkable signals

- **Given** a story whose ACs/Affects cite a configured spec path, OR whose `affects_files` count is at/above `plan_review.affects_files_threshold`, OR whose routed difficulty band is at/above `plan_review.min_difficulty`
- **When** `plan_review.triggers(text, root)` is evaluated
- **Then** it returns `fired: True` with the matched signal(s), computed purely from the artefact fields and config with no model call
- **Verify:** manual - retired by US0909: the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC2: A triggered story cannot enter implementation without a plan-review verdict

- **Given** a schema-v3 story that trips the trigger and has no recorded plan-review APPROVE from a reviewer distinct from the plan's author
- **When** it transitions Ready -> In Progress (or `plan_review.gate` is checked)
- **Then** the transition is blocked with a message naming the missing plan-review; a recorded plan-review APPROVE (reviewer != author) unblocks it; the gate is a no-op under schema v2
- **Verify:** manual - retired by US0909: the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC3: A skip is possible only through a recorded operator override

- **Given** a triggered story with no plan-review verdict
- **When** an operator override is recorded (ledger-visible marker)
- **Then** the gate passes and names the override; there is no silent-skip path, and an untriggered story passes without any verdict
- **Verify:** manual - retired by US0909: the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC4: The plan-review verdict phase is recorded and readable

- **Given** `critic.py record` gains a `--phase {delivery,plan-review}` field (default `delivery`)
- **When** a plan-review verdict is recorded
- **Then** it is written distinctly from a delivery critic verdict and `plan_review.gate` reads only plan-review-phase APPROVEs
- **Verify:** manual - retired by US0909: the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

### AC5: The new script is catalogued

- **Given** `scripts/plan_review.py` ships
- **When** the docs floor is checked
- **Then** `reference-scripts.md` catalogues it and `reference-config.md` documents the `plan_review` config keys
- **Verify:** manual - retired by US0909: the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict
- **Verified:** manual (2026-09-25) - retired, superseded by US0909

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0194 (gate + deterministic trigger) |
| 2026-09-25 | Claude Opus 5.5 | AC1, AC2, AC3, AC4, AC5 retired by US0909 (D0259 pattern): the spec plan-review gate, its trigger, its override field and its `plan_review.py` script were deleted; a story reaches In Progress and Done with no plan-review verdict |
