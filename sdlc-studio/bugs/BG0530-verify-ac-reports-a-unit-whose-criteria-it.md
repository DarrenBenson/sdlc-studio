# BG0530: verify_ac reports a unit whose criteria it could not parse as a clean pass: ac=0 pass=0 fail=0, exit 0 - and every bug delivered in the last two sprints is in that state

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Found while delivering BG0527 on RUN-01KZBBZ0, 2026-08-06, at commit 367459cd, by running the tool on my own unit and getting ac=0 for criteria I had just written. Confirmed across BG0495, BG0510, BG0520 and BG0525 - every bug of the previous run, all Fixed, all panel-signed.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`verify_ac.py run --id <id>` prints `ac=0 pass=0 fail=0 manual=0 unspecified=0` and exits 0 when it parses NO acceptance criteria at all. Nothing distinguishes that from a unit whose criteria all passed. The exit code is the same, the line reads the same to a skim, and every downstream reader treats it as evidence.

The parser accepts two shapes: an `### AC1: title` heading, or a `- [ ] **AC1** ...` bullet whose bold text begins with `AC<digits>`. Verifier lines must be `**Verify:**` in bold. The house bug template - as written by `file_finding.py` and as groomed by hand across this repo - uses neither: `- [x] **A prose title.** ... *Mutant:* ... *Verify:* pytest ...`, with an italic `*Verify:*` and no `ACn` marker. So a bug's criteria are invisible to the tool that exists to execute them.

Measured, not asserted: `verify_ac.py run --id` over BG0495, BG0510, BG0520 and BG0525 - the four bugs delivered by RUN-01KZ9315, all now Fixed and signed off by the panel - returns `ac=0 pass=0 fail=0` for every one. Their criteria name real pytest selectors that really pass; none of them was ever executed by the gate that claims to.

This is LL0008 in the tool the whole verification story rests on: a deterministic tool must fail loud, never report success it did not achieve.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/verify_ac.py run --id BG0520` -> `[APL] BG0520-...md: ac=0 pass=0 fail=0 manual=0 unspecified=0 changes=0`, exit 0. 2. The same for BG0495, BG0510, BG0525. 3. Open any of those files: the Acceptance Criteria section carries four to six criteria, each with a real `*Verify:* pytest ...` selector that passes when run by hand. 4. `sdlc_md.AC_BULLET_RE` requires the bold run to start `AC<digits>`; `sdlc_md.VERIFY_RE` requires `**Verify:**` rather than `*Verify:*`. Neither matches the shape `file_finding.py` and the bug template produce.

## Proposed Fix

Two changes, and the first is the one that matters.

REFUSE the empty parse. A unit with zero parsed criteria must exit non-zero and say so - `no acceptance criteria could be parsed from <file>; the tool executed nothing` - naming the shapes it accepts. `unspecified` already exists for a criterion with no `Verify:` line, on the stated ground that an omission is not a claim; a whole unit with no criteria is the same argument one level up and currently reports the opposite. Guard it behind the same forward-only cutoff the two-role gate uses, so an existing backlog is not retro-refused.

Then widen the parser, or narrow the template, so the two agree - LL0016. Widening is the smaller change and does not require rewriting 500 artefacts: accept a checkbox bullet whose bold run is prose rather than `ACn`, numbering them positionally, and accept an italic `*Verify:*` alongside the bold form. Whichever is chosen, one fixture must carry the house bug template verbatim and assert a non-zero criterion count, or the two shapes drift apart again the moment a template changes.

The four bugs already Fixed should be re-verified once the parser sees them, not silently re-blessed.

## Acceptance Criteria

> Authored as `### ACn` headings with a bold `**Verify:**` - the only shape `verify_ac` parses.
> Writing this bug's own criteria in the shape the bug is about is the first test of the fix.

### AC1: a unit whose criteria could not be PARSED is refused, not reported clean

- **Given** a unit carrying a `## Acceptance Criteria` section from which the parser reads no criteria at all
- **When** `verify_ac.py run --id <id>` runs
- **Then** it exits NON-ZERO, says plainly that it executed nothing, and names the shapes it accepts
- **Mutant:** return 0 on a zero count - which is today's behaviour for 311 of 533 bug files, a line byte-comparable to a clean pass
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_a_section_that_parses_to_nothing_is_refused
- **Verified:** no

### AC2: "no criteria at all" is distinguished from "criteria I could not read"

- **Given** one unit with no `## Acceptance Criteria` section, and one whose section parses to nothing
- **When** each is run
- **Then** they produce DIFFERENT messages, and only the second is refused - nothing was claimed in the first case, and the grooming gate already refuses it at plan time, whereas the second is the writer and the parser disagreeing about a claim somebody did make
- **Mutant:** refuse both identically - 232 filed findings that never claimed a verifier start failing, the refusal becomes noise, and the signal it exists to carry is switched off wholesale
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_absent_and_unparseable_are_different_events
- **Verified:** no

### AC3: the writer and the parser agree, pinned by the template itself

- **Given** the acceptance criteria `file_finding.py` writes for a new bug
- **When** they are parsed by `verify_ac.parse_story`
- **Then** the count is non-zero, asserted from a fixture that carries the house template VERBATIM rather than a hand-written example that happens to match
- **Mutant:** revert the writer to its prose-title, italic-`*Verify:*` form - this reddens. `file_finding.py:127` claims the runner and the validator "cannot drift into contradicting each other again"; they had, and the comment asserting they could not sits in the file that produced the drift
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::WriterMatchesParserTests::test_the_house_bug_template_parses
- **Verified:** no

### AC4: the corpus effect is MEASURED, against a stated before figure

- **Given** the 533 bug files as they stand, of which 311 return `ac=0` today (79 with a criteria section the parser cannot read, 232 with no section)
- **When** the fix has landed and the parser is widened
- **Then** the count of bugs whose section parses to nothing is reported and is materially lower, measured over the real corpus rather than a fixture
- **Mutant:** widen the parser and measure only the fixture - the fix passes while the corpus is untouched, which is exactly how this drifted for 400 bugs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_the_corpus_shape_is_readable
- **Verified:** no

### AC5: a bug's criteria can reach the release gate at all

- **Given** `gate.py`'s release lane, which walks `sdlc-studio/stories` only
- **When** the release verify lane runs
- **Then** bugs are either included, or their exclusion is REPORTED as a stated scope rather than left silent - no bug's acceptance criteria has entered the release gate in any version, and nothing says so
- **Mutant:** leave the walk story-only and silent - the release gate keeps reporting a verification pass over 55% of the delivery corpus it never looked at
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseVerifyScopeTests::test_the_release_lane_states_its_scope
- **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in verify_ac.py, delete the non-zero exit taken on a zero criterion count | a unit whose criteria could not be PARSED is refused, not reported clean |
| AC2 | in verify_ac.py, return one identical message for an absent section and an unreadable one | "no criteria at all" is distinguished from "criteria I could not read" |
| AC3 | in file_finding.py, revert the writer to its prose-title, italic Verify form | the writer and the parser agree, pinned by the template itself |
| AC4 | in tests/test_verify_ac.py, replace the corpus walk with a single hand-written fixture | the corpus effect is MEASURED, against a stated before figure |
| AC5 | in gate.py, drop the scope statement the release verify lane prints | a bug's criteria can reach the release gate at all |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
