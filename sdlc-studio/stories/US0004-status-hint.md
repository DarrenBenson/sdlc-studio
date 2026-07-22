<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US0004-status-hint.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->

# US0004: Status dashboard and single-step hint

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** Orchestrator / Operator
**I want** a deterministic census of the pipeline pillars and a single recommended next step
**So that** I can render the status dashboard and decide what to do next from JSON, without re-reading every artifact in-context

## Context

### Persona Reference

**Orchestrator / Operator** - opens a session and wants to know project health and the next move at a glance.
[Full persona details](../personas.md#orchestrator--operator)

### Background

`scripts/status.py` provides two subcommands. `pillars` censuses the pipeline from artifact files and review state; `hint` walks a mechanical priority ladder to the single next command. The script reports only artifact-derived state - it deliberately leaves live metrics (lint, type-check, coverage) and the visual dashboard, the status cache, and the integrity scan to Claude (per `help/status.md`). Those decorations are the consumer's job; the script supplies the deterministic core.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | Behaviour | Report pipeline health and the next actionable step | `pillars` JSON + `hint` next_command |
| Epic | Architecture | Pure stdlib, read-only, unit-tested | No lint/coverage subprocess; nothing written |
| PRD | Determinism | Same disk -> same pillars and same hint | The hint ladder is fully mechanical |

---

## Acceptance Criteria

### AC1: Four-block pillar census from files and review state

- **Given** a workspace with a PRD, personas, 9 epics all `Ready`, and no stories
- **When** I run `python3 scripts/status.py pillars --root . --format json`
- **Then** the object has `generated_at`, plus `requirements` (`prd`, `personas` booleans; `epics`/`stories` each `{ total, by_status }`; `epics_ready_pct` counting `Ready`+`Approved`+`Done`; `stories_done_pct` counting `Done`), `code` (`trd` boolean and a `note` that lint/type-check/coverage are run live, not derivable from files), `tests` (`tsd` boolean; `test_specs` `{ total, by_status }`), and `reviews` (`has_review_state`, `review_files`, `latest`)
- **And** statuses are canonicalised (`Done (v2.66.0)` collapses to `Done`) and `*-consultations.md` files are excluded from counts
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/status.py pillars --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert {'requirements','code','tests','reviews'} <= set(d)"
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC2: `hint` returns a single next step from a mechanical ladder

- **Given** a workspace with a PRD and TRD but no TSD
- **When** I run `python3 scripts/status.py hint --root . --format json`
- **Then** the result is exactly `{ "next_command": "tsd", "reason": "no TSD yet" }`
- **And** the ladder is ordered: no PRD -> `prd generate`/`prd create`; no TRD -> `trd generate`/`trd create`; no TSD -> `tsd`; no personas -> `persona`; no epics -> `epic`; no stories -> `story`; a `workflow-state.json` present -> `resume workflow`; otherwise -> `story plan / story implement`
- **And** the `generate` vs `create` choice depends on whether any of `src`, `lib`, `app`, `cmd` directories exist (brownfield -> `generate`)
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/status.py hint --format json | python3 -c "import json,sys; assert 'next_command' in json.load(sys.stdin)"
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC3: Text rendering of pillars and hint

- **Given** I want a quick console read
- **When** I run `status.py pillars` (text, the default format)
- **Then** four lines print - `Requirements:` with PRD/personas yes-no, epic total and ready-plus %, story total and done %; `Code:` with TRD yes-no; `Tests:` with TSD yes-no and test-spec total; `Reviews:` with review-file count and latest yes-no
- **And** `status.py hint` (text) prints `/sdlc-studio <next_command>  (<reason>)`
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/status.py hint | grep -q "/sdlc-studio"
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC4: Done-percentage maths is empty-safe

- **Given** a type with zero files
- **When** the percentage is computed
- **Then** `_pct_done` returns `0` for an empty census (no division by zero), and otherwise `round(100 * done / total)` over the relevant done-states
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::CensusTests::test_pct_done
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC5: Cache, `--full`, and integrity flagging are consumer concerns, not script behaviour

- **Given** `help/status.md` describes `--full`, `--brief`, `--workflows`, `status-cache.json`, an INTEGRITY section (missing index entries, status mismatches, stale statuses, ID collisions), and non-standard-status flagging
- **When** I inspect `status.py`
- **Then** the script exposes only `pillars` and `hint`, each taking only `--root` and `--format` - it has no `--full`/`--brief`/`--workflows` flag, never reads or writes `status-cache.json`, and runs no integrity scan; the cache, the dashboard art, and the integrity/ID-collision checks are performed by Claude when it renders status (it may delegate the integrity scan to `reconcile.py` from US0001)
- **Verify:** shell ! python3 .claude/skills/sdlc-studio/scripts/status.py pillars -h 2>&1 | grep -q -- "--full"
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- `scripts/status.py pillars` and `hint`: the artifact-derived census, the mechanical hint ladder, JSON and text rendering.

### Out of Scope

- Live metrics (lint, type-check, coverage) - Claude runs these.
- `status-cache.json`, `--full`/`--brief`/`--workflows`, the visual dashboard, and the INTEGRITY / ID-collision / non-standard-status flagging from `help/status.md` - these are consumer concerns, not implemented by the script.

---

## Technical Notes

`count_by_status` tallies a type's files by canonical Status with a `total`. `gather` assembles all four blocks; `reviews` reads `.local/review-state.json` (default `{}`), counts `reviews/RV*.md`, and checks `reviews/LATEST.md`. `compute_hint` detects code by the presence of any of `src`/`lib`/`app`/`cmd`; the final two ladder rungs (`resume workflow`, `story plan / story implement`) carry `reason` text flagging them as judgement calls for the operator to confirm.

> **Doc-vs-code note:** the script's `pillars` JSON has no top-level "Code health %" or "Tests health %" - `help/status.md`'s weighted health scores and progress bars are computed by Claude from the census plus live checks, not by the script.

### API Contracts

```text
python3 scripts/status.py pillars [--root ROOT] [--format {text,json}]
python3 scripts/status.py hint    [--root ROOT] [--format {text,json}]

pillars JSON: { "generated_at",
  "requirements": { "prd", "personas", "epics": { "total", "by_status" },
                    "stories": { "total", "by_status" }, "epics_ready_pct", "stories_done_pct" },
  "code": { "trd", "note" },
  "tests": { "tsd", "test_specs": { "total", "by_status" } },
  "reviews": { "has_review_state", "review_files", "latest" } }
hint JSON: { "next_command", "reason" }
```

### Data Requirements

Reads epic/story/test-spec files, `prd.md`/`personas.md`/`trd.md`/`tsd.md`, `.local/review-state.json`, `reviews/RV*.md`, `reviews/LATEST.md`, and probes for `.local/workflow-state.json` and `src`/`lib`/`app`/`cmd`. Writes nothing.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| Zero epics / zero stories | `*_pct` returns 0; no division by zero |
| Status decorated (`Done (v2.66.0) · …`) | Canonicalised to `Done` for the tally |
| File with no `> **Status:**` line | Counted under `Unknown` |
| `*-consultations.md` present | Excluded from counts (not an artifact of the type) |
| `review-state.json` absent | `has_review_state` false; no crash |
| No `src`/`lib`/`app`/`cmd` directory | `hint` chooses `create` over `generate` for missing PRD/TRD |
| `workflow-state.json` present and pipeline seeded | `hint` returns `resume workflow` (judgement: confirm with operator) |
| Unexpected exception | `error: <msg>` on stderr, exit code 1 |

> **Minimum edge cases:** 8 for API stories, 5 for others

---

## Test Scenarios

- [ ] `pillars` JSON has all four blocks with the documented keys
- [ ] `epics_ready_pct` counts Ready+Approved+Done; `stories_done_pct` counts Done
- [ ] Decorated and status-less files canonicalise / fall to Unknown correctly
- [ ] `hint` ladder returns the first unmet rung in order
- [ ] `generate` vs `create` flips on presence of a code directory
- [ ] `_pct_done` returns 0 for an empty census
- [ ] Text rendering prints the four pillar lines and the hint line
- [ ] Script has only `--root`/`--format`; no `--full`/cache/integrity
- [ ] `reviews` block reads review-state and counts RV files

> **Minimum test scenarios:** 8 for API stories, 6 for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| [US0001](US0001-reconcile-census-autofix.md) | Related | Claude may delegate the status INTEGRITY scan to reconcile | Ready |
| [US0003](US0003-review-cadence.md) | Related | Both read `.local/review-state.json` | Ready |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| Python 3.10+ | Runtime | Available |

---

## Estimation

**Story Points:** 5
**Complexity:** Medium

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

Not applicable – story does not change runtime behaviour. The script is read-only and writes nothing.

---

## Open Questions

- [ ] None - behaviour fully extracted from `scripts/status.py`. - Owner: Darren Benson

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Story extracted (brownfield) from scripts/status.py |
