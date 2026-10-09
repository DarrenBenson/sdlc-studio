# EP0280: A recorded review verdict is what the reviewer wrote, bound to its bytes and to the agent that wrote it

> **Status:** Draft
> **Parent:** CR0615
> **Derived Point Total:** 23
> **Parent:** CR0619
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0619. Delivers the work CR0619 requested.

## Story Breakdown

- [ ] [US1011: A review brief names the file the reviewer writes its verdict to](../stories/US1011-a-review-brief-names-the-file-the-reviewer.md)
- [ ] [US1012: A recorded verdict is bound to the bytes of the file its brief issued](../stories/US1012-a-recorded-verdict-is-bound-to-the-bytes.md)
- [ ] [US1013: A verdict that differs from its issued file, or was recorded before, is named](../stories/US1013-a-verdict-that-differs-from-its-issued-file.md)
- [ ] [US1014: A recorded verdict names the agent that was briefed and wrote it, read from the harness transcript](../stories/US1014-a-recorded-verdict-names-the-agent-that-was.md)
- [ ] [US1015: A verdict written by the context that edited the unit is a self-review, whatever seat it names](../stories/US1015-a-verdict-written-by-the-context-that-edited.md)
- [ ] [US1016: critic.py brief --rejoinder with no file quotes the seat's standing REJECT from the ledger](../stories/US1016-critic-py-brief-rejoinder-with-no-file-quotes.md)

## Acceptance Criteria (Epic Level)

- [ ] The brief names a verdict file path for the reviewer to write itself, record reads that file and stores a hash of its exact bytes (and the reviewer's session id when known) on the ledger row
- [ ] record warns when the verdict file was last written by a process other than the reviewing session, or when the recorded text differs from the reviewer-written file
- [ ] A verdict whose recording session is the session that authored the unit is refused, or recorded and shown on the ledger as a self-review, whatever seat name it carries

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
