# CR-0308: verify_ac run --story should accept a story id (it silently means --file): the natural first call 'run --story US0177' fails with 'no story file'

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16

## Summary

`verify_ac.py` run exposes '--story, --file STORY' (a path) AND '--id ID' (a story id). Observed 2026-07-16: 'run --story US0177' fails with 'no story file at US0177' before 'run --id US0177' succeeds. Sibling scripts spell it the other way (transition.py set --id, `sprint_report.py` show --id), so the muscle memory is id-shaped; a flag named --story that refuses a story id is a small but recurring paper cut. Deterministic fix: when the --story value matches the id shape and is not an existing path, resolve it as an id (or fold both into one flag that disambiguates).

## Impact

Every agent or operator verifying one story reaches for --story USxxxx first; the flag is an alias of --file, so the natural call fails and the working form (run --id) is only discoverable via --help.

## Acceptance Criteria

- [ ] `verify_ac` run --story US0177 resolves the story by id when the value matches ^(US|BG)\d+$ and no such file exists; existing path behaviour unchanged
- [ ] Help text documents the disambiguation; a value that is neither a real path nor a resolvable id fails naming both attempts

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
