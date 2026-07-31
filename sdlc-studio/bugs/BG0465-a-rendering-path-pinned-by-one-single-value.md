# BG0465: A rendering path pinned by one single-value assertion accepts a hardcoded constant, and a sweep that named handoff.py in its own Affects never touched it

> **Status:** Fixed
> **Verification depth:** functional (each half verified by replaying the reviewer's own mutant: `outside = 2` and the restored `split("-")[0]` idiom, both KILLED; anchors asserted unique, `__pycache__` purged, `python3 -B`, restored byte-identical; full skill suite green at 5588)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/provenance.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_provenance.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Closing full-diff review of RUN-01KYTKA1's thirteen delivered bugs (engineering seat, isolated worktree, 54 mutants, base ad989eea). BG0442=REJECT, BG0452=REJECT; the other eleven APPROVE.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two blocking findings against bugs this sprint had already marked Fixed.

BG0442 exists because a placement line printed a number that could not be falsified. Its repair computed the number correctly and its verifier then pinned the RENDERING path with one fixture and one single-value assertion, `assertIn("2 raised outside one", line)`. Replacing the call with the literal `outside = 2` survived all 623 tests of the module, at every scope the reviewer tried - the one true survivor of 54 mutants. The bug's own AC2 names this hazard in terms and places its control on the helper, which does discriminate; the defect was in the half AC3 owns.

BG0452 swept three hand-rolled `stem.split("-")[0]` id parses onto the shared reader. Its Summary named `handoff.py:711` as carrying the identical defect and its Proposed Fix committed to "sweep the other two call sites in the same slice". `handoff.py` and `test_handoff.py` are in its declared Affects. Neither was touched, the line still read `split("-")[0]`, and AC3 substituted a fourth site the bug had never named. `provenance.py:97,130` carried the same pattern.

Repairing the second exposed a third fact: `extract_record_id` covers `ARTIFACT_TYPES` and only those, so it returns None for a handoff, a retro or a review. Applying it to handoff.py replaced one defect with another, and the regression test caught it.

## Steps to Reproduce

```text
BG0442, the reviewer's mutant:
  sprint.py:4587  outside = _findings_outside_batches(root, spans)
               -> outside = 2
  SURVIVED all 623 tests of test_sprint.py, and its own verifier in isolation

BG0452, measured on the shipped tree:
  handoff.py:711        sdlc_md.norm_id(p.stem.split("-")[0])
  provenance.py:97,130  aid = p.stem.split("-")[0]
  a v3 key `HO-<ulid>-slug` parses to `HO`, so the id never matches

and the trap under the repair:
  extract_record_id('HO0001-a-run')  -> None
  extract_record_id('RETRO0086-x')   -> None
```

## Proposed Fix

Pin the rendering path with TWO fixtures whose counts differ, so a constant cannot satisfy both. One fixture and one assertion is not a test of a computed number, whatever the docstring beside it says.

Add `stem_record_id` to the shared library: the same two key schemas as `extract_record_id` but a generic type prefix, so families outside `ARTIFACT_TYPES` - handoffs, retros, reviews - have one idiom to reach for rather than a hand-rolled split each. Route handoff.py through it and provenance.py through `extract_record_id`, which is correct there because it walks `ARTIFACT_TYPES`.

## Acceptance Criteria

### AC1: BOTH numbers on the placement line move with their own input

- **Given** the line's two counts - findings raised at a batch boundary, and findings raised outside one - varied independently
- **When** the line is rendered
- **Then** each moves with its own input and neither stands in for the other, because pinning one leaves the other free to be a constant: hardcoding the out-of-batch count survived the whole module and hardcoding the in-batch count survived its own selector, the same defect twice on the two halves of one sentence
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::FindingPlacementIsMeasuredNotConstantTests::test_BOTH_rendered_numbers_move_with_their_own_input
- **Verified:** yes (2026-07-31)

### AC2: the handoff locator resolves both key schemas

- **Given** a v2 handoff key and a v3 `HO-<ulid>-slug` key
- **When** the document is located by id
- **Then** both resolve, because `split("-")[0]` yields the bare prefix `HO` for the v3 form and `extract_record_id` returns None for a family outside `ARTIFACT_TYPES` - so reaching for either alone is a defect, and the shared `stem_record_id` is the one idiom that answers for every family
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::RefreshReadsBothKeySchemasTests::test_a_v3_handoff_key_resolves_to_its_document
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed |
| 2026-07-31 | Claude Opus 5 | Both blocking halves repaired. AC3 (no `split("-")[0]` id parse remains) holds by census over the shipped scripts and is covered by AC2's mutation; `provenance.py` routes through `extract_record_id`, correct there because it walks `ARTIFACT_TYPES`. |
