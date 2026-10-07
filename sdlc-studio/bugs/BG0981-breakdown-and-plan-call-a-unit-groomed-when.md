# BG0981: breakdown and plan call a unit groomed when a Verify line is one verify_ac cannot parse

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_breakdown_unparseable_verify.py, changelog.d/BG0981.md
> **Evidence:** homelab RUN-01M4B5HP, US0185 AC1, 2026-10-07
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:40:36Z

## Summary

homelab US0185 AC1 carried ``- **Verify:** `file utilities/fleet/deploy-manifest.yaml` `` (the expression wrapped in backticks). `sprint.py breakdown` reported the batch `0 ungroomed`, `sprint.py plan --write` opened the run on it, and only `verify_ac.py run` at build time refused it: ``"unrecognised verifier '`file' - use a DSL verb ... or prefix an explicit `shell`"``. The grooming gate checks that a criterion HAS a Verify line, not that the line is one the runner accepts, so an AC that can never pass reaches the sprint as groomed. Seen 2026-10-07, skill 6.1.0+12.

## Steps to Reproduce

1. A story whose AC has ``- **Verify:** `file some/path` `` (backticks around the expression)
2. sprint.py breakdown --worklist <it> -> 0 ungroomed
3. sprint.py plan --worklist <it> --write -> run opens
4. `verify_ac.py` run --id <it> -> FAIL: unrecognised verifier '`file'

## Proposed Fix

Have the breakdown census (and so the plan gate) parse each Verify line with the same parser `verify_ac.run` uses, and count an unparseable verifier as ungroomed with `verify_ac`'s own message. `verify_ac` already has a `lint` verb; reuse it rather than a second parser.

## Acceptance Criteria

- [ ] **AC1** A unit whose only Verify line `verify_ac` cannot parse (a backtick-wrapped expression, an unknown verb) is reported ungroomed by `sprint.py breakdown`, with `verify_ac`'s own message
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_breakdown_unparseable_verify.py -k unparseable_verify_is_ungroomed
- [ ] **AC2** `sprint.py plan --write` refuses such a unit through the same gate, and opens no run
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_breakdown_unparseable_verify.py -k plan_refuses_unparseable_verify
- [ ] **AC3** A Verify line `verify_ac` accepts (a DSL verb, `shell`, or a `manual` marker) still counts as groomed
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_breakdown_unparseable_verify.py -k parseable_verify_still_groomed

## Triage

- Reproduced at 8b844a80: `conformance.unit_is_ungroomed('story', ...)` returns `(False, '')` for a criterion whose Verify is `` `file utilities/x.yaml` ``, while `verify_ac.run_verifier` on the same line returns invalid, "unrecognised verifier '`file'". The grooming gate checks that a verifier exists, not that it parses. Not a regression.
- `conformance.py` added to Affects: it holds the grooming predicate `breakdown` and `plan` share. Reuse `verify_ac`'s own parser, as proposed, rather than a second one.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at 8b844a80; tool-derived criteria replaced with three executable ones; conformance.py and a changelog fragment added to Affects; code spans holding backticks double-fenced for markdownlint |
