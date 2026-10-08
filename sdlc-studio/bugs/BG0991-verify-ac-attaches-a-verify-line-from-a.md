# BG0991: verify_ac attaches a **Verify:** line from a LATER section (history, update notes) to the last criterion and executes it, because a criterion block never closes at a ## heading

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG0991.md
> **Evidence:** Found in a consuming project RUN-01M4BHCT, 2026-10-07: BG0470's AC2 read FAIL with the text of a dated `**Verify:**` line from its `## Closed 2026-07-23` history section (line 93), 'unrecognised verifier `grep'. Code read at this repo's main 922b9d6c, verify_ac.parse_story (~137-215).
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T18:51:52Z

## Summary

`parse_story` tracks the current `##` section but does not flush the open ACBlock when a new `##` heading starts. A criterion opened in `## Acceptance Criteria` therefore stays open to the end of the file, and every later `**Verify:**` line - in Revision History, an `## Update <date>` note, a `## Closed <date>` record - is appended to its `extra_verifiers` and executed as part of that criterion (BG0265 made extra verifiers run). `criteria_blocks` filters by the section at the block's HEADING (BG0648), so the block counts as in-section while carrying verifiers from outside it. The visible symptom is a criterion failing on a historical, prose-form Verify note the author never meant as a check; the worse case is a stale historical Verify that passes and props up a criterion, or one that runs a shell command nobody reviewed as part of the AC.

## Steps to Reproduce

A bug with `## Acceptance Criteria` holding AC1 and AC2 (each with a valid Verify), followed by `## Closed 2026-07-23` containing a line starting `**Verify:**` with prose. `verify_ac.py run --id <bug>` -> AC2 FAIL quoting the history line.

## Proposed Fix

Flush the open criterion when a `##` heading begins a different section (keep fenced-block handling), so a criterion's verifiers are only the Verify lines inside its own section; and have `lint` name any `**Verify:**` line outside the criteria section so authors can relabel historical ones.

## Acceptance Criteria

- [ ] **AC1** A **Verify:** line under a later ## section is not attached to any criterion and is not executed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py -k verify_in_later_section_not_attached
- [ ] **AC2** `verify_ac` lint names a **Verify:** line that sits outside the Acceptance Criteria section
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac_section_boundary.py -k lint_names_verify_outside_criteria

## Triage

- Reproduced at 124c4d08: `verify_ac.parse_story` on a bug whose `## Closed <date>` section holds a `**Verify:**` line attaches it to AC2 as an extra verifier (`['grep the history note']`), so it is executed. Not a regression of a recent run. Related, not a duplicate: BG0981 (an unparseable Verify counted as groomed); both are the runner and the grooming gate reading Verify lines differently from the author. Reconcile's BG0356 advisory dismissed: BG0356 (Fixed) was validate and verify_ac disagreeing on whether a Verify executes, not which section a Verify belongs to. The filed text's code spans with trailing spaces were fixed for markdownlint (BG0974).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Claude Opus 5.5 | Filed |
| 2026-10-08 | Claude Opus 5.5 (triage) | Triaged: reproduced at 124c4d08, not a regression; consuming-project name generalised; changelog fragment added to Affects |
