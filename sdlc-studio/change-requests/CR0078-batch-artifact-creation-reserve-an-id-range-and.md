# CR-0078: batch artifact creation - reserve an ID range and wire many stories in one pass

> **Status:** Proposed
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

`new` creates one artifact per invocation. A greenfield start commonly needs tens of
stories at once (the source run mapped 33 stories across 7 epics). One-at-a-time
creation forces either N serial subprocess calls or - what the agent actually reached
for - parallel sub-agents purely to coordinate id allocation, which is *"costly and
risk[s] inconsistency"*. Add a batch path so the tool's core value (collision-free
ids) extends to bulk creation in one deterministic pass.

> The batch path is the substrate for **RFC0019**'s author phase: it lets delegated
> sub-agents fill content into pre-wired scaffolds rather than coordinate ids and links.

## Problem

From the source run (verbatim): *"That's 33 stories total across 7 epics... Rather
than writing each story file manually, I'll parallelize by delegating to sub-agents -
one per epic, each given... ID ranges. They'll author full story files without
touching indexes, then I'll build the index myself. Sub-agents are costly and risk
inconsistency though."*

The agent only spun up sub-agents to avoid id collisions across concurrent writers -
a coordination cost the tool should absorb. Manual id-range hand-out is exactly the
collision class LL0002 warns about, and the per-epic indexes are still hand-built
afterwards.

## Proposed Changes

### Item 1: `new --batch <spec>` with a reserved contiguous id range

**Priority:** Medium
**Effort:** 3

Accept a batch spec (JSON, or repeated `--title`) describing many artifacts of one
type. Allocate a single contiguous id block up front (reserve N from `_next_number`),
render each file, append all index rows in one read-modify-write of the index, and -
for stories - wire every entry into its parent epic's Story Breakdown in one pass.
All-or-nothing: if any id collides or any epic is missing, write nothing and report.
`--dry-run` previews the full id map and wiring.

Example:

```bash
new --batch stories.json --root .
# stories.json: [{"epic":"EP0001","title":"REST conventions"}, ...]
```

### Item 1b: `--batch` implies `--template full`

**Priority:** Medium
**Effort:** 1

Batch is the mode where the full template's only cost (verbosity) disappears - an *agent*
fills the file, not a human typing one - and its benefit (a guaranteed section contract)
is highest. So `--batch` defaults to `--template full` (CR0077 Item 2), with `--minimal`
as the explicit opt-out. Evidence: a greenfield agent fanned the full template to 7
sub-agents precisely to guarantee every section; an audit of the 33 resulting files found
a **byte-identical level-2 heading signature** - the uniformity came from the full
template being the shared contract. The minimal scaffold stays the default only for the
single-story human path.

### Item 2: Reuse the batch path from `story`/`project` generation

**Priority:** Low
**Effort:** 1

Where `story` / `project implement --from stories` generate multiple stories for an
epic, route them through the batch path so the id reservation and single-pass index
build are shared rather than re-implemented.

## Acceptance Criteria

- [ ] `new --batch <spec> --type story` creates all N files with a contiguous id
      range, one index-write, and all epic Story-Breakdown links wired in one pass
- [ ] the batch is atomic: a single missing epic or id collision writes nothing and
      reports the offending entries (no partial state)
- [ ] `--dry-run` prints the full allocated id map and the planned epic wiring without
      writing
- [ ] `--batch` defaults to `--template full` (CR0077 Item 2); `--minimal` opts out
- [ ] concurrent-collision guard documented per LL0002 (batch reserves before writing)
- [ ] unit tests cover: happy-path batch, atomic rollback on a bad epic, dry-run id
      map; CHANGELOG `[Unreleased]` entry in the same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Confirmed by a greenfield agent ("yes, strongly"): pre-wired scaffolds flip delegated agents from "create file" to "fill file", collapsing the consistency risk to content-only (~80% of the worry was structural) |
