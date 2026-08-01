# BG0484: EP0194 shipped a false claim about its own feature: critic.py brief never emitted the fingerprint the gate demands

> **Status:** Fixed
> **Verification depth:** functional (five findings repaired; F1 pinned by a CLI test not a library one, F4 mutant verified KILLED after being SURVIVED, three docstrings corrected)
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/carry_forward.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** independent-critic (engineering/qa/product seats); human; v1
> **Raised-in-batch:** 2026-08-01T08:00:52Z

## Summary

Five findings from the EP0194 batch-boundary review, all classified NEW against base 3570c94a by `git log -S`.

F1 (US0577) - `brief_fingerprint` had exactly ONE caller, the `--brief-file` branch of `cmd_record`. `cmd_brief` never called it, so running `critic.py brief` printed no fingerprint and the value `record` demands could not be obtained from any command a reviewer runs. Meanwhile the changelog fragment and the commit message both stated that `critic.py brief` emits it. The claim was false when written. AC1's verifier computed `brief_fingerprint(critic.brief(...))` IN-PROCESS - a library test, which cannot see that the lane is missing.

F2 (US0577) - the mandatory `--brief` value was unvalidated: `--brief x` recorded successfully. Combined with F1 the cheapest route through the gate was to invent a value, recording provenance for a prompt that was never issued.

F3 (US0578) - the refusal named a remedy the tool could not perform, pointing at a fingerprint nothing printed.

F4 (US0580) - the untagged-finding guard was load-bearing and pinned by nothing: deleting it left the entire suite green. Every REJECT row in the shipped log carries untagged findings that predate the origin axis, so the mutant would have begun covering real units at the Done gate silently.

F5 (US0580) - `sprint_covers_independently`'s docstring, its restatement in sprint.py and `carry_forward.py`'s header all still said coverage requires an APPROVE. True at the base ref, falsified by this diff, and inside the unit's own declared Affects. The claim-drift lane shipped in the sibling epic fired on none of them.

## Steps to Reproduce

F1: python3 .claude/skills/sdlc-studio/scripts/critic.py brief --unit <id> --seat engineering 2>&1 >/dev/null | wc -c -> 0 bytes on stderr; grep -c fingerprint over stdout -> 0.
F2: critic.py record --unit US0001 --verdict approve --brief x -> exit 0, row records `x`.
F4: delete the `any(f['origin'] != ORIGIN_PRE_EXISTING ...)` line and run the full suite -> green.
F5: git show 3570c94a:.claude/skills/sdlc-studio/scripts/critic.py and compare the docstring against the shipped body.

## Proposed Fix

`cmd_brief` prints the fingerprint on stderr with the record command to run. `cmd_record` validates the value against the 12-lowercase-hex shape and NOTES (does not refuse) a value matching no brief the repo can currently produce, because the brief embeds artefact state that legitimately moves. The untagged guard gains a direct test using the row shape in the shipped log. All three docstrings are corrected to state both covering shapes and that an untagged finding never qualifies.

## Acceptance Criteria

- [ ] The behaviour described is corrected: Five findings from the EP0194 batch-boundary review, all classified NEW against base 3570c94a by `git log -S`.
- [ ] Following the recorded steps no longer reproduces the defect: F1: python3 .claude/skills/sdlc-studio/scripts/critic.py brief --unit <id> --seat engineering 2>&1 >/dev/null | wc -c -> 0 bytes on stderr; grep -c fingerprint...
- [ ] The proposed fix lands, pinned by a test: `cmd_brief` prints the fingerprint on stderr with the record command to run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | independent-critic (engineering/qa/product seats) | Filed |
