# BG0690: critic.py repair re-judges stored findings through the code-span guard, and its typed closure scanner unescapes any backslash before a greater-than sign

> **Status:** Open
> **Closes with:** US0914 (D0264: superseded only once it ships; backlog sweep D0265, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/reference-scripts-review.md
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0659-delivery-engineering.txt (engineering seat); verdicts/BG0659-delivery-qa.txt (qa seat); verdicts/BG0677-delivery-engineering.txt (engineering seat); verdicts/BG0677-delivery-qa.txt (qa seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Two text paths in critic.py's record and repair verbs do not do what they claim. (1) The code-span edge-whitespace guard. `record_repair` passes the outstanding findings, which it copies from a stored row, back through the judging `_clean` (critic.py:1416), so a partial repair of a REJECT recorded before the guard, whose finding holds a span with a trailing space, exits 2 with a remedy to requote a span the repairer did not write (exit 0 PARTIAL at 3f73ab64). The edge refusal's 'starts at character N of M' is measured after the pipe and newline substitution and the strip (critic.py:326-337), the parity refusal's before, so two leading spaces and a newline before the span report character 0 of 12 for a span starting at character 4. A span holding only a tab is refused although markdownlint passes the raw row, against the helper's docstring (critic.py:273, 288-296), and the refusal's 'no code span holds a value whose first or last character is whitespace' is false for a span of spaces only, which is recorded and passes MD038 (critic.py:333-335). No test pins the tab-only outcome or either offset. A refused record against an absent ledger still creates the file with its header, because `record_verdict` writes the header before `_clean` runs (critic.py:391-392, the same at 3f73ab64). (2) The typed --closed scanner treats any backslash followed by > as an escape, not only inside -\>, so evidence typed as C:\> anchors is stored as C:> anchors where 3f73ab64 kept it whole (critic.py:1258-1262). -\> inside a code span is stored with the backslash showing, though it reads back exactly (critic.py:1348). The cut-at-own-arrow refusal also rejects a legitimate typed closure that quotes up to the raised finding's own arrow and carries an arrow in its evidence, which 3f73ab64 recorded (critic.py:1391); it is loud, writes nothing and names --closed-file. `_ARROW_HINT` is appended to every no-match refusal, including closures with no arrow (critic.py:1642); `_cut_at_own_arrow` scans the closed text a second time apart from `parse_closures`, and `closures_from_document` has no production caller left (critic.py:1355, 1391). The lone-trailing-backslash bound is untested: changing it to i + 1 <= n raises IndexError and survives all 373 `test_critic` tests (critic.py:1258).

## Steps to Reproduce

1. With the 3f73ab64 CLI, record a delivery REJECT whose second finding holds a code span ending in a space. At HEAD run critic.py repair --unit <id> --closed '#2 -> fixed: <evidence>' - exit 2 with a requote remedy; at 3f73ab64 the same exits 0 PARTIAL. 2. critic.py record a finding carrying a code span of one tab - refused; run markdownlint on the same raw row - it passes. 3. In a workspace with no sdlc-studio/reviews/critic-verdicts.md, record a finding the guard refuses - the command refuses and the ledger file now exists with its header. 4. critic.py repair --closed 'AC1 -> fixed: evidence at C:\> anchors' - the stored evidence reads C:> anchors. 5. Against a REJECT whose finding text carries its own arrow, type a closure that quotes the finding up to that arrow and carries an arrow in its evidence (the qa seat's example: AC4 - `test_the_thing` names a helper -> fixed: a -> b) - refused before any write.

## Proposed Fix

Pass text copied from a stored cell through the non-judging path that `_supersede_value(escape`=False) already uses (critic.py:783), not `_clean`. Measure both refusals' offsets in the same string. Align the edge test with MD038 (a whitespace-only span, tab included, passes) and reword the refusal and docstring to match. Run `_clean` before `record_verdict` writes a header. Unescape only the documented -\> sequence and document that a literal backslash before > is typed doubled; state in the docs whether a code-span arrow keeps its backslash. Let the cut refusal accept a closure whose remainder parses as a disposition. Attach `_ARROW_HINT` only when the text carries an arrow. Fold `_cut_at_own_arrow` into `parse_closures` and retire `closures_from_document.` Pin the tab-only span, both offsets, the absent-ledger case, the lone trailing backslash and the arrow-in-evidence closure.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Two text paths in critic.py's record and repair verbs do not do what they claim.
- [ ] **AC2** The proposed fix lands, pinned by a test: Pass text copied from a stored cell through the non-judging path that `_supersede_value(escape`=False) already uses (critic.py:783), not _clean.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): held open under D0264 until US0914 ships - planning: SUPERSEDED - critic.py repair re-judging: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
