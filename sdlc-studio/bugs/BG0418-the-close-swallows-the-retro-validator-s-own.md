# BG0418: The close swallows the retro validator's own warning, so a scaffold with six unreplaced demonstration rows reports as 'valid' to the operator

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** US0558 AC4 requires that when THE CLOSE reads a retro, unreplaced demonstration content is reported. Independent review executed the shipped template scaffolded verbatim: the checker finds 6 leftovers, and the close step prints 'RETRO9998 valid'. `_close_retro_validate` calls the retro CLI through `_run_cli`, which captures stdout, then on rc == 0 returns the success tuple and DISCARDS the captured output. The EXAMPLES warning retro.py prints is swallowed. The operator sees: 'close [1/8] retro-validate: ok - RETRO9998 valid'.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

The mechanism exists, prints the right thing, and is read by nobody.

`retro.py`'s validator detects unreplaced demonstration rows and warns about them in wording that names the close as the thing that would otherwise be fooled: replace them before the close reads this as a filled-in retro. The close then reads it as a filled-in retro, because `_close_retro_validate` captures the CLI's stdout and throws it away on the success path.

AC4's stated protection is that a retro passing structurally is not silently accepted as filled in. What ships is exactly the silent acceptance the criterion forbids.

The unit's own `Verify:` line exercises `retro.main`, not the close, so it passes while the behaviour the criterion names does not happen. That is why this reached Done-adjacent status with a green verifier: the verifier tests a different actor from the one the acceptance criterion is written about.

The defect propagates: `close --dry-run` routes through the same probe, so the preview inherits the same blindness.

## Steps to Reproduce

1. Scaffold a retro from the shipped template and leave it as scaffolded.
2. Run the retro validator directly: it reports 6 unreplaced demonstration rows.
3. Run the close against the same retro: the step prints 'ok - RETROxxxx valid'.
4. Read `_close_retro_validate`: on rc == 0 it returns a success tuple built from the id, and the captured output is never inspected.

## Proposed Fix

1. **The close reports what the validator said.** On success, the captured output is inspected for the warning and carried into the step's detail rather than discarded, so the operator sees it in the close's own output.
2. **Decide, on the record, whether it BLOCKS.** The criterion says reported, not refused; reporting is the minimum. If a scaffold-shaped retro should refuse the close, that is a stronger rule and should be stated as one rather than arrived at by accident.
3. **The verifier tests the actor the criterion names.** A criterion written about the close must be verified through the close. The existing test exercises `retro.main` and would pass with the close removed entirely.
4. The dry run inherits the fix, since it routes through the same probe.

## Acceptance Criteria

- [ ] The close reports the retro validator's unreplaced-demonstration warning in its own output, so a scaffolded retro cannot pass as filled in.
- [ ] Whether that reporting also BLOCKS the close is stated explicitly as a rule, not left to be inferred.
- [ ] The criterion is verified THROUGH the close, not through the retro CLI - the test must fail if the close stops reporting it.
- [ ] `close --dry-run` reports the same warning, since it routes through the same probe.
- [ ] A retro with no unreplaced demonstration content produces no warning, so the check does not become noise on every close.

## Impact

The retro is where a sprint's findings become work, and the demonstration rows are the template's placeholders. A close that accepts them as filled in is the exact failure the content check exists to prevent, and it certifies a document nobody has written.

The wider pattern is the one this review round found four times: the test asserts the pure helper or the postcondition, never the production path the acceptance criterion actually names.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
