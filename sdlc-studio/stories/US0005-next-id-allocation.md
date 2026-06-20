<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US0005-next-id-allocation.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# US0005: Deterministic next-ID allocation

> **Status:** Ready
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** AI Agent Executing the Skill
**I want** the next free artifact ID for a type computed deterministically, optionally checking origin/main
**So that** I never scan files and guess a number, and two collaborators on different branches do not both allocate the same ID

## Context

### Persona Reference

**AI Agent Executing the Skill** - creates new epics, stories, CRs and must pick a fresh, non-colliding ID every time.
[Full persona details](../personas.md#ai-agent-executing-the-skill)

### Background

`scripts/next_id.py` implements doctrine rule 13 (cross-repo numbering). `allocate` scans local artifact files for the highest used number and prints the next zero-padded 4-digit ID. With `--remote` it also reads the highest number already on `origin/main` via a read-only `git ls-tree` (no fetch - the caller fetches first), so a teammate's just-merged ID is not re-used.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
| --- | --- | --- | --- |
| Epic | Behaviour | Deterministic, collision-avoiding allocation | `next = max(local, remote) + 1` |
| Epic | Architecture | Pure stdlib, read-only | `git ls-tree` only; no fetch, no write |
| PRD | Determinism | Same disk + same origin/main -> same next ID | IDs are 4-digit zero-padded per type prefix |

---

## Acceptance Criteria

### AC1: `allocate --type <type>` prints the next zero-padded ID

- **Given** a type whose highest local artifact number is N (or no files, N = 0)
- **When** I run `python3 scripts/next_id.py allocate --type story --root .`
- **Then** it prints `US{N+1:04d}` on stdout (e.g. an empty `stories/` yields `US0001`), and the prefix is taken from the type: `epic`->`EP`, `story`->`US`, `plan`->`PL`, `bug`->`BG`, `cr`->`CR`, `rfc`->`RFC`, `test-spec`->`TS`, `workflow`->`WF`
- **And** `--type` is required and constrained to those eight choices
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/next_id.py allocate --type story | grep -qE "^US[0-9]{4}$"
- **Verification target:** functional
- **Verified:** yes (2026-06-20)

### AC2: Collision avoidance is max-plus-one, not first-gap

- **Given** local story files `US0001`, `US0002`, `US0007` (a gap at 3-6)
- **When** I `allocate --type story`
- **Then** it returns `US0008` (one above the maximum), never re-using the gap, so a deleted-and-recreated ID is never re-issued
- **And** IDs are de-duplicated and parsed via the 4-digit suffix, so `CR0007` and `CR-0007` count as the same number
- **Verify:** grep "next_num = base + 1" .claude/skills/sdlc-studio/scripts/next_id.py
- **Verification target:** functional
- **Verified:** no

### AC3: `--remote` consults origin/main read-only

- **Given** `--remote` is passed
- **When** allocation runs
- **Then** it runs `git ls-tree -r --name-only origin/main -- <type-dir>` (no network fetch), takes the max remote number, and allocates above `max(local_max, remote_max)`
- **And** when origin/main is missing or git is unavailable, `remote_available` is `false` and allocation falls back to the local maximum without error
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/next_id.py allocate --type epic --remote --format json | python3 -c "import json,sys; assert 'remote_available' in json.load(sys.stdin)"
- **Verification target:** functional
- **Verified:** yes (2026-06-20)

### AC4: Output shape - text vs JSON, and the ahead-of-local warning

- **Given** an allocation
- **When** I add `--format json`
- **Then** the object is `{ "type", "prefix", "local_max", "remote_max", "remote_available", "next_id", "warning" }`; in text mode only the ID is printed to stdout
- **And** when `--remote` finds origin/main strictly ahead of local, `warning` carries `origin/main is ahead of local for <type> (<prefix><remote_max> > <prefix><local_max>); allocating above the remote maximum` - printed to stderr in text mode, embedded in JSON otherwise; the exit code is `0`
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/next_id.py allocate --type story --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert set(d)>={'type','prefix','local_max','remote_max','remote_available','next_id','warning'}"
- **Verification target:** functional
- **Verified:** yes (2026-06-20)

### AC5: `scan` lists every ID in use for a type

- **Given** I want to audit existing IDs
- **When** I run `python3 scripts/next_id.py scan --type story --format json`
- **Then** the object is `{ "type", "ids": [<sorted zero-padded IDs>], "count" }`; in text mode each ID prints on its own line and a `# <count> <type>(s)` summary goes to stderr
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/next_id.py scan --type story --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'ids' in d and 'count' in d"
- **Verification target:** functional
- **Verified:** yes (2026-06-20)

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- `scripts/next_id.py allocate` (with `--remote`) and `scan`: deterministic max-plus-one allocation, zero-padded IDs, origin/main check, JSON and text output.

### Out of Scope

- Fetching from origin (the caller runs `git fetch` first; this script never touches the network).
- Writing the new artifact file (Claude does that after allocation).

---

## Technical Notes

`local_ids` extracts the record ID from each artifact file stem and its 4-digit numeric suffix (`id_number`), returning a sorted unique list. `remote_ids` runs `git ls-tree` with `check=False`, returning `([], False)` on `FileNotFoundError` (no git) or non-zero exit (no origin/main). `base = max(local_max, remote_max)`; `next_id = f"{prefix}{base + 1:04d}"`. The warning fires only when `--remote` and `remote_available` and `remote_max > local_max`.

### API Contracts

```text
python3 scripts/next_id.py allocate --type {bug,cr,epic,plan,rfc,story,test-spec,workflow}
                                    [--remote] [--root ROOT] [--format {text,json}]
python3 scripts/next_id.py scan     --type <type> [--root ROOT] [--format {text,json}]

allocate JSON: { "type", "prefix", "local_max", "remote_max", "remote_available", "next_id", "warning" }
scan JSON:     { "type", "ids": [...], "count" }
```

### Data Requirements

Reads `<type-dir>/*.md` artifact files; with `--remote` reads `origin/main` via `git ls-tree`. Writes nothing.

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
| --- | --- |
| No files for the type | `local_max = 0`; allocates `<prefix>0001` |
| Gap in the local sequence (1,2,7) | Allocates 8 (max+1); the gap is never re-issued |
| `CR0007` and `CR-0007` both present | Counted as the same number 7 (dash-insensitive suffix parse) |
| `--remote` but no origin/main | `remote_available: false`; falls back to local max; no error |
| git not installed | `FileNotFoundError` caught; `remote_available: false` |
| origin/main ahead of local | `warning` set; allocates above remote; exit 0 |
| `--type` omitted or unknown | argparse error (required, constrained choices), exit 2 |
| Unexpected exception | `error: <msg>` on stderr, exit code 1 |

> **Minimum edge cases:** 8 for API stories, 5 for others

---

## Test Scenarios

- [ ] Empty type directory allocates `<prefix>0001`
- [ ] Highest local + 1 is allocated (gaps not re-used)
- [ ] Each type maps to its correct prefix
- [ ] `--remote` allocates above `max(local, remote)`
- [ ] Missing origin/main yields `remote_available: false` and local fallback
- [ ] Ahead-of-local case sets the `warning` string and still exits 0
- [ ] `CR0007` and `CR-0007` counted once
- [ ] JSON allocate object has all seven keys
- [ ] `scan` lists sorted IDs with a count
- [ ] Missing/unknown `--type` exits with argparse error code 2

> **Minimum test scenarios:** 8 for API stories, 6 for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
| --- | --- | --- | --- |
| None | -- | -- | -- |

### External Dependencies

| Dependency | Type | Status |
| --- | --- | --- |
| Python 3.10+ | Runtime | Available |
| `git` (only for `--remote`) | Tool | Soft - falls back to local if absent |

---

## Estimation

**Story Points:** 3
**Complexity:** Low

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

Not applicable – story does not change runtime behaviour. The script is read-only and writes nothing.

---

## Open Questions

- [ ] None - behaviour fully extracted from `scripts/next_id.py`. - Owner: Darren Benson

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Story extracted (brownfield) from scripts/next_id.py |
