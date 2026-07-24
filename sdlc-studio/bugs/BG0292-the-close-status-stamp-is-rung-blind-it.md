# BG0292: the close-status stamp is rung-blind: it tells a design rung that sign-off is owed to reach Done, which was never that rung's target

> **Status:** Open
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** Medium
> **Points:** 2

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Detail

Hit closing RUN-01KYA8CF, a `--goal design` rung. The close stamped the review anchor with:

```text
**RUN-01KYA8CF closed stopped.** 18 unit(s) in the batch. **Sign-off is OWED and is the
operator's** - the two-role gate holds Done.
```

Nothing in that rung was going to Done. A design rung grooms stories; its units correctly end
at `Ready`, and their acceptance criteria are correctly RED - that is the whole point of the
red-now bar. The done-gate refused every unit for red ACs, as it should. So the stamp tells the
operator that a sign-off is owed for a state the run never targeted and could not reach.

`sprint.py:3380` writes the `owed` line unconditionally on the rung. The sibling `stopped`
outcome IS rung-correct and deliberate (partial or missed closes as the honest `stopped`), which
is what makes the sign-off half stand out.

The cost is not cosmetic. The anchor is the file `AGENTS.md` orders every fresh session to read
first. A session reading it will believe 18 units are held at a gate awaiting the operator, and
the operator reading it will believe they owe a signature they do not.

## Impact

Every design rung close. It puts a false owed-action into the one document written specifically
to orient someone who has no other context.

## Acceptance Criteria

### AC1: the stamp states the terminal the rung actually targets

- **Given** a run closed at `--goal design` whose units correctly end at Ready
- **When** the close stamps the review anchor
- **Then** it does not claim sign-off is owed to reach Done - it names the rung's own terminal, and says the units are groomed rather than awaiting signature
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseStampRungTests::test_a_design_rung_is_not_told_it_owes_a_done_signoff

### AC2: a build rung is unchanged

- **Given** a run closed at `--goal done` with units at Review past `two_role_after`
- **When** the anchor is stamped
- **Then** the owed-sign-off line is present exactly as today - this fix must narrow the claim, not remove it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseStampRungTests::test_a_build_rung_still_states_the_owed_signoff

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
