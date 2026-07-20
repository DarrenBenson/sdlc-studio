# BG0231: a Done story stays green after the test its AC names is deleted: freshness tracks the AC text, not the existence of its verifier

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional (5 real-pytest tests: a deleted ::node exits 4 and a stale -k pattern exits 5, both now attributed vacuous with the re-point remedy, not a plain code failure; a real failure stays a plain failure; a real pass is untouched. 4 mutants killed - detection removed (3), exit-5-only misses the deleted node (2), exit-4-only misses the stale pattern (1), and any-kind over-reach caught by the pre-existing shell-verb boundary test (1))
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

## Resolution 2026-07-21 - scope split, no overclaim

Two separable defects lived under this title. Only the first is fixed here.

**Fixed (detection):** an unresolved pytest verifier - a deleted `::node` (exit 4) or a stale
`-k` pattern (exit 5) - was reported as a plain code failure, indistinguishable from a real
regression. It is now attributed **vacuous** with the "re-point the Verify line" remedy, scoped
to pytest's own no-collection exit codes so a shell verb's nonzero exit stays a failure it owns.
This is what makes any sweep meaningful: when verification runs, a deleted test now reads as a
verifier problem, not broken code. Mutation-verified.

**Split to CR0380 (trigger):** nothing re-runs an already-Done story's verifiers, so a green
persists between closes until a full sweep forces a re-run - the reason US0097 read
`Verified: yes` for weeks. That is a WHEN-to-re-verify decision across the whole repo, cost-
sensitive and interacting with RFC0048, so it is tracked forward rather than crammed in under
close-time pressure. The detection fix here is its prerequisite.
