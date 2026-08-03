# BG0506: a repeated single-valued metadata field is accepted, read first-wins, and corrected first-only - so a gate can read one of two contradictory claims

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, sdlc-studio/change-requests/CR0138-mixed-batch-sprint-tranches-bugs-plus-crs-first-class.md, sdlc-studio/change-requests/CR0218-the-converged-seat-home-retire-amigos-precedence-one.md, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Found while checking a premise before filing it: EP0174 carries two `Parent:` lines, which turned out to be the DESIGNED multi-parent convention (`parent_refs` reads every line, `refine --into` writes one per request, 23 live epics use it, EP0071 has twelve). Scanning the same way for every other repeated field found two that are not: CR0138 with two `Created-by:` lines and CR0218 with two `Verification depth:` lines. Reproduced through the shipped entry points against a throwaway fixture at HEAD 32648f1f.
> **Created:** 2026-08-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sdlc_md.extract_field` matches with `re.search`, so a repeated `> **Name:** value` line is read FIRST-WINS, and `transition._set_field` substitutes with `count=1`, so a correction rewrites the first and leaves the rest standing. Nothing refuses the shape: `validate.py check` over a fixture holding two `Verification depth` lines reports `checked=1 errors=0 warnings=0`.

That matters because the field is a gate input. `transition.py set BG9001 Fixed` over that fixture refused with "depth is smoke; Fixed requires functional+" - reading the first line while a `soak` line sat immediately below it. Reverse the order and the gate passes on a claim the artefact itself contradicts, with the losing line still reading like live metadata to a human.

`Parent:` is plural BY DESIGN and must stay that way, so this is not a blanket no-duplicates rule: `parent_refs` reads every `Parent:` line because a shared batch epic delivers more than one request, and 23 live epics rely on it. A guard has to know which fields are single-valued, which is the part that needs writing rather than the detection.

## Steps to Reproduce

1. Create a fixture bug carrying two `> **Verification depth:**` lines, `smoke` first and `soak` second.
2. `python3 validate.py --root <fixture> check` -> `checked=1 errors=0 warnings=0`. Nothing objects.
3. `python3 -c "...sdlc_md.extract_field(text, 'Verification depth')"` -> `'smoke (the first line)'`. The second line is invisible.
4. `python3 transition.py --root <fixture> set BG9001 Fixed` -> blocked with "depth is smoke; Fixed requires functional+", so the gate's verdict came from the first of two contradictory claims.
5. `transition.annotate(root, 'BG9001', 'Verification depth', 'functional (corrected)')` -> the file now holds `functional (corrected)` AND the original `soak` line. The correction did not correct the record.
6. In the live tree, `CR0218` carries two `Verification depth:` lines with different evidence, and `CR0138` two `Created-by:` lines with different provenance.

## Proposed Fix

Give `validate.py check` a lane that refuses a repeated metadata field, driven by an explicit set of fields that are plural by design - today `Parent:` alone. Deriving the exemption from a hard-coded list is the point: a blanket duplicate check false-flags all 23 multi-parent epics, and an exemption inferred from "whatever is currently repeated in the corpus" would exempt exactly the two defects this finding names. The set belongs beside `PARENT_FIELD` in `sdlc_md`, where the plural reader already lives, so a future plural field is declared in one place rather than discovered by a guard reddening.

Consider whether `_set_field`'s `count=1` should become a refusal rather than a silent first-only write: with the lane in place a duplicate cannot enter the tree, but the writer is the surface that would have to be safe if one ever did.

Repair the two live records as part of it - `CR0218`'s two depth records describe different verification runs and need reconciling into one line rather than deleting whichever is second, and `CR0138`'s second `Created-by:` is a backfill note that belongs in the Revision History.

## Acceptance Criteria

- [ ] **AC1: a repeated single-valued field is refused.** An artefact carrying two
      `> **Verification depth:**` lines is reported by `validate.py check` as an error, naming
      the field and both line numbers, where today it passes with `errors=0`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RepeatedFieldTests::test_a_repeated_single_valued_field_is_an_error

- [ ] **AC2: the plural fields are exempt by declaration, not by observation.** An epic
      carrying twelve `Parent:` lines passes, and the exempt set is read from one declared
      constant beside `PARENT_FIELD` - so a check run over the live corpus flags nothing among
      the 23 multi-parent epics while still flagging CR0138 and CR0218.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RepeatedFieldTests::test_the_plural_set_is_declared_and_exempts_multi_parent_epics

- [ ] **AC3: the two live records are repaired and the corpus is clean.** `CR0218` carries one
      `Verification depth` reconciling both runs and `CR0138`'s backfill note has moved to its
      Revision History, so `validate.py check` over the repository reports no instance of this
      error - the guard landing and the debt being paid are proven separately.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::RepeatedFieldTests::test_the_live_corpus_holds_no_repeated_single_valued_field

## Impact

Anyone whose transition is gated on a field, and anyone reading an artefact's metadata as its record.

The damage is the pairing this repository treats as worst: silent, and in the direction that looks fine. A gate that reads the first of two claims still prints a confident verdict, and the artefact keeps a second line that reads as live metadata and is seen by nothing. `Verification depth` is the gate on `-> Fixed`, so the shape reaches the strongest refusal in the bug ladder; `Created-by` reaches provenance, which is what a reader consults when asking who to trust for a record. Two instances today, both benign by luck rather than by design - CR0218's two lines happen to agree on the tier.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-03 | sdlc-studio | Filed |
