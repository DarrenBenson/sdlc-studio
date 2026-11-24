# BG0996: The finding filer's identifier wrapper pulls trailing punctuation into the code span: (`API_KEY_2`, `TOKEN_V2)` and `keep_alive.`

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding_md_safe_punctuation.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG0996.md
> **Evidence:** Found in a consuming project's run (RUN-01M4BHCT), 2026-10-08; reproduced against this repo's main e77cd2d5. That project's BG0509 AC1 was filed reading '(`API_KEY_2`, `TOKEN_V2)` is reported'.
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T10:59:16Z

## Summary

`_md_safe` (`file_finding.py` ~1659, also used by artifact.py) wraps `snake_case` identifiers in backticks but takes a trailing `)` or `.` into the span. Executed: `_md_safe('keys carry digits (API_KEY_2, TOKEN_V2) is reported')` returns '... (`API_KEY_2`, `TOKEN_V2)` is reported', and `_md_safe('uses resolve_canonical(x) and keep_alive.')` returns '... and `keep_alive.`'. The rendered text shows a stray parenthesis or full stop as code, and a reader copying the identifier copies the punctuation.

## Steps to Reproduce

`python3 -c` importing `file_finding` from the scripts dir: `file_finding._md_safe('(API_KEY_2, TOKEN_V2) x')`.

## Proposed Fix

End the wrapped token at the identifier's last word character: strip trailing `.,;:)]` from the matched span (keeping a call's balanced `(...)` if that is intended) before adding the closing backtick.

## Acceptance Criteria

- [ ] **AC1** Given the text `keys carry digits (API_KEY_2, TOKEN_V2) is reported` and `ends with keep_alive.`, when `file_finding._md_safe` wraps it, then each identifier is wrapped without the trailing `)` or `.`. Fails on: `TOKEN_V2)` and `keep_alive.` wrapped with the punctuation inside the span (reproduced at HEAD).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_md_safe_punctuation.py -k trailing_punctuation_outside_span
- [ ] **AC2** Given `uses resolve_canonical(x) and f(a_b).`, when `_md_safe` wraps it, then a call keeps its balanced parentheses and the sentence's full stop stays outside the span. Fails on: a fix that strips every `)` and so breaks a call's own parentheses.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding_md_safe_punctuation.py -k balanced_call_keeps_its_parentheses

## Triage

- Reproduced at 3bc1620e: `_md_safe('keys carry digits (API_KEY_2, TOKEN_V2) is reported')` wraps the second identifier as `TOKEN_V2)`, and `_md_safe('uses resolve_canonical(x) and keep_alive.')` wraps the last as `keep_alive.`, each with the punctuation inside the span. Pre-existing.
- Severity Low stands: cosmetic in rendered text, though a copied identifier carries the punctuation. Groomed as filed (1 point, new test file).

- 2026-10-09: filing RFC-0061 wrapped `persona_resolve` with the sentence's full stop inside the code span, the same defect in a fresh filing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | Claude Opus 5.5 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced on current code; private project names generalised; relations recorded |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at HEAD; added the balanced-call negative control as AC2 so the fix cannot strip every `)` |
