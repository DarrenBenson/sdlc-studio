# BG0038: integrity requires a Story link on test-specs, breaking epic-scoped test-specs

> **Status:** Open
> **Severity:** high
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

integrity.py REQUIRED_LINKS lists test-spec as needing BOTH Epic and Story links, so an epic-scoped test-spec (one covering a whole epic, no single story) is flagged missing-required. But reference-test-spec.md explicitly defines epic-scoped specs: an epic link with no story field, or story listing multiple. This is a direct contradiction - CR0096 makes an epic-scope test-spec a hard requirement at epic scope and CR0110 authors it at design, so the very artifact the skill mandates fails its own integrity check. A field agent breaking down EP0005 hit this on TS0005 (covering 7 stories) and had to hack a multi-story Story field to pass.

## Steps to Reproduce

1. Author an epic-scoped test-spec (Epic link, covers multiple stories, no single Story metadata field) - the kind reference-test-spec.md#epic-scoped-coverage describes and CR0096 requires at epic scope. 2. Run integrity.py check. 3. It reports missing-required Story on the test-spec, even though epic-scoped specs are defined to omit the single story field. Repro: TS0005 covering EP0005 US0020-US0026.

## Proposed Fix

Make the Story link conditional for test-specs: require Epic always; require Story only for a story-scoped spec, not an epic-scoped one (Epic link present + epic-scoped per reference-test-spec.md detection = Story not required). Simplest: drop Story from REQUIRED_LINKS[test-spec] (keep Epic), since a test-spec always carries an Epic and may be story- or epic-scoped. Unit test: an epic-scoped TS (Epic, no single Story) passes integrity; a TS with neither Epic nor Story still flags. CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Filed |
