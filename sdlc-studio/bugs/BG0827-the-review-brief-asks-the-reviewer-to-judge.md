# BG0827: The review brief asks the reviewer to judge origin 'at the base ref' but never names the base ref

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py, changelog.d/BG0827.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** soak F41; US0965 rehearsal friction; eval 09 v6-main; HEAD 7e53a438 brief text (scratchpad brief-BG0816.txt lines 99-100) names 'the base ref' with no value
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:28Z

## Summary

`critic.py brief` tells the reviewer to tag each finding by what the unit's diff did 'at the base ref' and scopes the diff by Affects, but never names the ref or commit to diff against. A carried bug's repair and the carried unit's round-1 code in one uncommitted tree cannot be told apart (soak F41), a repair round carries no claims-to-verify section, and the US0965 rehearsal and eval 09's second reviewer had to be told the run's commit. The hand-over half of the same friction (pass the brief whole, `--out FILE`) is BG0817, filed 2026-09-28; this finding is the base ref only.

## Steps to Reproduce

`critic.py brief --unit <id> --seat qa` for a unit in an open run: the text says 'at the base ref' and names none.

## Proposed Fix

Print the unit's review base (its `review_base`, else the run's base ref) as a commit in the diff-scope section with the exact `git diff <base> -- <Affects>` command; in a rejoinder, name the prior round's commit as the repair's base. Land after or with BG0817, which also edits critic.py brief.

## Acceptance Criteria

- [ ] **AC1** Given a unit in an open run, when `critic.py brief` runs, then the brief names the base commit and a `git diff <base> -- <Affects>` command. Fails on: HEAD, which names no ref
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py::BriefBaseRefTests::test_the_brief_names_its_base_commit
- [ ] **AC2** Given a rejoinder brief, then it names the commit the prior round reviewed as the repair's base. Fails on: HEAD
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_base_ref.py::BriefBaseRefTests::test_a_rejoinder_names_the_prior_round_commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
