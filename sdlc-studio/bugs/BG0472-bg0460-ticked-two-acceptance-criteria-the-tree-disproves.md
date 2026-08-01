# BG0472: BG0460 ticked two acceptance criteria the tree disproves, and its verifiers bypassed the function they name

> **Status:** Fixed
> **Severity:** High
> **Points:** 3
> **Verification depth:** functional (retitled through `artifact.py retitle` so H1, slug, index row and one inbound reference moved together. Both verifiers rewritten to drive `close_dry_run`; the seat's gutting mutant now KILLS both, where it previously survived both. A first repair of AC4's verifier still survived, because mocking every chain step made a gutted preview satisfy it - the assertion now requires the preview to have covered the chain)
> **Affects:** sdlc-studio/stories/US0555-sprint-close-dry-run-reports-every-unmet-prerequisite.md, changelog.d/BG0460.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings classified by execution. Repaired in the same session; recorded here because the repair is post-close work on a unit already at Fixed, and must be a filed unit rather than an ad-hoc edit.

Two of BG0460's three criteria were recorded met and are not. AC2 required the 'all seven steps' claim to be retired from the story surface; `US0555` was byte-identical to the base ref and still carried it in its title and its I-want line, against a ten-step chain. AC3 required US0555's AC4 and AC5 verifiers to call `close_dry_run`; both still asserted `_dry_run_result` over a hand-built list, so gutting `close_dry_run` to a fixed clean result left them passing, and an AST scan found no test anywhere following a clean dry run with a real close. Separately `changelog.d/BG0460.md` described the gate as reported `unevaluated` - the behaviour round 3 reverted - while the shipped code reports `ok` when the preflight ran it.

## Steps to Reproduce

1. git diff --quiet edb9fdf0 HEAD -- sdlc-studio/stories/US0555-*.md -> identical.
2. Gut `close_dry_run` to return a fixed clean result; run only the two named verifiers -> 2 passed, mutant SURVIVED. Control: CloseChainCoverageTests -> 8 failures.
3. AST scan for a test calling both `close_dry_run` and the real chain -> none.
4. grep the changelog for 'unevaluated' against the shipped note(step, "ok", ...).

## Proposed Fix

Retitle the story through `artifact.py retitle` so H1, slug, index row and inbound references move together; correct the I-want line; rewrite both verifiers to drive `close_dry_run` and assert the preview covered the chain, so the gutting mutant dies; correct the changelog to the shipped behaviour.

## Acceptance Criteria

- [x] The behaviour described is corrected: Found by an independent seat briefed from the SHIPPED `critic.py brief`, unit-scoped to the unit's own `Affects` against base `edb9fdf0`, with findings...
- [x] The proposed fix lands, pinned by a test: Retitle the story through `artifact.py retitle` so H1, slug, index row and inbound references move together; correct the I-want line; rewrite both verifiers to...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Filed |
