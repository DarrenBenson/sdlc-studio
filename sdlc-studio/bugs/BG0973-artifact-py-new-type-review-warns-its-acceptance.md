# BG0973: artifact.py new --type review warns 'its acceptance criteria are still the scaffold placeholder' although the review scaffold has no Acceptance Criteria section

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact_review_scaffold.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py, changelog.d/BG0973.md
> **Evidence:** Found running a consuming project on the installed skill 6.1.0, 2026-10-07; confirmed by reading the code at sdlc-studio main fb1ce886. the consuming project's RV0277 and RV0278.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:37:22Z

## Summary

Minting a review record prints 'NOT FINISHED: its acceptance criteria are still the scaffold placeholder. Author them before planning or reviewing this - sprint plan refuses an ungroomed unit'. The minted file has Scope / Findings / Verdict / Revision History and no Acceptance Criteria section, and a review record is not a plannable unit. The warning names a section the template does not contain, so authors either add one by guesswork (RV0276, RV0277, RV0278 each did) or learn to ignore the warning.

## Steps to Reproduce

`artifact.py new --type review --title x` -> the NOT FINISHED line; open the file -> no Acceptance Criteria section.

## Proposed Fix

Do not emit the grooming warning for meta types (review, retro, handoff, report), or add the section to the review template if review records are meant to carry criteria.

## Acceptance Criteria

- [ ] **AC1** Minting a review record prints no grooming warning about a section its template lacks
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact_review_scaffold.py -k no_ac_warning_for_review

## Triage

- Reproduced at 8b844a80 in a scratch root: `artifact.py new --type review` prints the NOT FINISHED line and the file holds no Acceptance Criteria section. Since cb232b65 (BG0476, 2026-08-02); not a regression.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Triaged: reproduced at 8b844a80, not a regression, consuming-project name generalised for the neutrality lane; changelog fragment added to Affects |
