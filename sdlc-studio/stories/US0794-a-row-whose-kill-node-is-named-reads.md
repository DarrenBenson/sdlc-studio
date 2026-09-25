# US0794: A row whose kill node IS named reads `killed`, unchanged - the paired control

> **Status:** Superseded
> **Closes with:** US0936 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Delivers:** CR0554
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0241
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A row whose kill node IS named reads `killed`, unchanged - the paired control
**So that** CR0554 is delivered by work that can be planned and checked

## Acceptance Criteria

> **Ungroomed - acceptance criteria are a grooming placeholder** - author each criterion and its Verify check against this story's slice while grooming, before it is planned to Done. Shape: `templates/core/story.md`. Verifier guidance: `reference-verify.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | audit ruling | RUN-01M306PY sweep, US0854 AC2: ruled GENUINELY DISTINCT, not a duplicate. US0793 asserts the defect case - a row whose ledger kill node is not named by its criterion's `Verify:` selector reads `killed-elsewhere` - and US0794 asserts the PAIRED POSITIVE CONTROL, that a row whose kill node IS named still reads `killed`. This project's own testing practice requires a positive control beside each refusal, so the two are one criterion's two halves. They share four files and 50% of their wording because that is what a control IS; the detector is right about the surface and wrong about the conclusion. Recorded on BG0721. |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0921 ships - planning: SUPERSEDED - mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| 2026-09-25 | sdlc-studio BG0772 | Closes with re-pointed from US0921 to US0936 (D0264): US0921 was split and US0936 carries the ledger deletion this item waits on |
| 2026-09-25 | sdlc-studio US0936 | Superseded under D0264: its closing story US0936 is Done (BG0772) |
