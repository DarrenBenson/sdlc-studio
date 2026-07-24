# CR-0417: a writer's --fields-file allows only its prose keys, so an invocation setting metadata must be split across a document and flags: lessons add takes --tags, --epic and --wave that its own fields-file refuses

> **Status:** Proposed
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py,.claude/skills/sdlc-studio/scripts/file_finding.py
> **Priority:** Medium
> **Type:** Feature
> **Size:** S

## Summary

{{what changes and why}}

## Impact

{{who this affects and what breaks}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |

## Detail

Hit recording a lesson through the very path this sprint built. `lessons add` accepts `--tags`,
`--epic`, `--wave`, `--origin` and `--validity-days` alongside `--title` and `--body`, but its
`--fields-file` allows only `title` and `body`, so the document was refused:

```text
error: --fields-file lesson.json carries unknown field(s): tags - known fields are title, body
```

The refusal itself is right, and is the loader working as designed: an unknown key is refused
rather than silently dropped, which is the whole reason the loader exists. The friction is that
one logical invocation now has to be split across two surfaces - prose in a document, metadata on
the command line - and the author has to know which is which before writing either.

That also erodes the benefit. The fields-file exists so a whole invocation can be re-run,
committed as evidence and diffed; a half-invocation that needs remembered flags beside it is none
of those things.

Not a defect in the loader's contract - `allowed` is per-writer and deliberately narrow. The
question is whether a writer's allowed set should cover every field it accepts, with only the
PROSE ones hazard-checked, so the document is the whole call.

## Impact of the split

Small but recurring: every writer that gained `--fields-file` this sprint has non-prose flags
beside it. The safe path is the one with the extra step, which is the wrong way round for a path
this project wants people to prefer.

## Acceptance Criteria

- [ ] AC1: a writer's fields-file accepts every field its CLI accepts
- **Given** a writer whose parser takes prose fields and metadata fields
- **When** a fields-file supplies any of them
- **Then** all are accepted, so one document is the whole invocation - while the hazard check still applies only to the PROSE fields, which are the ones a shell can mangle
- **Verify:** manual

- [ ] AC2: an unknown key is still refused
- **Given** a document carrying a key the writer's CLI does not accept at all
- **Then** it is still refused by name - widening the allowed set must not become accepting anything
- **Verify:** manual
