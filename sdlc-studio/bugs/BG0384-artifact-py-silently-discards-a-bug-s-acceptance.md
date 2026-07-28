# BG0384: artifact.py silently discards a bug's acceptance criteria, so the sanctioned filing path produces the criteria-less bug the floor exists to refuse

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; the cross-path test falsified the report's own premise)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Evidence:** artifact.py:502 `_fill_acs` - `if not acs or type_ not in ("story", "cr", "epic"): return body`
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

`artifact.py new --type bug --fields-file <doc>` accepts an `acs` list, writes the bug, reports success, and throws the criteria away. `_fill_acs` returns the body untouched unless the type is one of `story`, `cr` or `epic`, and the bug template has no `## Acceptance Criteria` section for it to fill. Nothing warns, and the exit code is 0.

`file_finding.py` - the other sanctioned path to the same artefact - is WORSE, and this bug originally said it was the correct one. `derived_criteria` returns nothing when the author supplied their own, on the stated rule that an authored criterion is never displaced by a derived one; nothing then renders them, so `criteria_block` falls through to the stated absence and writes `nothing here states what fixed would look like` OVER the criteria the author wrote. The document asserts the opposite of the truth, and the engagement floor reads that assertion and agrees. Two paths, one artefact, and neither stores the field (LL0016) - this one found by a test written for the other.

## Steps to Reproduce

1. Write a fields file with a populated `acs` list.
2. `artifact.py new --type bug --fields-file <doc>` -> `created BG0xxx ... (indexed=True)`, exit 0.
3. `grep -c 'Acceptance Criteria' <the new file>` -> 0. The criteria are nowhere in the document.

## Proposed Fix

Two parts, and the second is the one that lasts. Give the bug template an `## Acceptance Criteria` section and let `_fill_acs` fill it for a bug on the same terms as a CR. Then make the drop impossible to repeat silently: a supplied field that the chosen type's template has no home for is REFUSED at filing, naming the field and the type, rather than written away. The enumerated tuple `('story', 'cr', 'epic')` is the defect's actual shape - an enumeration silently exempts what it forgot (LL0013), and the next type added will be forgotten the same way.

## Acceptance Criteria

- [ ] A bug filed through `artifact.py new` with a populated `acs` list carries those criteria in its document, in the same form `file_finding.py` produces for a bug.
- [ ] A supplied field the chosen type cannot store is refused at filing, naming the field and the type - not written and not silently dropped. Pinned by a test that supplies a field no template accepts and asserts a non-zero exit.
- [ ] The two filing paths agree: a test files the same fields document through `artifact.py new` and through `file_finding.py file` and asserts both documents carry the same criteria count.
- [ ] BG0381, BG0382 and BG0383 carry the criteria they were filed with.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
| 2026-07-28 | Claude Opus 5 | Acceptance criteria back-filled. They were supplied at filing and neither creation path wrote them: `artifact.py` has no Acceptance Criteria section for a bug, and `file_finding.py` rendered the STATED ABSENCE over them. Both are repaired under BG0384; these four documents are the evidence of the defect and are restored from the fields files they were filed from, not re-invented. |
| 2026-07-28 | Claude Opus 5 | Summary corrected during delivery. The filer was described as honouring `acs`; it does not. BG0384 itself was filed through it and its four criteria were replaced by the thin-evidence note - the finding recording the defect was written by the defect. Found because AC3's cross-path test compared the two counts and got 2 against 0; the test was written to check my fix and falsified my premise instead. |
