# BG0949: An inline `ruled:` or `decided:` ruling is never recognised - `_RULING_RE` puts a word boundary after the colon

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_ruling_inline_forms.py
> **Evidence:** Found migrating a consuming project from skill 2.4.1 to the installed 6.1.0 on 2026-10-06; reproduced against sdlc-studio main at aa19a2e3.
> **Created:** 2026-10-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-06T12:35:14Z

## Summary

`unresolved_questions` accepts a ruling recorded on the item itself when `_RULING_RE` matches (lib/`sdlc_md.py`:2282). The pattern is `\b(ruled by|ruled:|settled in|resolved by|decided:)\b`. The trailing `\b` after `ruled:` and `decided:` requires a word character immediately after the colon, so the forms anyone actually writes - `ruled: yes, shipped in v2`, `**Decided:** no` - never match and the item is reported as an unanswered Open Question. Only `ruled:yes` with no space passes. `ruled by`, `settled in` and `resolved by` end in a word character, so they are unaffected.

The docstring says the inline route exists so that demanding the `## Resolved Questions` heading is not 'demanding a layout, not an answer'. For two of the five advertised forms the layout is still demanded, and the refusal does not say why, because the author did write a ruling.

Found while clearing 189 open-question errors on a migrating project: rulings had to be moved under the heading because the inline form silently failed. The same corpus also carried rulings as a `**Resolved:** ...` line directly under the item (the consuming project's EP0006, CR0020, CR0022), which the item-line-only read cannot see - worth deciding whether that form counts while the pattern is being fixed.

## Steps to Reproduce

From .claude/skills/sdlc-studio/scripts:

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from lib import sdlc_md; d=lambda i: '# US0001: t\n\n> **Status:** Done\n\n## Open Questions\n\n'+i+'\n'; [print(repr(i), bool(sdlc_md.unresolved_questions(d(i)))) for i in ['- [x] Cache? - ruled: yes', '- [x] Cache? - **Decided:** no', '- [x] Cache? - ruled by the consult', '- [x] Cache? - ruled:yes']]"
```

Observed: True, True, False, False (True = reported unresolved). Expected: all four resolved.

## Proposed Fix

Drop the trailing `\b` for the colon forms - e.g. `\b(?:ruled by|settled in|resolved by)\b|\b(?:ruled|decided):` - and pin every alternative followed by a space in a test.

## Acceptance Criteria

- [ ] **AC1** `- [x] <q> - ruled: <answer>` and `- [x] <q> - decided: <answer>` (a space after the colon, any case, bold or plain) are accepted by `unresolved_questions`, shown by a test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ruling_inline_forms.py -k colon_forms
- [ ] **AC2** A test pins each `_RULING_RE` alternative written the way prose writes it, so a boundary regression on any one of them goes red
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ruling_inline_forms.py -k every_alternative
- [ ] **AC3** A ruling that names a destination is still held to that destination (the BG0456 guard keeps passing)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ruling_inline_forms.py -k destination_still_held

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-06 | Claude Opus 5.5 | Filed |
| 2026-10-06 | Claude Opus 5.5 (triage) | Consuming-project name generalised for the neutrality lane |
