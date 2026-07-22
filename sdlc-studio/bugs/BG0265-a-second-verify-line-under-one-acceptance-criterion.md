# BG0265: A second Verify line under one acceptance criterion is silently dropped, and every verifier it has silently dropped in this workspace sits on a Done story

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found by a grooming agent during RUN-01KY5EJX and confirmed directly in the source. `parse_story` captures a verifier with `if vm and current.verify_line is None` (`verify_ac.py`:156), so the FIRST `- **Verify:**` line in an AC block wins and every later one in the same block is read as an ordinary bullet. Nothing warns. The author sees their verifier on disk, the report counts the AC as verified, and the second command has never been executed.

Census over the live workspace, re-derived after this run split its own offender: FOUR AC blocks carry more than one Verify line and SIX verifiers have therefore never run. All four blocks are on stories at Done - US0015 AC1, US0022 AC2 (which carries FOUR verifiers, three of them dead), US0307 AC3 and US0308 AC2 - so every dropped verifier in this workspace sits on shipped work, which is worse than the first count said rather than better. A fifth block existed when this was filed: BG0257, stacked by this run's own grooming and split during it. The scan covers `sdlc-studio/stories` and `sdlc-studio/bugs`; a fenced EXAMPLE in `reference-verify.md` is not an AC and is correctly skipped by `parse_story`. The last two shipped in RUN-01KY3MFX and were inside that sprint's published claim of 84 acceptance criteria verified, which makes this the same family as US0310's four false passes: the count was not measuring what it said it measured.

The shape is this project's own recurring one. It is not a wrong answer, it is a SILENT answer - the tool does exactly what its code says and never tells the author that half their evidence was discarded. An author who stacks two verifiers is expressing that one criterion needs two checks, which is a reasonable thing to want and is also, per LL0013, exactly when an enumeration silently exempts what it forgot.

Worth noting the interaction with the duplicate-verifier lint, which already exists and already reads every Verify line on disk. The data to detect this was present and unused, which is the third time that sentence has been written about this repository this week.

## Steps to Reproduce

1. Author an AC block with two `- **Verify:**` lines, both naming resolvable pytest nodes, the second of which FAILS. 2. Run `verify_ac run` over the story. Observed: the AC is reported as passing, because only the first verifier was executed and the second was parsed as a plain bullet. 3. For the live census: scan every AC block in sdlc-studio/stories and sdlc-studio/bugs counting `- **Verify:**` lines per block. Observed: four blocks with more than one, six verifiers never executed, all four blocks on Done stories. Expected: either every verifier in a block runs, or a second one is refused at author time the way a pseudo-verify already is.

## Proposed Fix

Refuse a second `Verify:` line in one AC block, at author time, and say that a criterion needing two checks is two criteria. That is the cheaper half and it matches the existing grain: the creators already refuse a pseudo-verify rather than accepting it and warning later. Running every verifier in a block is the alternative, but it changes what an AC MEANS - one criterion, one discriminating check - and it would quietly turn the four dead verifiers already on disk into newly-failing ones without anybody deciding to. Whichever is chosen, the seven existing occurrences must be dispositioned explicitly rather than left: US0307 AC3 and US0308 AC2 in particular were counted as verified evidence in a sprint that published the number.

## Acceptance Criteria

### AC1: a second Verify line in one AC block is refused at author time

- **Given** an acceptance criterion carrying two `- **Verify:**` lines
- **When** the story is linted
- **Then** it is refused, naming the dropped verifier and saying that a criterion needing two
  checks is two criteria - the same grain as the pseudo-verify refusal, which the creators
  already apply rather than accepting and warning later
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StackedVerifierTests::test_a_second_verify_line_in_one_block_is_refused

### AC2: the seven already on disk are dispositioned, not left

- **Given** the four AC blocks in this workspace that carry more than one Verify line
- **When** the guard ships
- **Then** each is split or its extra verifier deliberately removed, and US0307 AC3 and
  US0308 AC2 in particular are re-run, because both were counted inside a published claim of
  84 verified criteria while their second verifier had never executed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StackedVerifierTests::test_no_ac_block_in_the_workspace_stacks_verifiers

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
