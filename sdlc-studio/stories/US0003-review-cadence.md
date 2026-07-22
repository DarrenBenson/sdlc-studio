<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US0003-review-cadence.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->

# US0003: Unified review with modified-since detection and cadence

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** Orchestrator / Operator
**I want** the unified review to start from a deterministic list of artifacts modified since their last review, plus persona-usage and count inputs, so the five-leg review (including the CODE leg) judges from data
**So that** I run reviews on a deliberate cadence without re-deriving project state in-context, and nothing stale slips through

## Context

### Persona Reference

**Orchestrator / Operator** - runs the unified review at cadence boundaries (epic close, every 5 minor releases, > 4 weeks).
[Full persona details](../personas.md#orchestrator--operator)

### Background

The unified review (PRD - TRD - TSD - Persona - Code) is Claude's judgement call. `scripts/review_prep.py prep` front-loads the *mechanical* inputs each leg needs so the review starts from data: which artifacts changed since their last review, which personas are defined-but-unreferenced, and the count / AC-verification inputs. The script makes no judgements and mutates nothing - it gathers. The CODE review leg, the cadence decision, and the review verdict all stay Claude's judgement; the script only supplies inputs.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | Behaviour | Detect artifacts modified since last review; enforce cadence (incl. CODE leg) | Staleness is computed mechanically; the CODE leg verdict is Claude's |
| Epic | Architecture | Pure stdlib, read-only, unit-tested | No git subprocess; mtime is the deterministic signal; nothing is written |
| PRD | Determinism | Same disk + same review-state -> same `needs_review` set | Comparison is `mtime > last_reviewed`, string-compared as ISO-8601 |

---

## Acceptance Criteria

### AC1: Modified-since-review detection from mtime and review-state.json

- **Given** `sdlc-studio/.local/review-state.json` with `artifacts.prd.last_reviewed = "2026-06-01T00:00:00Z"` and a `sdlc-studio/prd.md` whose mtime is later
- **When** I run `python3 scripts/review_prep.py prep --root . --format json`
- **Then** `staleness.prd` is `{ "path": "sdlc-studio/prd.md", "last_modified": "<mtime ISO-8601 Z>", "last_reviewed": "2026-06-01T00:00:00Z", "needs_review": true }`, and `needs_review` (top level) is the sorted list of every key whose `needs_review` is true
- **And** an artifact with no entry in `review-state.json` (`last_reviewed == null`) always reports `needs_review: true`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::StalenessTests::test_no_review_state_means_needs_review
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC2: Staleness covers project docs and every artifact

- **Given** a workspace
- **When** `prep` builds the staleness map
- **Then** it considers the four project docs `prd`, `trd`, `tsd`, `personas` (keyed by name) plus every artifact file of every type (keyed by record ID, e.g. `EP0001`, `US0042`), skipping any that does not exist on disk
- **And** the "last modified" signal is the file mtime rendered as an ISO-8601 Z string (NOT a git timestamp), so the comparison is string-lexicographic against `last_reviewed`
- **Verify:** grep "PROJECT_DOCS" .claude/skills/sdlc-studio/scripts/review_prep.py
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC3: Persona usage - defined vs referenced in the PRD

- **Given** `sdlc-studio/personas.md` with H2 headings and `sdlc-studio/prd.md`
- **When** `prep` computes `persona_usage`
- **Then** `defined` is every H2 (`##`) heading text in personas.md; `referenced_in_prd` is each defined name appearing as a substring of prd.md; `unused` is defined-minus-referenced; and `method` records the heuristic string
- **And** the `unused` list is what the Persona leg judges (refresh / archive / first-consult)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::PersonaUsageTests::test_defined_referenced_and_unused
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC4: Count and AC-verification inputs for the CODE and test legs

- **Given** the verify report from US0002 may or may not exist
- **When** `prep` computes `inputs`
- **Then** `inputs.counts` is a map of every artifact type to its file count, and `inputs.ac_verification` is either `null` (no `sdlc-studio/.local/verify-report.json`) or `{ "stories": <n>, "verified": <sum>, "failed": <sum> }` summed across the report's stories
- **And** these inputs feed the CODE review leg, whose verdict stays Claude's judgement - the script computes no health score and renders no dashboard
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_review_prep.py::InputsTests::test_counts_and_ac_summary
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC5: Cadence and review-state lifecycle are review-command, not script, concerns

- **Given** the cadence (every 5 minor releases, per-epic completion, > 4 weeks since last unified review) and the writing of `review-state.json` / `reviews/LATEST.md`
- **When** the review command runs
- **Then** `review_prep.py` only *reads* `review-state.json` and *emits* inputs; it has a single `prep` subcommand and never writes review state, never enforces an interval, and provides no pause/resume queue - the cadence decision, the `review-state.json` write (step 4 of `reference-review.md#review-workflow`), and `LATEST.md` are performed by Claude as part of the review command
- **Verify:** shell f=sdlc-studio/.local/review-state.json; b=$(cat "$f" 2>/dev/null; stat -c %Y "$f" 2>/dev/null); python3 .claude/skills/sdlc-studio/scripts/review_prep.py prep --format json >/dev/null 2>&1; a=$(cat "$f" 2>/dev/null; stat -c %Y "$f" 2>/dev/null); test "$b" = "$a"
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- `scripts/review_prep.py prep`: staleness (mtime vs review-state), persona usage, count / AC-verification inputs, JSON and text output.

### Out of Scope

- The review verdict and the CODE leg judgement (Claude, per `reference-review.md`).
- Writing `review-state.json` / `reviews/LATEST.md`, enforcing the cadence interval, and any pause/resume queue - the script does none of these; they are review-command steps or reference-doc concepts, not script behaviour.

---

## Technical Notes

`staleness` reads `.local/review-state.json` (defaulting to `{}` when absent or malformed via `sdlc_md.read_json`). `_mtime_iso` formats `path.stat().st_mtime` as `%Y-%m-%dT%H:%M:%SZ`; because both timestamps are ISO-8601 Z strings, `modified > last_reviewed` is a valid lexicographic comparison. `persona_usage` matches H2 headings (`^##\s+(.+?)\s*$`) against a substring search of prd.md - a deliberately simple, deterministic heuristic, recorded in the `method` field.

> **Doc-vs-code note for the review leg:** `reference-review.md` step 4 says `last_modified` should come from the git-log timestamp; the script uses file mtime. The two agree in a clean checkout but can differ after a `git clone` (which resets mtimes). The review command should treat the script's `needs_review` set as the starting point and reconcile with git history when precision matters.

### API Contracts

```text
python3 scripts/review_prep.py prep [--root ROOT] [--format {text,json}]

JSON: { "generated_at",
        "staleness": { <key>: { "path", "last_modified", "last_reviewed", "needs_review" } },
        "needs_review": [ <key>, ... ],          # sorted
        "persona_usage": { "defined": [...], "referenced_in_prd": [...], "unused": [...], "method" },
        "inputs": { "counts": { <type>: int }, "ac_verification": null | { "stories", "verified", "failed" } } }
```

### Data Requirements

Reads `sdlc-studio/{prd,trd,tsd,personas}.md`, every artifact file, `.local/review-state.json`, and `.local/verify-report.json`. Writes nothing.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| `review-state.json` absent or malformed | Treated as `{}`; every artifact reports `needs_review: true` |
| A project doc (e.g. `tsd.md`) does not exist | Skipped entirely - no staleness entry |
| `personas.md` absent | `defined` is empty; `unused` is empty |
| `prd.md` absent | `referenced_in_prd` empty; all defined personas are `unused` |
| `verify-report.json` absent | `inputs.ac_verification` is `null` |
| `review-state.json` is a list, not a dict | `reviewed` falls back to `{}` (guarded by `isinstance`) |
| Clone resets mtimes after a review | mtime may read newer than `last_reviewed`, over-reporting `needs_review` (conservative; safe) |
| Text format requested | Prints `needs_review (n): ...`, persona defined/unused line, counts, and the ac line if present |

> **Minimum edge cases:** 8 for API stories, 5 for others

---

## Test Scenarios

- [ ] Artifact with later mtime than `last_reviewed` reports `needs_review: true`
- [ ] Artifact with no review-state entry reports `needs_review: true`
- [ ] `needs_review` top-level list is sorted and matches the per-key flags
- [ ] Project docs and every artifact type appear in the staleness map
- [ ] Missing files are skipped, not errored
- [ ] `persona_usage.unused` = defined minus PRD-referenced
- [ ] `inputs.counts` tallies every artifact type
- [ ] `inputs.ac_verification` is null without a verify report, summed with one
- [ ] Malformed `review-state.json` degrades to empty, not a crash
- [ ] `prep` is the only subcommand; the script writes nothing

> **Minimum test scenarios:** 8 for API stories, 6 for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| [US0002](US0002-verify-ac-gate.md) | Data | `verify-report.json` feeds `inputs.ac_verification` | Ready |
| [US0004](US0004-status-hint.md) | Related | Both read `.local/review-state.json` for review currency | Ready |

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

- [ ] Reconcile `last_modified` signal (mtime vs git log) between the script and `reference-review.md` step 4. - Owner: Darren Benson

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Story extracted (brownfield) from scripts/review_prep.py |
