# BG1142: doc-freshness is described as a LATEST.md check everywhere, though it now censuses the TRD, PRD and TSD; one hook comment lists it as a per-commit lane

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/doc_freshness.py, .claude/skills/sdlc-studio/reference-scripts-verify.md, .githooks/pre-commit, tools/tests/test_lean_spec_restatements.py, changelog.d/BG1142.md, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py
> **Evidence:** US1098 builder report, 2026-10-31: items 1-4 outside the unit. `gate.py --root . --only doc-freshness` prints `[warn] ... 3 stale ... claim(s)`; doc-freshness is absent from gate.DEFAULT_CHECKS.
> **Created:** 2026-10-31
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-31T23:42:26Z

## Summary

Found by US1098's builder on 2026-10-31. Since US1098 (bdccb0e2), `doc_freshness.py` also censuses the TRD, PRD and TSD, but four places still describe it as LATEST.md-only or misplace it. (1) gate.py's `_doc_freshness` labels every finding 'N stale LATEST.md claim(s)', TRD findings included; this mislabel predates US1098. (2) The `doc_freshness.py` section of reference-scripts-verify.md, and the script's own parser description ('Flag stale facts in LATEST.md'), mention no census. (3) The .githooks/pre-commit comment near line 255 lists doc-freshness among the per-commit gate's lanes, but the lane is not in `DEFAULT_CHECKS` and runs on demand. (4) tools/tests/`test_lean_spec_restatements.py`::`_census_blanked` works out which document the census reads from `census_claims`' default doc (the TRD), and line 212 asserts the census does not read the TSD. That assertion still passes, but it is now wrong in substance.

## Steps to Reproduce

1. `gate.py --only doc-freshness` on the current tree: the finding reads 'stale LATEST.md claim(s)' while the stale baselines it counts are the TRD's, PRD's and TSD's.
2. Read reference-scripts-verify.md's `doc_freshness` section and `doc_freshness.py --help`: no census.
3. Read .githooks/pre-commit near line 255.

## Proposed Fix

Label each finding by the document it came from. Describe the census in the reference section and the parser description. Correct the hook comment. Make `_census_blanked` read the census's document set, `CENSUS_DOCUMENTS`, not the default doc.

## Acceptance Criteria

- [ ] **AC1** A doc-freshness finding from the TRD, PRD or TSD is labelled with that document, not as a LATEST.md claim.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py
- [ ] **AC2** The reference section, the parser description and the pre-commit comment describe the census and the lane's on-demand placement.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_doc_freshness.py
- [ ] **AC3** `_census_blanked` reads the census's document set, so it fails if the census stops reading the PRD or TSD.
  - **Verify:** pytest tools/tests/test_lean_spec_restatements.py

## Impact

Readers of the gate, the docs and the hook are told a narrower story than the code runs, which is the drift the census exists to catch (LC-018).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-31 | claude | Filed |
