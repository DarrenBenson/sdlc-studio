# EP0330: Agents find a symbol's line range from the repo map and from their brief, without searching

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0678
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0678. Delivers the work CR0678 requested.

## Story Breakdown

- [ ] [US1208: Repo map outline and where print each symbol's line range from the index and refuse a stale index](../stories/US1208-repo-map-outline-and-where-print-each-symbol.md)
- [ ] [US1209: The lane brief lists the symbols the unit's criteria name in each Affects file, with line ranges](../stories/US1209-the-lane-brief-lists-the-symbols-the-unit.md)
- [ ] [US1210: The critic brief names the enclosing symbol and its line range for each diff hunk](../stories/US1210-the-critic-brief-names-the-enclosing-symbol-and.md)

## Acceptance Criteria (Epic Level)

- [ ] `repo_map.py outline <file>` prints each symbol's name, kind and start-end line range and `repo_map.py where <symbol>` prints its file and range, both served from the existing index, and a stale index is rebuilt or refused rather than printing wrong lines.
- [ ] `sprint.py lane brief` lists, for each Affects file, the symbols the story and its criteria name (or the top symbols `query` ranks) with their line ranges.
- [ ] `critic.py brief` names the enclosing symbol and its line range for each diff hunk.
- [ ] Before and after: search-only calls per builder on the benchmark (US1128) fall from run six's 11.9 (166 over 14) to 8 or fewer.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
