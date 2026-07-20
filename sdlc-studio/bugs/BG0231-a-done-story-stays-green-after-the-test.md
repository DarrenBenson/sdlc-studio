# BG0231: a Done story stays green after the test its AC names is deleted: freshness tracks the AC text, not the existence of its verifier

> **Status:** Open
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/scripts/conformance.py
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

US0097 has read Verified: yes (2026-07-09) since commit 95aaacd deleted the test its AC names. The test `test_root_is_alias_of_repo_root` was added by US0097 own delivery commit (20ae964) and removed by the later CLI-grammar change; the AC text never changed, so the fingerprint-based freshness check saw nothing stale and the annotation was never re-run. A pytest node that no longer exists exits 5 with nothing collected, which is indistinguishable from a pass unless the run actually happens. Exposed by a full `verify_ac` sweep during RUN-01KY03GS, not by any gate: the per-story runs this project does at close only touch the sprint units, so a Done story elsewhere can rot indefinitely. Two more surfaced in the same sweep - US0112 asserts zero disclosure warnings against 19 today, and US0115 asserts a non-stale mutation report - both conditions true when they shipped and false now.

## Steps to Reproduce

Run `verify_ac` over ALL stories rather than a sprint subset. US0097 AC flips from yes (2026-07-09) to no, and conformance reports 3 non-conformant Done units that no gate had previously named. Confirm the cause with: git log -S `test_root_is_alias_of_repo_root` --all, which shows the test added in 20ae964 and deleted in 95aaacd.

## Proposed Fix

Treat a verifier that resolves to nothing as a distinct outcome from pass and from fail, and make the AC fingerprint cover the verifier target rather than only the AC prose - an AC whose named test disappears is stale by construction, which is the fact the fingerprint exists to catch. A pytest exit 5 (no tests collected) must never be readable as green; the same holds for a grep verb whose file is gone. Separately, run the full sweep at close rather than only the sprint units, since the rot this found is by definition outside the batch being worked on.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Filed |
