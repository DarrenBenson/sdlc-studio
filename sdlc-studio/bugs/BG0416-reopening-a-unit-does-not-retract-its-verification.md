# BG0416: Reopening a unit does not retract its verification-depth claim, so the planner reads it as BUILT-NOT-CLOSED and forecasts it at zero points

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each repair verified by applying its own mutant and watching it redden, bytecode purged, python3 -B)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0372 stands at Status Open, REOPENED at RUN-01KYNKDP's closing review because the fix delivered nothing, and still carries `> **Verification depth:** functional (tests red-first)` from the retracted Fixed. Planning the next sprint, `sprint plan` prints `excluded from the build forecast (BUILT-NOT-CLOSED, close them): BG0402, BG0359, BG0372` and forecasts 142 points against a 150-point batch. The 8 missing points are exactly those three units.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

**The filed diagnosis was wrong about the mechanism, and the corrected one is worse.** Both are recorded below; the original is kept rather than rewritten, because a finding that names the wrong cause and is then quietly edited is how a wrong premise gets built on.

**As filed:** the planner reads the surviving `Verification depth` field and concludes the unit is built.

**As checked:** `_built_not_closed` never reads that field. It reads `_verifiers_all_green`, which reads the unit's entry in `sdlc-studio/.local/verify-report.json`. The exclusion is driven entirely by the unit's executable ACs passing.

That makes the defect sharper. BG0372 was reopened because its tests "asserted a constant and a hand-written header the writer never emits" - a green that a human judged meaningless. Those tests still pass. So the planner reads a green verdict that a reviewer has already overturned, and prices the unit at zero.

**A reopen is a human overturning a machine verdict, and nothing in the machine hears it.** The verify-report is not invalidated, so every downstream reader of "are this unit's ACs green" keeps getting the answer the reopen rejected. The forecast is the reader that happened to be looking; it will not be the only one.

The verification-depth half of the original filing is still true as a fact - BG0372 stands at Open while asserting it was verified to a functional tier - it is simply not the cause of the exclusion. It stays in scope as hygiene, and because a retracted depth is the natural place to record that a green is no longer trusted.

## Steps to Reproduce

1. Open BG0372: Status is Open, the revision history records the reopen, `Verification depth` still reads `functional (tests red-first)`, and its four `Verify:` lines point at `VelocityCarriesTheOverheadSplitTests` - the tests the reopen recorded as asserting nothing.
2. Run those tests: they pass. The verify-report records the unit green.
3. Put BG0372 in a worklist and run `sprint plan` - it appears under `excluded from the build forecast (BUILT-NOT-CLOSED, close them)`.
4. Read `_built_not_closed` in sprint.py: it consults `_verifiers_all_green` and the status, and never reads `Verification depth`. The filed diagnosis does not hold.

## Proposed Fix

1. **A reopen retracts the evidence with the status.** Moving a unit out of a terminal status rewrites `Verification depth` to a stated retraction naming the reopen, so no reader finds an unretracted claim on a unit whose delivery was withdrawn. This also makes the existing `_bug_depth_gate` refuse a second trip to Fixed without fresh evidence, which is the behaviour that should already follow.
2. **A reopen invalidates the unit's verify-report entry.** The green the reopen overturned must not be readable as current by anything. The verifiers have to be re-run after the reopen for the unit to read green again.
3. **The planner does not price a retracted unit as built.** `_built_not_closed` refuses on a retracted depth regardless of what the verify-report says, so the two mechanisms cannot disagree.
4. **The exclusion is loud when it moves the total.** The plan already names the excluded ids; it should also state the points they remove, so a forecast below the batch total explains the difference in the same line.

## Acceptance Criteria

- [ ] Moving a unit out of a terminal status rewrites its `Verification depth` to a stated retraction naming the reopen, so no reopened unit carries an unretracted claim.
- [ ] A reopen invalidates the unit's verify-report entry, so the green a reviewer overturned cannot be read as current by any downstream reader.
- [ ] `_built_not_closed` refuses to call a unit built when its verification depth is retracted, whatever the verify-report holds, so the two cannot disagree.
- [ ] The plan states the points removed by any build-forecast exclusion, so a forecast below the batch total explains the difference in the same line.
- [ ] A test reopens a unit whose verifiers pass and asserts BOTH the retraction AND that the planner prices it at full points - the mutant that reverts either half must redden it. BG0372, BG0359 and BG0402 are corrected on disk.

## Impact

Reopening is how this project withdraws a false completion claim, and it is the mechanism that most needs to leave nothing behind. What it currently leaves behind is the green verdict itself: the tests a reviewer judged vacuous keep passing, keep being recorded as passing, and keep being read as "this unit is built".

Here the effect is a forecast 5% low on a sprint whose whole goal is that its own measurements can be trusted. The general effect is worse - it means the reopen mechanism, the one control that exists to overturn a false green, does not actually reach the green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
| 2026-07-29 | Claude Opus 5 (RUN-01KYPZ1G) | DIAGNOSIS CORRECTED before any code was written. The filing blamed the surviving `Verification depth` field; `_built_not_closed` never reads it. The exclusion comes from `_verifiers_all_green` reading the unit's verify-report entry, and BG0372's vacuous tests still pass - so the planner reads a green a reviewer had already overturned. The original wording is kept above rather than replaced. Acceptance criteria restated against the real mechanism; the depth-retraction half stays in scope as hygiene and as the place a withdrawn green is recorded. |
