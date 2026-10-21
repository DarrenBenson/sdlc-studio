# CR-0640: A reference page edited without regenerating its reading guide passes every commit lane and is found only by the full suite at push

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .githooks/pre-commit, tools/tests/test_precommit_reading_guides.py
> **Date:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T14:02:33Z

## Summary

Each `reference-*.md` carries a reading guide that `docgen reading-guides` derives from it, and `test_lean_docs_tell_truth.py` fails the full suite when one has drifted. No commit-time lane runs `docgen reading-guides --check` when a reference page is staged, so the drift is found only by the push's full suite. It happened twice in one session: 978083c6 had to regenerate after an earlier change, and on 2026-10-13 BG1003's one-paragraph edit to reference-review.md turned the gate host's full suite red (`docgen reading-guides: 1 drift item(s) over 26 reference(s)`), costing a ten-minute re-run.

## Impact

Anyone editing a reference page: the drift costs a full-suite run to find, and a regenerate-and-rerun to clear.

## Acceptance Criteria

- [ ] Given a staged change to a reference page whose reading guide it leaves stale, when the pre-commit hook runs, then a cheap lane refuses and names `docgen reading-guides` as the fix
- [ ] Given the guide regenerated, when the hook runs again, then the lane passes

## Triage (2026-10-21)

Kept (D0387). To plan it:

- Refine needs: one story, Points 2
- Verify into the new tools/tests/test_precommit_reading_guides.py (stale guide refused naming `docgen reading-guides`; regenerated guide passes)
- LL0056: say what it retires; the cheaper route is BG1000's census-subject selection selecting a reading-guide drift test for a staged reference page, with no new lane
- Persona: Rowan Achterberg (.githooks, D0379)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Raised |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
