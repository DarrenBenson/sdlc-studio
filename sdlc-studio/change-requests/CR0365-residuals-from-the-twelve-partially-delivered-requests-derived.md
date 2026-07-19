# CR-0365: Residuals from the twelve partially-delivered requests derived Complete by CR0364

> **Status:** Proposed
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/prd.md, tools/tests/test_trd_freshness.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/reference-rfc.md, .claude/skills/sdlc-studio/templates/workflows/release-gate.md
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M

## Summary

CR0364 derives a request Complete once every child it produced is resolved. An evidence sweep of
all 59 open CRs found that twelve of the requests it derives have children that ARE all resolved
but acceptance criteria of their own that are NOT all met - the decomposition was incomplete, so
the stories delivered less than the request asked for.

Deriving them is correct under the two-backlog doctrine: a request is intake-and-decompose, and
its terminal is a fact about its children, not about its own checkboxes. But the residual work is
real, and without this record it would be absorbed into a Complete status and lost. This CR is
that record. Every item below carries the evidence the sweep found it with.

## The residuals

| From | Residual | Evidence |
| --- | --- | --- |
| CR0281 | AC3: the PRD coverage note names 8 workstreams; the tables also cover lessons ranking, amigo consult, command-surface audit, reconcile-apply index creation, audit cost pre-flight, interactive token capture and backlog triage | prd.md:14-19 |
| CR0284 | AC1 asked for a gate that does not exist (no accuracy condition in close_owed, no hooks dir); VELOCITY.md still missing RETRO0029-0043, 0046, 0047; RETRO0028 0.44x never named in plan output | sprint.py:2513-2527, retros/VELOCITY.md |
| CR0294 | US0166 AC1 and AC2 are still byte-identical whole-file Verify selectors - the duplicate-verifier defect the CR was filed for | US0166 lines 25 and 34 |
| CR0298 | AC2 names reference-retro.md; the close-ceremony report step actually landed in reference-sprint.md. Cross-reference only | reference-sprint.md:181-185 |
| CR0299 | templates/workflows/release-gate.md still presents the strict version check as the enforcement, never mentioning gate.py --release | release-gate.md:44-47 |
| CR0302 | trd.md:32 claims 58 scripts (actual 67); trd.md:637 claims 52 reference and 41 help files (actual 53 and 44) | trd.md:32, :637 |
| CR0304 | AC2 regressed into a FALSE claim: trd.md asserts SKILL.md's type table points upgrade at reference-upgrade.md; SKILL.md has no upgrade row at all | trd.md:466-484 vs SKILL.md:225-250 |
| CR0334 | AC2 is over-broad as written - the fingerprint deliberately excludes AC body prose, and the delivering story made that explicit. Needs an AC correction, not code | verify_ac.py:92-93 |
| CR0338 | The global doc-coverage finding does not name the undocumented item; the remedy says to run doc_coverage.py to find it | conformance.py:341-345 |
| CR0340 | test_relevant omits help/ and SKILL.md, yet three tests read them - a help-only commit skips a suite it can break | .githooks/pre-commit:138 |
| CR0357 | The RFC accept refusal cannot say which scan path produced its list, and the false-positive trade is documented only in a source docstring, not reference-rfc.md | transition.py:322-335, :279-298 |
| CR0363 | No enumeration of the test files the command selects, no out-of-selection warning, no advisory path. AC3 was already satisfied incidentally by existing report-writing code | mutation.py:449, :459-461 |

## Impact

Twelve known defects would otherwise be closed silently at the moment the backlog is being sized
for a launch decision. Two are genuine live defects rather than documentation drift, and both are
guards that do not guard: CR0302's freshness check is anchored to the stale number it exists to
catch (first-match regex, floor-only comparison, so it reports green), and CR0340's skip set lets a
help-only commit bypass a suite that can fail on it. CR0304 is worse than when filed: the document
was corrected into a new inaccuracy.

## Acceptance Criteria

- [ ] each residual above is either fixed, or refiled as its own unit with a reason, or declined in writing - none is silently dropped
- [ ] CR0302's freshness guard is anchored to the claim it checks, not to the first match in the file, and fails on the stale counts it currently reports green on
- [ ] CR0340's test-relevant set covers every path a shipped test reads, so no commit can skip a suite that its own change can break
- [ ] CR0304's TRD sentence states what SKILL.md actually contains
- [ ] the AC-correction cases (CR0334, and CR0284's AC1) are recorded as AC defects rather than carried as outstanding build work

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Body written from the five-agent evidence sweep, ahead of the CR0364 derivation |
