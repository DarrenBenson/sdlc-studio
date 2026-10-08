# BG0995: refine leaves the bold **ACn** label in seeded AC headings, so a request written by the skill's own filer seeds '### AC1: **AC1** ...' (BG0291 incomplete)

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/tests/test_refine_bold_ac_label.py, .claude/skills/sdlc-studio/scripts/tests/test_refine.py
> **Evidence:** Found in a consuming project's run (RUN-01M4BHCT), 2026-10-08; reproduced against this repo's main e77cd2d5. That project's US0608, refined from its CR0554 (filed by artifact.py), seeded '### AC1: **AC1** A REST turn whose history ... with the CR-0158'.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T10:58:55Z

## Summary

`_AC_LABEL_RE` (refine.py ~74) is `^\**\s*AC\s*\d+\**\s*[:.)\]-]\s+` - it requires a punctuation separator AFTER the closing bold, so it strips `AC1: text` and `**AC2** - text` but not `**AC1** text` or `**AC1:** text` (colon inside the bold). `- [ ] **AC1** text` is exactly the form artifact.py and `file_finding.py` write, so refining any request the skill itself filed seeds a heading with a duplicated label - the BG0291 defect, back for the skill's own house style. Executed: `_strip_ac_label('**AC1** A REST turn')` and `_strip_ac_label('**AC1:** A REST turn')` both return the input unchanged.

## Steps to Reproduce

`python3 -c` importing refine from the scripts dir: `refine._strip_ac_label('**AC1** A REST turn')` returns `'**AC1** A REST turn'`. Or refine a CR filed by `artifact.py new --type cr` into one story and read its AC headings.

## Proposed Fix

Accept the bold label with or without a separator, and a separator inside the bold: e.g. `^\**\s*AC\s*\d+\s*[:.)\]-]?\**\s*[:.)\]-]?\s+`, with tests for every form the skill's own filers emit.

## Acceptance Criteria

- [ ] **AC1** Refining a request whose criteria are written `**ACn** text` or `**ACn:** text` seeds headings `### ACn: text` with no duplicated label, and the BG0291 forms still strip
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_refine_bold_ac_label.py -k every_filer_form_strips

## Triage

- Reproduced at 3bc1620e: `refine._strip_ac_label('**AC1** A REST turn')` and `('**AC1:** A REST turn')` return the input unchanged, while `'AC1: text'` and `'**AC2** - text'` strip. Pre-existing, not a regression: `_AC_LABEL_RE` (refine.py:74) has required a separator after the closing bold since US0353 (b1e4bfb3); BG0291's fix covered the separated forms only.
- Severity Medium stands: every request the skill's own filers write uses `- [ ] **ACn** text`, so every refine of one seeds duplicated labels. Groomed as filed (1 point, new test file).
- Related: CR-0618 (refine's seeding also drops the request's Verify lines); the two touch the same `_seed_acs` path and could share a unit's refactor, but each stands alone.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; private project names generalised; relations recorded |
