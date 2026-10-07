# BG0959: The engagement floor rejects a ULID adopt_after cutoff and tells you to set a sequential one

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py, changelog.d/BG0959.md
> **Evidence:** Field report, 2026-10-07, planning Sprint 0 on sdlc-studio-lens. engagement_floor.py check printed the adopt_after remedy for 13 Fixed ULID bugs. Reproduced at HEAD: `_mode_and_cutoff` on a config of `adopt_after: BG-01KXB3QF` raises ValueError.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T08:40:26Z

## Summary

On a schema-v3 project the engagement floor's own remedy cannot be followed. conformance.adopt_after already parses a ULID cutoff (`sdlc_md.parse_cutoff` with allow_ulid, and `sdlc_md.cutoff_exempts`, US0974). The floor calls parse_cutoff without allow_ulid and exempts only when id_number(rid) is less than or equal to the cutoff. A ULID has no id number, so the call raises ValueError: adopt_after cutoff is not a number or id: 'BG-01KXB3QF'. The printed remedy names only a bare integer or a prefixed sequential id (CR0238). The 13 shipped lens bugs (BG-01KX8B04 through BG-01KXB3QF) cannot be grandfathered; each needs its own waiver.

## Steps to Reproduce

1. Write sdlc-studio/.config.yaml with engagement_floor.adopt_after set to BG-01KXB3QF. 2. Call engagement_floor._mode_and_cutoff on that root. 3. It raises ValueError and names a bare integer or a prefixed id. id_number('BG-01KXB3QF') is None.

## Proposed Fix

Parse the floor's cutoff with allow_ulid and exempt with cutoff_exempts, the same comparator conformance uses. An earlier ULID bucket is exempt, the cutoff id itself is exempt, a later bucket is judged. Teach REMEDY_CUTOFF a v3 id as a legal example. Do not treat a numeric cutoff and a ULID cutoff as the same comparison.

## Acceptance Criteria

- [ ] **AC1** A ULID `adopt_after` exempts an earlier-bucket unit and still judges a later one, and does not raise
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CutoffTests::test_id_at_or_below_cutoff_is_exempt_for_a_v3_ulid
- [ ] **AC2** `engagement_floor.py check` on a schema-v3 fixture whose `adopt_after` is a ULID exits without a traceback, grandfathers the earlier-bucket shipped units and still reports a later one
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CutoffTests::test_check_honours_a_ulid_cutoff_through_the_cli
- [ ] **AC3** A numeric `adopt_after` judges exactly as today, and the remedy text names a v3 id as a legal cutoff beside the integer and the prefixed sequential id
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::CutoffTests::test_a_numeric_cutoff_is_unchanged_and_the_remedy_names_a_v3_id

## Triage

- Reproduced at fb1ce886. Already in the code: US0974 (2026-10-01) taught `conformance` ULID cutoffs through `sdlc_md.parse_cutoff(allow_ulid=True)` and `sdlc_md.cutoff_exempts`; the floor (CR0229, 2026-07-13) was never moved onto them. Not a regression of a recent run.
- Re-sized 3 -> 2: one parse call, one comparator and one remedy string, with tests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Grok 4.7 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at fb1ce886 (`_mode_and_cutoff` raises ValueError on BG-01KXB3QF); the ULID helpers live in `sdlc_md`, not `conformance`; 3 -> 2 points; a CLI criterion and a numeric positive control added; changelog fragment added to Affects |
