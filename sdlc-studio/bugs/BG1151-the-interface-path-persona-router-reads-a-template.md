# BG1151: The interface-path persona router reads a template placeholder as a declared interface, cuts a row at an escaped pipe, leaves ./ unpinned, and disagrees with validate on overlap

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/templates/personas/persona-template.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, tools/tests/test_persona_coherence.py, changelog.d/BG1151.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1080 APPROVE by qa-seat-US1080-r1 (brief 7c3f6bee8af2): mutants M14 and M15 survive; the placeholder, escaped-pipe and overlap probes as described.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T03:58:01Z

## Summary

qa-seat-US1080-r1's APPROVE of US1080 (2026-11-01) left four low findings in the new interface routing. (1) persona-template.md:15 puts its example paths (`src/`, `bin/run`) in code spans inside the `{{optional ...}}` slot, and `persona_interface_paths` (`sdlc_md.py`:2825-2845) reads every whitespace-free span, so a card that keeps the placeholder declares src and bin/run; in a two-Primary cast this routes src/ units to the wrong Primary with no warning. (2) `_INTERFACE_ROW_RE` (`sdlc_md.py`:2820) stops at an escaped pipe in the Interface cell, losing the paths after it; the missing-interface warning does fire. (3) The `./` normalisation on card spans (`sdlc_md.py`:2842) and on Affects (artifact.py:368) is pinned by no test: dropping either survives every AC test. (4) validate.py:1291-1300 detects two Primaries sharing an interface by comparing the row text, while the mint compares the declared paths, so two cards with different prose and the same or nested paths pass validate and the overlap routes silently to the first Primary.

## Steps to Reproduce

1. Give a second Primary card the template's Interface row unfilled; mint an unnamed story with Affects src/app.py: it goes to that card, with no warning.
2. Write an Interface cell with an escaped pipe before the spans: the later spans are lost.
3. Drop removeprefix('./') at `sdlc_md.py`:2842 or artifact.py:368: every test stays green.
4. Give two Primaries the path src/ with different prose: validate passes.

## Proposed Fix

Treat a row still carrying `{{...}}` as undeclared (or take the example out of code spans). Let the row pattern step over `\|`. Pin the ./ normalisation on both sides. Have validate compare the declared paths, and report an exact or nested overlap.

## Acceptance Criteria

- [ ] **AC1** A card whose Interface row still carries the template's `{{...}}` slot is treated as declaring no interface, and the missing-interface warning names it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
- [ ] **AC2** An escaped pipe in the Interface cell does not end the row, so every span after it is read.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
- [ ] **AC3** Dropping the ./ normalisation on either side fails a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
- [ ] **AC4** validate reports two Primaries whose declared paths are equal or nested, whatever their prose.
  - **Verify:** pytest tools/tests/test_persona_coherence.py

## Impact

In a multi-Primary cast, stories can be minted against the wrong Primary without a warning.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
