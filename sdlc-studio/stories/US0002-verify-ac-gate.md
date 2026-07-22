<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US0002-verify-ac-gate.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->

# US0002: Executable AC verification with verify gate

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** AI Agent Executing the Skill
**I want** each acceptance criterion to carry a one-line `Verify:` expression I can run mechanically, with a machine-maintained `Verified:` state and a blocking gate before "Done"
**So that** a story is marked Done only when its ACs actually pass against the live codebase, not when a checkbox was ticked by hand

## Context

### Persona Reference

**AI Agent Executing the Skill** - uses verify_ac as the "Done" oracle; needs a deterministic pass/fail signal, not a self-assessment.
[Full persona details](../personas.md#ai-agent-executing-the-skill)

### Background

Through v1.5.0, ACs were Given/When/Then markdown with no executable backing, and ticked ACs regressed within a week. `scripts/verify_ac.py` parses each AC's `Verify:` line, runs it through a small DSL, and rewrites the AC's `Verified:` state in place. It writes `sdlc-studio/.local/verify-report.json`. When `require_ac_verification: true`, the Story Completion Cascade refuses to mark a story Done until every AC reports `Verified: yes`.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | Behaviour | verify_ac is the Done oracle; supports a blocking gate | A failing AC keeps the story In Progress |
| PRD | Security | `shell`/fallback verifiers run trusted, team-authored input only | Never verify a story whose AC block came from un-reviewed external content |
| PRD | Determinism | Verifiers must be re-runnable any time | Per-verifier `--timeout` (default 120s); cwd pinned to `--repo-root` |

---

## Acceptance Criteria

### AC1: The Verify-line DSL routes by first token

- **Given** an AC bullet `- **Verify:** <expression>`
- **When** the runner parses the expression, splitting on the first whitespace
- **Then** the leading token selects the verifier - `pytest <node>` runs `pytest -q <node>`; `jest <pattern>` runs `jest -t <pattern>`; `vitest <pattern>` runs `vitest run -t <pattern>`; `go <args>` runs `go test <args>` (shlex-split); `file <path>` runs `test -e <path>`; `grep <regex> <path>` runs `rg -q` when `rg` is on PATH else `grep -rqE`; `http METHOD URL -- <jq>` builds `curl -sf -X METHOD URL | jq -e '<jq>' > /dev/null`; `shell <cmd>` runs the rest with `shell=True`
- **And** an unrecognised expression falls back to `shell` (whole expression run through the shell), and an AC with no `Verify:` line is counted as `manual` and left untouched
- **And** the verifier passes only on subprocess exit code `0`
- **Verify:** grep "def _build_command" .claude/skills/sdlc-studio/scripts/verify_ac.py
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC2: Per-AC `Verified: yes/no` maintained in place

- **Given** a story file whose AC1 passes its verifier but currently shows `- **Verified:** no`
- **When** I run `python3 scripts/verify_ac.py run --story <path> --repo-root .` (apply mode, no `--dry-run`)
- **Then** the AC's `Verified:` line is rewritten to `- **Verified:** yes (<today UTC YYYY-MM-DD>)`, preserving the original indentation; if no `Verified:` line exists one is inserted after the `Verify:` line (or the last AC bullet)
- **And** an AC that currently shows `yes` but now fails is downgraded to `- **Verified:** no (<today>)` and counted as `stale`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunTests::test_apply_mode_updates_verified_state
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC3: Pass / fail / manual counts and `run` vs `--dry-run`

- **Given** a stories directory
- **When** I run `verify_ac.py run` (apply) or `verify_ac.py run --dry-run`
- **Then** per story a line prints `[APL]` or `[DRY]` `<name>: ac=<n> pass=<verified> fail=<failed> manual=<manual> changes=<changed>`, where `verified` counts ACs that passed this run, `failed` counts non-zero verifiers, and `manual` counts ACs with no `Verify:` line
- **And** under `--dry-run` no story file is modified and no report is written; under apply, files are written and the report is written
- **And** the process exits `1` if any AC failed across all stories, else `0`; with no stories found it prints `no stories found` and exits `2`
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --dir /tmp/nope-$$ ; test $? -eq 2
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC4: `.local/verify-report.json` shape

- **Given** an apply-mode run
- **When** the run finishes
- **Then** `sdlc-studio/.local/verify-report.json` is written with `generated_at` (ISO-8601 Z) and a `stories` map keyed by story id (filename minus `.md`); each entry has `ac_count`, `verified`, `failed`, `stale`, `manual`, `passed` (list of AC ids), and `failures` (each `{ ac, verifier, kind, exit_code, stderr, duration_ms }`)
- **And** `verify_ac.py report` re-prints the latest report; a failing `kind: invalid, exit_code: 2` means the expression could not be parsed, `exit_code: 127` means the tool is not on PATH, `exit_code: 124` means timeout
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RunTests::test_passing_story_reports_zero_stale
- **Verification target:** functional
- **Verified:** yes (2026-06-24)

### AC5: `require_ac_verification` gate aborts the completion cascade

- **Given** `require_ac_verification: true` in `sdlc-studio/config.yaml` (or `templates/config-defaults.yaml`; default `false`)
- **When** the Story Completion Cascade reaches its pre-flight verifier step before marking the story Done
- **Then** the story is refused transition to Done unless every AC reports `Verified: yes`; a story that fails the gate stays `In Progress` with the report pointing at the failing ACs (per `reference-verify.md#verify-gate`)
- **Verify:** manual with `require_ac_verification: true`, confirm the cascade refuses a Done transition while any AC reports `Verified: no` (markdown-cascade behaviour; CR0084 since made this a deterministic gate in `transition.py`)
- **Verification target:** functional
- **Verified:** manual

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- `scripts/verify_ac.py run` and `report`: the DSL, in-place `Verified:` maintenance, counts, dry-run, JSON report.
- The blocking gate contract consumed by the Story Completion Cascade.

### Out of Scope

- Authoring good verifiers (guidance lives in `reference-verify.md#verify-writing-good`).
- The cascade steps themselves (defined in `reference-outputs.md`).
- Running verifiers on externally-ingested AC bodies (forbidden by the trust boundary).

---

## Technical Notes

`parse_story` extracts AC blocks from `### ACn: Title` headings, tracking the `Verify:` line (preferred insertion anchor) and the `Verified:` line. `update_verified` clamps the insert index to file bounds (malformed markdown cannot IndexError) and inherits indentation. `run_verifier` captures stdout/stderr (last 4000 chars), catches `TimeoutExpired` (exit 124) and `FileNotFoundError` (exit 127). Verifier stdout/stderr is truncated to 500 chars in the report.

### API Contracts

```text
python3 scripts/verify_ac.py run [--dir sdlc-studio/stories] [--story PATH] [--dry-run]
                                 [--timeout 120] [--report sdlc-studio/.local/verify-report.json]
                                 [--repo-root .]
python3 scripts/verify_ac.py report [--report PATH] [--format {text,json}]

report JSON: { "generated_at", "stories": { <id>: { "ac_count", "verified", "failed",
               "stale", "manual", "passed": [...],
               "failures": [ { "ac", "verifier", "kind", "exit_code", "stderr", "duration_ms" } ] } } }
```

### Data Requirements

Reads `US*.md` story files; rewrites their `Verified:` lines in apply mode; writes `sdlc-studio/.local/verify-report.json`.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| AC has no `Verify:` line | Counted as `manual`; the `Verified:` line is not touched |
| AC passes, already `Verified: yes` | No file write for that AC; not counted as a change |
| AC fails, was `Verified: yes` | Downgraded to `no`, counted as `stale` (and a `change`) |
| `http` expression missing the ` -- ` separator | `kind: invalid, exit_code: 2` ("expected `METHOD URL -- <jq assertion>`") |
| `grep` with fewer than two tokens | `kind: invalid, exit_code: 2` ("grep: expected <regex> <path>") |
| Verifier tool absent from PATH | `kind: <kind>, exit_code: 127`, stderr = the FileNotFoundError message |
| Verifier exceeds `--timeout` | `kind: <kind>, exit_code: 124`, stderr `timeout` |
| `--dir` resolves to no story files | Prints `no stories found` on stderr, exit code 2 |
| `--story` path does not exist | Prints `skip: <path> not found`, continues with the rest |
| Story file ends with a newline | Trailing newline preserved on rewrite |

> **Minimum edge cases:** 8 for API stories, 5 for others

---

## Test Scenarios

- [ ] `pytest`, `jest`, `vitest`, `go`, `file`, `grep`, `http`, `shell` each build the documented command
- [ ] Unrecognised expression falls back to `shell`
- [ ] Passing AC upgrades `Verified: no` to `yes (<today>)` in apply mode
- [ ] Failing AC that was `yes` downgrades to `no` and counts as `stale`
- [ ] `--dry-run` writes neither the story file nor the report
- [ ] Missing `Verify:` line counted as `manual`
- [ ] Report JSON has the documented `stories` / `failures` shape
- [ ] Exit code 1 on any failure, 0 on all pass, 2 on no stories
- [ ] `http` without ` -- ` yields `kind: invalid, exit_code: 2`
- [ ] Indentation preserved when an existing `Verified:` line is rewritten

> **Minimum test scenarios:** 8 for API stories, 6 for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| [US0001](US0001-reconcile-census-autofix.md) | Related | `reconcile --verify` / `--scope verify` invokes this runner | Ready |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| Python 3.10+ | Runtime | Available |
| `pytest` / `jest` / `vitest` / `go` / `curl` / `jq` / `rg` | Tool (only those a Verify line invokes) | Soft - install as needed |

---

## Estimation

**Story Points:** 8
**Complexity:** High

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

Not applicable – story does not change runtime behaviour. The script only rewrites `Verified:` lines and writes a report under `.local/`.

---

## Open Questions

- [ ] None - behaviour fully extracted from `scripts/verify_ac.py`. - Owner: Darren Benson

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Story extracted (brownfield) from scripts/verify_ac.py |
