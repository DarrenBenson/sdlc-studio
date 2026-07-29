# BG0311: Close-owed 'push/release guard' is enforced at neither moment: no pre-push hook, no CI flag, and --release does not bind

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/tsd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

The TSD documents --require-close as a Blocking push-or-release guard and reference-retro.md says it is 'enforced at the push/release moment', but nothing at either moment runs it: gate.py binds the close-owed lane only when the flag is passed, --release does not imply it, the TSD's own pre-release stage prescribes plain gate.py --release, no pre-push hook exists, CI runs the plain gate, and the `close_guard.py` fallback is wired nowhere - reproducing the exact 'ceremony with no detector' failure the lane was built to close.

## Steps to Reproduce

Evidence (Bound-lane table line 421; CI/CD stage 4 line 532; gate.py lines 1595-1597; reference-retro.md line 56; help/gate.md lines 168-206): gate.py:1595-1597 'if `require_close`: ... registry["close-owed"]'; tsd.md:532 pre-release stage omits the flag; .githooks/ contains only pre-commit and commit-msg; lint.yml:60 runs plain gate.py; help/gate.md:176-183 shows the flag only as a manual snippet.

## Proposed Fix

Bind the close-owed lane into --release (or add a pre-push hook / CI step running gate --require-close), and update the TSD stage and reference-retro.md to describe the binding that actually executes.

## Acceptance Criteria

### AC1: a release binds the close-owed guard

- **Given** `gate.py --release`
- **When** it is read
- **Then** `tag_check` REFUSES, naming the units - a release shipping work no sprint closed asserts a record that was never written, and this is the moment the specs promised enforcement and got none
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagRefusesAnOwedCloseTests::test_a_tag_is_refused_while_a_close_is_owed
- **Verified:** yes (2026-07-29)

### AC2: the ordinary gate does not

- **Given** a mid-sprint commit on a trunk-based repo
- **When** it is read
- **Then** a tag with nothing owed is allowed - a gate that always refuses is not a gate, and neither `--release` nor an ordinary push binds the lane, because blocking every push on a trunk-based repo would train the bypass the guard exists to prevent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_release_cut.py::TagRefusesAnOwedCloseTests::test_a_tag_with_nothing_owed_is_allowed
- **Verified:** yes (2026-07-29)

### AC3: the lane is bound, so it cannot be deselected

- **Given** `--release --skip close-owed`
- **When** it is read
- **Then** the run is refused, because a release verdict printed over a deselected lane is the false assurance this gate exists to refuse
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::CloseOwedLaneIsOptInTests::test_the_lane_is_bound_so_the_flag_cannot_be_deselected
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
