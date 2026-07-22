# EP0102: A filing path that never passes prose through a shell

> **Status:** Draft
> **Derived Point Total:** 5
> **Parent:** CR0384
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0384. Delivers the work CR0384 requested.

## Story Breakdown

- [ ] [US0305: file_finding accepts every field as data through a non-shell input path](../stories/US0305-file-finding-accepts-every-field-as-data-through.md)
- [ ] [US0306: Sweep the sibling filers for the same hazard](../stories/US0306-sweep-the-sibling-filers-for-the-same-hazard.md)

## Acceptance Criteria (Epic Level)

- [ ] A finding can be filed with no field passing through a shell: a --fields-file taking JSON, or reading a JSON document on stdin
- [ ] The documented and recommended path for an agent is the non-shell one, in reference-scripts.md and in the tool's own help
- [ ] A field arriving with an unbalanced backtick, a $( or a trailing backslash is reported rather than stored silently, so a mangled filing is visible at file time instead of being discovered when somebody reads the artefact
- [ ] A test files a finding whose Steps section contains backticks, a $(...) form and the literal text of a destructive git command, then reads the artefact back and asserts the stored text is character-for-character what was supplied
- [ ] The same test asserts no side effect occurred: the repository index and HEAD are unchanged after the filing

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
