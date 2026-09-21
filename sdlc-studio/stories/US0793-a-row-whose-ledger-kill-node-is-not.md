# US0793: A row whose ledger kill node is not named by its criterion's `Verify:` selector reads `killed-elsewhere`

> **Status:** Draft
> **Delivers:** CR0554
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0241
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A row whose ledger kill node is not named by its criterion's `Verify:` selector reads `killed-elsewhere`
**So that** CR0554 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | audit ruling | RUN-01M306PY sweep, US0854 AC2: ruled GENUINELY DISTINCT, not a duplicate. US0793 asserts the defect case - a row whose ledger kill node is not named by its criterion's `Verify:` selector reads `killed-elsewhere` - and US0794 asserts the PAIRED POSITIVE CONTROL, that a row whose kill node IS named still reads `killed`. This project's own testing practice requires a positive control beside each refusal, so the two are one criterion's two halves. They share four files and 50% of their wording because that is what a control IS; the detector is right about the surface and wrong about the conclusion. Recorded on BG0721. |
