# BG0530: verify_ac reports a unit whose criteria it could not parse as a clean pass: ac=0 pass=0 fail=0, exit 0 - and every bug delivered in the last two sprints is in that state

> **Status:** Open
> **Severity:** High
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
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

- [ ] The behaviour described is corrected: `verify_ac.py run --id <id>` prints `ac=0 pass=0 fail=0 manual=0 unspecified=0` and exits 0 when it parses NO acceptance criteria at all.
- [ ] The proposed fix lands, pinned by a test: Two changes, and the first is the one that matters.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
