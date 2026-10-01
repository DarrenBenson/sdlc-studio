# BG0827: The review brief asks the reviewer to judge origin 'at the base ref' but never names the base ref

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py, changelog.d/BG0827.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** soak F41; US0965 rehearsal friction; eval 09 v6-main; HEAD 7e53a438 brief text (scratchpad brief-BG0816.txt lines 99-100) names 'the base ref' with no value
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:28Z

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: a fixture run with `base_ref` 7aa48b1b holding BG0001; `critic.py brief --unit BG0001 --seat qa` prints 'Diff scope (... inspect with git diff/status on these paths): a.py' and 0 occurrences of the sha.

`critic.py brief` tells the reviewer to tag each finding by what the unit's diff did 'at the base ref' and scopes the diff by Affects, but never names the ref or commit to diff against. A carried bug's repair and the carried unit's round-1 code in one uncommitted tree cannot be told apart (soak F41), a repair round carries no claims-to-verify section, and the US0965 rehearsal and eval 09's second reviewer had to be told the run's commit. The hand-over half of the same friction (pass the brief whole, `--out FILE`) is BG0817, filed 2026-09-28; this finding is the base ref only.

## Steps to Reproduce

`critic.py brief --unit <id> --seat qa` for a unit in an open run: the text says 'at the base ref' and names none.

## Proposed Fix

Print the run's recorded base ref (`run_state.unit_run_base_ref`) in the diff-scope section as the exact `git diff <base> -- <Affects>` command; with no run naming the unit, the line stays as today. The rejoinder half is dropped: `review_base` is a ledger row count, not a commit, and naming the prior round's commit would need a new ledger field.

## Acceptance Criteria

- [ ] **AC1** Given a fixture git tree whose open run records `base_ref` <sha> and holds BG0001 (Affects `a.py`), when `critic.py brief --unit BG0001 --seat qa --root <fixture>` runs, then the brief's diff-scope section prints `git diff <sha> -- a.py`; with no run open, the brief prints no `git diff` command and exits 0. Fails on: HEAD, which names no ref
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py::BriefBaseRefTests::test_the_brief_names_its_base_commit
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD; rejoinder AC dropped (would need a per-round commit field); Points 2 to 1 |
