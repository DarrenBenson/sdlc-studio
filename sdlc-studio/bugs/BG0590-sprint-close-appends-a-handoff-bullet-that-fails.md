# BG0590: sprint close appends a handoff bullet that fails the repo's own markdown lane

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Verification depth:** functional (nine of the ten criteria run the REAL markdownlint over the written file rather than asserting a marker - AC4 and AC10 assert bytes and do not lint - and the class now proves the linter can DETECT MD004 on a known-bad file before trusting its silence. It previously claimed 'skipped, never faked' and did neither: `npx --no-install` raises OSError for a missing BINARY but merely exits non-zero with `npm ERR! 404` for a missing PACKAGE, so the helper returned that text and `assertNotIn("MD004")` passed against a linter that never ran - a review proved it with five passed and zero skipped. Mutation: 13 mutants across three rounds, each anchor asserted unique, `__pycache__` purged and `python3 -B`, all 13 KILLED, restore byte-exact. THREE survived a round before their criteria existed: the fenced-block skip, the LAST-marker rule, and the spaced thematic break; and the thematic-break test itself first passed on the defect because its fixture put the real list ahead of the break)
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The close writes a `## Handoff` section into the retro using a dash bullet - hardcoded at `handoff.py:615` in `_link_from_retro`, NOT in `sprint.py`, which only invokes `handoff.main(['generate', ...])` - regardless of the list style the rest of that document uses. Where the retro carries asterisk bullets - which every retro in this repository does, though NOT because `artifact.py new` scaffolds them: `templates/reviews/retro.md` is 17 dash bullets and 0 asterisks, so the stated CAUSE in this filing was wrong and a review executed the scaffolder to show it. The observed defect is real; its origin is the operator's own editing, not the generator - markdownlint's MD004 refuses the file, so the very next commit is BLOCKED by the tool's own output. The close succeeds and then makes the tree uncommittable, which is the worst ordering: the operator has already been told the run closed.

## Steps to Reproduce

Reproduced 2026-08-17 on RUN-01M05A5M at 4766cfe3. `sprint.py close --retro RETRO0103` exits 0 and appends to the retro: `- [HO-0059](../handoffs/HO0059-....md) - 12 remaining item(s)`. The following `git commit` is refused by the markdown lane: `RETRO0103-...md:257:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]`. Fixed by hand to an asterisk for that commit; the writer is unchanged.

## Proposed Fix

Read the document's established list style before appending, or - simpler and with fewer ways to be wrong - have the close write the handoff line through the same helper that scaffolds the retro, so one module owns the bullet. Whichever is chosen, pin it with a test that appends to a retro carrying asterisk bullets and runs the markdown lane over the result, because a test asserting the string naming a dash and HO- would pass on the defect. Check the other close-time appenders for the same assumption before assuming the handoff line is the only one.

## Correction to this filing

`Affects` originally named `sprint.py` and its test. Two review seats found that independently and
both were right: the bullet is written by `_link_from_retro` at `handoff.py:615`, and `sprint.py`
contains no handoff writer at all. It matters beyond tidiness, because `Affects` is what bounds the
`critic brief` review diff AND what `_ck_tick_verification` reads to decide whether a tick is
supported - so as filed, this unit's reviewer would have been shown a file the fix never touches,
and its own ticked criteria would have been reported unsupported at the close.

There is a SIBLING with the same assumption: `artifact.py:819` appends `- [ ] [US...](../stories/...)`
into an epic. Fixing one instance of a class and leaving the other is the enumerated-list failure
this repository keeps meeting, so AC3 covers it.

## Acceptance Criteria

- [x] **AC1** Given a retro whose lists use asterisk bullets, when the close appends its handoff section, then markdownlint reports no MD004 error for that file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_an_asterisk_retro_stays_clean
  - **Verified:** yes (2026-08-18)
- [x] **AC2** Given a retro whose lists use dash bullets, when the close appends, then markdownlint reports no MD004 error either - the fix must follow the document, not swap one hardcoded bullet for another.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_dash_retro_stays_clean
  - **Verified:** yes (2026-08-18)
- [x] **AC3** Given the sibling appender at `artifact.py` that writes a bullet into an epic, when it appends, then it follows the document's style too - one instance of a class fixed and the other left is the enumerated-list failure this repo keeps meeting.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_the_sibling_appender_follows_the_document
  - **Verified:** yes (2026-08-18)
- [x] **AC4** Given any retro, when the close appends its handoff section, then every byte OUTSIDE that section is unchanged - a fix that normalises every bullet in the file satisfies AC1 and AC2 perfectly while silently reformatting the operator's prose.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_nothing_outside_the_handoff_section_changes
  - **Verified:** yes (2026-08-18)
- [x] **AC5** Given a retro that quotes a dash-bulleted transcript inside a FENCED block while its real lists use asterisks, when the close appends, then it writes an asterisk - a fenced block is not a list, and MD004 agrees. Added because a mutant dropping the fence skip SURVIVED the other four criteria.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_bullet_inside_fenced_code_is_not_the_documents_style
  - **Verified:** yes (2026-08-18)
- [x] **AC6** Given a retro whose only unordered list sits inside a BLOCKQUOTE - a quoted reviewer verdict - when the close appends, then it follows that list's marker. markdownlint parses a quoted list AS A LIST while it parses a fenced one as text, so following the linter means matching that asymmetry rather than picking one rule. A review reproduced the failure end to end through the shipped CLI: clean before the close, MD004 after it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_blockquoted_list_sets_the_documents_style
  - **Verified:** yes (2026-08-18)
- [x] **AC7** Given a document carrying more than one marker, when the helper reads it, then the FIRST wins - which is what MD004's `consistent` mode judges against. The docstring said so and nothing pinned it; a mutant returning the last survived 327 tests.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_the_first_marker_wins_not_the_last
  - **Verified:** yes (2026-08-18)
- [x] **AC8** Given a `+`-bulleted document, when the close appends, then it writes `+` - CommonMark has three unordered markers and MD004 judges all three, so covering two is the enumerated-list failure this repository keeps meeting.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_plus_bulleted_document_is_followed_too
  - **Verified:** yes (2026-08-18)
- [x] **AC9** Given a document whose first marker-shaped line is a SPACED thematic break (`* * *`, `- - -`), when the helper reads it, then that line does not set the style - markdownlint counts neither as a list. The unspaced forms never matched, but the spaced ones do: a marker, whitespace, then a non-space is exactly the item shape. A review reproduced a dash-styled retro receiving an asterisk bullet and MD004 refusing it, where the pre-fix code linted clean - so this repair had regressed the very failure the unit exists to remove.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_spaced_thematic_break_is_not_a_list_marker
  - **Verified:** yes (2026-08-18)
- [x] **AC10** Given a bullet indented four spaces - an indented code block, not a list - when the helper reads it, then it does not set the style. The sibling of AC5's fenced block, equally unpinned until a review mutated the bound and watched 327 tests stay green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_handoff.py::HandoffBulletFollowsTheDocumentTests::test_a_bullet_indented_as_code_does_not_set_the_style
  - **Verified:** yes (2026-08-18)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | Fixed. `Affects` corrected a SECOND time: AC3's sibling lives in `artifact.py` and the shared helper in `lib/sdlc_md.py`, neither of which the corrected filing named - so the review diff would still have excluded most of the fix. AC5 added from a surviving mutant |

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | hardcode `-` in `_link_from_retro` again | Given a retro whose lists use asterisk bullets, when the close appends its handoff section, then markdownlint reports no MD004 error for that file. |
| AC2 | hardcode `*` instead, swapping one fixed marker for another | Given a retro whose lists use dash bullets, when the close appends, then markdownlint reports no MD004 error either. |
| AC3 | keep the hardcoded dash in `artifact._wire_story_to_epic` | Given the sibling appender at `artifact.py` that writes a bullet into an epic, when it appends, then it follows the document's style too. |
| AC4 | normalise every bullet in the file to the document's style | Given any retro, when the close appends its handoff section, then every byte OUTSIDE that section is unchanged. |
| AC5 | drop the fenced-block skip from `sdlc_md.document_bullet` | Given a retro that quotes a dash-bulleted transcript inside a FENCED block while its real lists use asterisks, when the close appends, then it writes an asterisk. |
| AC6 | drop the blockquote strip from `sdlc_md.document_bullet`, so a quoted list stops setting the style | Given a retro whose only unordered list sits inside a BLOCKQUOTE, when the close appends, then it follows that list's marker. |
| AC7 | return the LAST matching marker rather than the first | Given a document carrying more than one marker, when the helper reads it, then the FIRST wins. |
| AC8 | drop `+` from the marker class | Given a `+`-bulleted document, when the close appends, then it writes `+`. |
| 2026-08-18 | sdlc-studio | Round 1 REJECT repaired. `document_bullet` skipped blockquotes while markdownlint does not, so a retro whose only list was a quoted reviewer verdict still got a dash - AC1's literal condition, failing. AC6-AC8 added. The filing's stated CAUSE was also false and is corrected on three surfaces: `artifact.py new --type retro` scaffolds DASH bullets (`templates/reviews/retro.md` is 17 dash, 0 asterisk), so the asterisk styling every retro here carries is the operator's editing, not the generator's output |
| AC9 | drop the thematic-break guard from `sdlc_md.document_bullet`, so `* * *` sets the style | Given a document whose first marker-shaped line is a SPACED thematic break, when the helper reads it, then that line does not set the style. |
| AC10 | relax the leading-space bound from `^ {0,3}` to `^ *`, so an indented code block's bullet counts | Given a bullet indented four spaces, when the helper reads it, then it does not set the style. |
| 2026-08-18 | sdlc-studio | Round 2 REJECT repaired. Two blocking: `document_bullet` read a SPACED thematic break as a marker - a REGRESSION introduced by round 1's own repair, against a docstring asserting the case was handled - and the markdownlint helper PASSED SILENTLY when the package was absent rather than skipping, so the lint half of four criteria was inert in any clone that had not run `npm ci`. The class now proves the linter detects MD004 before trusting its silence. AC4 checks the tail as well as the head |
