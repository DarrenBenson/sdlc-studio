# EP0324: A lesson's Revalidated citations are checked against the tree and re-anchored when code moves

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0657
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0657. Delivers the work CR0657 requested.

## Story Breakdown

- [ ] [US1188: lessons revalidate with a citation check reports each Revalidated citation past the file's end or away from its symbol](../stories/US1188-lessons-revalidate-with-a-citation-check-reports-each.md)
- [ ] [US1189: The project lessons log's critic.py citations are re-anchored to the current tree and the reason on L-0370 is corrected](../stories/US1189-the-project-lessons-log-s-critic-py-citations.md)

## Acceptance Criteria (Epic Level)

- [ ] `lessons.py revalidate --check-citations` reports every Revalidated reason whose `path:line` citation points past the file's end, or whose named symbol is no longer within a few lines of the cited line.
- [ ] The re-validation guidance asks a reason to name the symbol beside each line, and the critic.py citations in L-0001 to L-0270 are re-anchored to the current tree.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
