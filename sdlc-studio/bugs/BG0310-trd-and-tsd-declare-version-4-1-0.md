# BG0310: TRD and TSD declare version 4.1.0 against shipped 5.0.0 with the v5 architecture absent, and nothing gates spec version

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/trd.md
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d); agent; skill v5.0.0

## Summary

Both specs state 'the document version tracks the product version' yet declare 4.1.0 after 5.0.0 was cut: the TRD omits the v5 architecture entirely (goal ladder, plan-review pass D0061, run-archive D0043, delegated sign-off disclosure D0059), the TSD's Last Updated contradicts its own revision history and pins a test-noise baseline of 233 against the ratcheted 129, and no checker enforces any of it - `check_versions.py` never references prd/trd/tsd and the doc-freshness lane covers LATEST.md only.

## Steps to Reproduce

Evidence (trd.md header lines 4-6 and section 1 Coverage (lines 37-39); tsd.md header lines 4-6/17-18, lines 211-214, line 651): SKILL.md frontmatter version 5.0.0; package.json 5.0.0; CHANGELOG [5.0.0] 2026-07-26; sprint.py GOALS ladder and `_disclose_delegated_signoffs`, `run_state.py` `ARCHIVE_REL` - none in trd.md; tsd.md:4 'Version: 4.1.0', :5 'Last Updated: 2026-07-17' vs a 2026-07-24 revision row, :211-212 baseline 233 vs tools/skill-tests.sh `TEST_NOISE_BASELINE` 129; grep 'tsd|prd|trd' tools/`check_versions.py` returns nothing.

## Proposed Fix

Run a spec-truth refresh bringing TRD and TSD to 5.0.0 (documenting the goal ladder, plan review, run archive, delegated sign-off, and current baselines/headers), and extend `check_versions.py` or the doc-freshness lane to fail when a spec's declared version trails the shipped version.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d) | Filed |
