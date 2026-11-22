# BG1704: BG0999 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, changelog.d/BG0999.md
> **Created:** 2026-11-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-22T14:21:23Z

## Summary

BG0999 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair's direct-parent rule for a skill script (`Path(cleaned).parent.name in ("", "scripts")`, critic.py:5053-5054, added in ac68018d) is pinned by no test against a path nested beneath a `scripts/` directory. The test's refusals (test\_critic.py:2209-2211) cover a sibling directory (`lib/decisions.py`), a directory whose name only ends in scripts (`subscripts/decisions.py`) and a project directory (`src/gate.py`), but no path such as `scripts/lib/gate.py`. A mutant that accepts any ancestor named scripts (`Path(cleaned).parent.name == "" or "scripts" in Path(cleaned).parent.parts`) survives CallerNamedTests. I re-tested that branch alone through `critic.py caller-check`, over a consuming fixture whose tree holds only src/thing.py and tests/test\_thing.py. The shipped code reports `Caller: scripts/lib/gate.py run` as caller-unresolved, and the mutant resolves it. That path is in neither tree, so the changelog's "as is a name found in neither tree" (changelog.d/BG0999.md:8) and the bug's Proposed Fix ("A name that exists in neither tree still fails") both refuse it. Round one asked for a lookup by "a path ending in scripts/ and the name". The repair holds that rule against a sibling directory, a name suffix and a non-script file. It does not hold it against a deeper path, so a later edit that widens the rule stays green; RULINGS: Round one's finding "A Caller naming a project path that does not exist now resolves whenever its file name matches" is CLOSED as reported. Through the CLI, `Caller: src/gate.py run` is caller-unresolved at 93c4b9cd, and `README.md` is no longer a skill name (`_skill_script_names` keeps only `.py` files). The mutant dropping the parent check and the mutant dropping the `.py` filter are each killed by CallerNamedTests. My mutant that widens the parents to bin, tools and src is killed too. The one survivor is the nested-path finding above. Claim inventory of the repaired changelog, docstrings and comment: "a Python script of the loaded skill", "named bare or under a `scripts/` directory", `src/gate.py` and `README.md` "still reported unresolved", and "a bare word or a stem never resolves against the skill" are TRUE by execution. "The line `sprint close` prints from it" is TRUE by trace only (the same `caller_findings`). "as is a name found in neither tree" is TRUE of the shipped code but held by no test for a nested path (the finding above). `verify_ac.py run --id BG0999 --dry-run` gives 1/1 pass and CallerNamedTests gives 3 passed. The author's replayed mutants are all killed. Out of scope: the `uncommitted_notice`, `_undeclared_block`, `_merge_resolutions` and `carried_review_base` hunks belong to BG0970, BG0982, BG1120 and BG1108 and are not judged here.

## Steps to Reproduce

1. Read the round 2 REJECT of BG0999 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0999 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] The repair's direct-parent rule for a skill script (`Path(cleaned).parent.name in ("", "scripts")`, critic.py:5053-5054, added in ac68018d) is pinned by no test against a path nested beneath a `scripts/` directory. The test's refusals (test\_critic.py:2209-2211) cover a sibling directory (`lib/decisions.py`), a directory whose name only ends in scripts (`subscripts/decisions.py`) and a project directory (`src/gate.py`), but no path such as `scripts/lib/gate.py`. A mutant that accepts any ancestor named scripts (`Path(cleaned).parent.name == "" or "scripts" in Path(cleaned).parent.parts`) survives CallerNamedTests. I re-tested that branch alone through `critic.py caller-check`, over a consuming fixture whose tree holds only src/thing.py and tests/test\_thing.py. The shipped code reports `Caller: scripts/lib/gate.py run` as caller-unresolved, and the mutant resolves it. That path is in neither tree, so the changelog's "as is a name found in neither tree" (changelog.d/BG0999.md:8) and the bug's Proposed Fix ("A name that exists in neither tree still fails") both refuse it. Round one asked for a lookup by "a path ending in scripts/ and the name". The repair holds that rule against a sibling directory, a name suffix and a non-script file. It does not hold it against a deeper path, so a later edit that widens the rule stays green
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG0999 AC1 still passes: A criterion whose Caller is decisions.py waive resolves when that script exists in the loaded skill and not in the project tree
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CallerNamedTests::test_the_named_caller_must_resolve_when_the_caller_is_a_skill_script

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-22 | sdlc-studio | Filed |
