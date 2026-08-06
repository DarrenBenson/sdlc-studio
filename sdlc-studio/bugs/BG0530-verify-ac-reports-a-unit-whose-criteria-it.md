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

> **REVISED at plan review, before any code.** A seat executed against the tree and refuted three
> things: AC2's carve-out rested on a claim that the grooming gate refuses criteria-less bugs at
> plan time (`engagement_floor check` reports 0 violations over 1601 units, so nothing does);
> AC3's mutant was fictional (`file_finding.py` emits `- [ ] <text>`, and there is no italic
> `*Verify:*` form to revert to); and AC4's mutant edited a test, which cannot die on a mutation
> of itself. It also named the case that would have SURVIVED the whole fix, now AC6.

### AC1: a unit whose criteria could not be PARSED is refused, not reported clean

- **Given** a unit whose `## Acceptance Criteria` section yields no criteria to the parser
- **When** `verify_ac.py run --id <id>` is driven as a COMMAND, not as a library call
- **Then** it exits non-zero, says it executed nothing, and names the shapes it accepts
- **Mutant:** in verify_ac.py, delete the non-zero exit taken on a zero criterion count
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_a_section_that_parses_to_nothing_is_refused_through_the_cli
- **Verified:** no

### AC2: "no criteria at all" is reported distinctly from "criteria I could not read"

- **Given** one unit with no criteria section and one whose section parses to nothing
- **When** each is run
- **Then** the messages DIFFER and name their own cause. Whether the first also exits non-zero is a stated decision recorded on this criterion, not an accident: it is 232 of 534 bug files, most of them filed findings that never claimed a verifier, and nothing else in the tree refuses them today
- **Mutant:** in verify_ac.py, return one identical message for both - a reader is sent to write criteria when the criteria exist and cannot be read, or the reverse
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_absent_and_unparseable_are_different_events
- **Verified:** no

### AC3: the writer emits the shape the parser reads, pinned by the template itself

- **Given** the criteria `file_finding.py` writes today - `- [ ] <prose>` bullets carrying no `ACn` marker, which `AC_BULLET_RE` cannot match
- **When** a freshly filed bug is parsed by `verify_ac.parse_story`
- **Then** the count is non-zero, asserted from a fixture built by CALLING the filer rather than from a hand-written example that happens to match
- **Mutant:** in file_finding.py, drop the `ACn` marker from the criteria renderer, returning it to the bare `- [ ] <prose>` bullet it emits today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::WriterMatchesParserTests::test_a_freshly_filed_bug_parses
- **Verified:** no

### AC4: the corpus effect is MEASURED by production code, against a reproducible figure

- **Given** the 534 bug files as they stand: 232 with no criteria section, 75 whose section parses to nothing, 36 that parse but carry no verifier at all
- **When** `verify_ac.py corpus-scan` reports those three counts
- **Then** the counting routine SHIPS, so the before and after figures are produced by the same code rather than by a script somebody wrote once and threw away
- **Mutant:** in verify_ac.py, collapse the three counts into one total - the three states become indistinguishable and AC6's case hides inside the number
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_the_corpus_scan_reports_three_distinct_states
- **Verified:** no

### AC5: the release lane states its scope

- **Given** `gate.py`'s release verify lane, which walks `sdlc-studio/stories` only
- **When** it runs
- **Then** it names the artefact classes it did NOT walk and how many units that is, because a verification pass silently taken over 55% of the delivery corpus is the same false green one level up
- **Mutant:** in gate.py, drop the scope statement the release verify lane prints
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseVerifyScopeTests::test_the_release_lane_states_its_scope
- **Verified:** no

### AC6: the vacuous shape that would SURVIVE this fix is refused too

- **Given** a unit whose criteria parse but carry no `Verify:` line at all - `ac=N pass=0 fail=0 unspecified=N` - which is 36 bug files today and is where widening the parser MOVES the 75 unreadable ones
- **When** it is run
- **Then** it is refused, or reported in a form no reader can mistake for a pass. Without this, the fix converts a would-be refusal into a silent exit 0 while AC4's count improves - the criterion reproducing the defect it repairs, in a different costume. Found by a seat at plan review
- **Mutant:** in verify_ac.py, return 0 when every parsed criterion is unspecified
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_criteria_with_no_verifiers_are_not_a_pass
- **Verified:** no

### AC7: the positive control - a well-formed unit still passes at the shipped entry point

- **Given** a bug whose criteria parse and whose verifiers pass
- **When** `verify_ac.py run --id` is driven as a command
- **Then** it exits 0. `verify_ac` sits in the per-commit lane, so a refusal wired unconditionally satisfies AC1, AC2 and AC6 and stops every commit in every consuming project
- **Mutant:** in verify_ac.py, return the refusal for every unit regardless of what parsed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::EmptyParseIsRefusedTests::test_a_well_formed_unit_still_passes
- **Verified:** no

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in verify_ac.py, delete the non-zero exit taken on a zero criterion count | a unit whose criteria could not be PARSED is refused, not reported clean |
| AC2 | in verify_ac.py, return one identical message for an absent section and an unreadable one | "no criteria at all" is reported distinctly from "criteria I could not read" |
| AC3 | in file_finding.py, drop the ACn marker from the criteria renderer | the writer emits the shape the parser reads, pinned by the template itself |
| AC4 | in verify_ac.py, collapse the three corpus counts into one total | the corpus effect is MEASURED by production code, against a reproducible figure |
| AC5 | in gate.py, drop the scope statement the release verify lane prints | the release lane states its scope |
| AC6 | in verify_ac.py, return 0 when every parsed criterion is unspecified | the vacuous shape that would SURVIVE this fix is refused too |
| AC7 | in verify_ac.py, replace the pass path with the refusal for every unit | the positive control - a well-formed unit still passes at the shipped entry point |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
| 2026-08-06 | sdlc-studio | Groomed for the v5 release sprint: tool-derived criteria replaced with decidable ones naming their mutants, authored in the shape verify_ac actually parses |
