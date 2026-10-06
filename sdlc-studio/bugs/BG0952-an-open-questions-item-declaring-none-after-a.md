# BG0952: An Open Questions item declaring None after a dash is read as unanswered - `_DECLARES_NONE_RE` does not allow a leading dash

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_declares_none_forms.py
> **Evidence:** Found migrating a consuming project from skill 2.4.1 to the installed 6.1.0 on 2026-10-06; reproduced against sdlc-studio main at aa19a2e3.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:23Z

## Summary

`unresolved_questions` skips an item that declares there are no questions, via `_DECLARES_NONE_RE = ^(none|n/?a)\b` (lib/`sdlc_md.py`:2279). An item written `- [ ] <U+2014> None (CR-0165 Q1-Q4 resolved at the consult)` (an em dash) or `- [ ] - None.` - a dash before the word - does not match and is refused as an open question. The code's own comment states the intent: reading such an item as an unanswered question 'would force already-correct artefacts to be fixed, which is a guard manufacturing work'.

On the consuming project this produced at least 25 false open-question errors on Done stories (e.g. US0326, US0328, US0355), each of which had to be rewritten to say the same thing in a different shape.

## Steps to Reproduce

From .claude/skills/sdlc-studio/scripts:

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from lib import sdlc_md; d=lambda i: '# US0001: t\n\n> **Status:** Done\n\n## Open Questions\n\n'+i+'\n'; [print(repr(i), bool(sdlc_md.unresolved_questions(d(i)))) for i in ['- [ ] None', '- [ ] \u2014 None (all resolved)', '- [ ] - None.']]"
```

Observed: False, True, True (True = reported unresolved).

## Proposed Fix

Allow leading punctuation and whitespace before the declaration, e.g. `^[\s\-\u2013\u2014:]*(none|n/?a)\b`, with a test for each dash form.

## Acceptance Criteria

- [ ] **AC1** `- [ ] <U+2014> None ...` (em dash), `- [ ] <U+2013> None` (en dash) and `- [ ] - None.` are not reported as open questions, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_declares_none_forms.py -k dash_forms
- [ ] **AC2** `- [ ] Nonetheless, should we ...?` is still reported (the word boundary still holds)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_declares_none_forms.py -k word_boundary

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | Claude Opus 5.5 | Filed |
| 2026-10-06 | sdlc-studio | Retitled: was '`- [ ] <U+2014> None (...)` is read as an unanswered Open Question - `_DECLARES_NONE_RE` does not allow a leading dash' |
| 2026-10-06 | Claude Opus 5.5 (triage) | Em dashes spelled as U+2014 / `\u2014` so the house-style lane passes; the repro is unchanged in effect |
| 2026-10-06 | Claude Opus 5.5 (triage) | Consuming-project name generalised for the neutrality lane |
