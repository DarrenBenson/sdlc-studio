# BG0557: sprint close --dry-run reports a checklist STOP the real close does not

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Verification depth:** functional (unit: the renderer driven over multi-line and single-line steps including a blank-padded body; mutation: both planned mutants applied and killed, the second only after a fixture that could discriminate)
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio-authoring-session; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

During RUN-01KZF9AF's close, `sprint close --retro RETRO0099 --dry-run` reported `STOP checklist: 1 compulsory checklist item(s) unanswered` on three consecutive runs. The real close, run immediately afterwards against the same tree with no edits in between, reported `checklist: ok - 22 compulsory item(s), none outstanding`. Calling `sprint._close_checklist(root, retro, state)` directly also returned ok=True, and `sprint_report.checklist()` returned ok=True with outstanding=[] under both the bare and the `unit_ids`-passing call the two paths use.

## Relationship to BG0460

The filer warned this may duplicate BG0460, and it does not. BG0460 (Fixed) was about a step
reported as NEITHER refusing nor unevaluated, and about a count claiming seven steps over a
ten-step chain - both defects in how the dry run DESCRIBES its own pass. This one is that the
dry run and the real close reach different verdicts on the same tree, which is a defect in what
the dry run computes rather than in how it reports it. They share `sprint.py` and the close
path, which is why the wording overlaps.

## Steps to Reproduce

Close a run whose retro has just had its carried-issues table completed. Run `sprint.py close --retro RETROxxxx --dry-run` and read the checklist step, then run the real close. The dry run refused where the real one passed. The refusal is also unactionable on its own: the renderer truncates the multi-line detail at the first line, so the item the step is refusing on is never named in the output.

## Proposed Fix

Two things, and the second is worth more than the first. Find why the dry-run path composes a different checklist from the real one - the state each is handed is the first place to look. Then stop the renderer truncating the detail: `_close_checklist` builds a multi-line block naming each outstanding item, and the close's line renderer cuts it at the first newline, so a refusal that was written to name its cause prints without it.

## Acceptance Criteria

> **Narrowed after a premise check, 2026-08-11.** The bug reports two things. The second - the
> renderer truncating a multi-line refusal at its first newline - is reproducible, is a defect,
> and is what this unit fixes. The first - that `--dry-run` composes a DIFFERENT checklist from
> the real close - could not be reproduced in this session: the dry run reported unanswered
> known-issues rows, rulings were then added, and the real close passed. That is a state change
> between the two runs, not a divergence between two composers, and the bug's own note records
> that calling `_close_checklist` and `sprint_report.checklist` directly both returned ok.
> Recorded rather than built on, because a repair for a divergence nobody can reproduce is a
> repair aimed at nothing. The truncation ALONE explains the reported symptom: the dry run named
> a cause the reader never saw.

### AC1

- **Given** a close chain step whose refusal detail is MULTI-LINE - `_close_checklist` builds one
  naming each outstanding item, one per line
- **When** `sprint.py close --dry-run` renders it
- **Then** every line appears, indented under its step. A refusal that says "1 item unanswered"
  without saying WHICH sends the reader back to run the command again to find out, which is the
  reported symptom.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k the_dry_run_prints_every_line_of_a_multi_line_refusal
- **Verified:** yes (2026-08-11)
- **Mutant:** in `sprint.py`, restore the first-line-only truncation in `dry_run_report`.

### AC2

- **Given** a step whose remedy is multi-line
- **When** the same report renders
- **Then** its continuation lines appear too, and a single-line step still renders as ONE line -
  the positive control, without which "print every line" is satisfied by a renderer that pads
  every step with blanks.

- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k a_single_line_step_still_renders_as_one_line
- **Verified:** yes (2026-08-11)
- **Mutant:** in `sprint.py`, change the continuation filter to emit blank lines as well.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, revert `dry_run_report` to emitting only the first line of each detail | |
| AC2 | in `sprint.py`, change the continuation filter to emit blank lines as well | |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio-authoring-session | Filed |
