# CR-0199: status backlog: deterministic non-terminal census grouped by type and status

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** tooling

## Summary

"What is left in the backlog?" has no deterministic answer today. The `/sdlc-studio
status` dashboard renders per-type breakdowns, but the model assembles them from index
reads every time - token-expensive and re-derived per session. The script tier
(`status.py`) offers only `pillars` (counts) and `hint` (next action). Field evidence
from this repo's own operation (2026-07-08): asked for the backlog, the agent shortcut
the dashboard, hand-parsed `_index.md` with grep, and missed the `Complete` status on
the first pass - producing a wrong backlog list. Hand-rolling what a script should wire
is the exact failure ADR-002 exists to prevent.

Add `status.py backlog`: census non-terminal artifacts from the files (not the index -
files are truth), grouped by type then status, with id, title, priority and epic;
`--format json|text`; a `--type` filter. The dashboard workflow consumes it instead of
re-deriving; agents and operators get the one-shot answer. Terminal-status vocabulary
comes from the existing per-type status vocab (single source, no duplicated list).

## Acceptance Criteria

- [ ] `status.py backlog` lists non-terminal artifacts per type (CR, story, epic, bug,
      RFC) grouped by status, from a file census
- [ ] Terminal statuses resolve from the shared status vocabulary, not a hardcoded list
      in the new command
- [ ] `--format json` is stable for tooling; `--type cr` filters
- [ ] help/status.md and reference-scripts.md document it; the dashboard workflow points
      at it for the breakdown section
- [ ] Unit tests: mixed-status fixture, empty backlog prints explicitly, vocab-driven
      terminal detection

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed from the backlog-question miss at v4 readiness review |
