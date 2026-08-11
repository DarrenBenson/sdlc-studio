# BG0535: 106 of 1824 executable acceptance criteria are RED across stories already marked Done, and the lane that would have said so has never run to completion

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** High
> **Points:** 8
> **Affects:** tools/verify-corpus.sh, tools/verify-corpus-baseline.txt, tools/tests/test_verify_corpus.py, .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** RUN-01KZCAJX, first completed `--release` run, 2026-08-07. `[FAIL] verify [1666.9s]: 106 red AC(s) ... [645 story/stories, 1824 executable AC(s) in 1666s (batched) - OVER the 600s declared budget]`; `[FAIL] conformance [50.9s]: 1 non-conformant unit(s)`; `gate cost: 1726.7s - OVER the 45s budget by 1681.7s; dominant lane: verify at 1666.9s; 940% slower than the 166.0s baseline`. An earlier attempt the same session died at exit 124 under a 1700s timeout.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

> **RE-MEASURED 2026-08-09 on 167e7e38: 53 red of 1876, not 106 of 1824.** The second completed
> `--release` run in this bug's history: `[FAIL] verify [1663.0s]: 53 red AC(s) ... [661
> story/stories, 1876 executable AC(s) in 1662s (batched) - OVER the 600s declared budget]`,
> `gate cost: 1778.0s`. The title and the figures below are the 2026-08-07 measurement and are
> left standing rather than rewritten, because a number that moved by half is itself the finding
> and LATEST.md had warned the original was never re-run. Sampling the ten the new run names
> confirms the rot diagnosis and sharpens it: `US0063::AC1` invokes `audit_check.py` and
> `US0070::AC1` invokes `test_review_generate.py`, neither of which exists on disk;
> `US0021::AC1`, `US0040::AC3`, `US0042::AC2` and `US0052::AC4` name test methods absent from
> files that do still exist. These are stale selectors, not broken features, so the repair is
> mechanical and the guard against recurrence is the part that has to land with it - CR0508
> already describes it: a `Verify:` selector naming a test that does not exist is accepted at
> write time. Ruled under D0133: repair all of them rather than grandfather them. Planned in
> charter SC0003.

The first completed run of `gate.py --release` reports **106 red acceptance criteria out of 1824** across 645 stories - every one on a story already at Done. It had never completed before: the lane takes 1667 seconds against a declared 600s budget, and an earlier attempt in this same session was killed by a 28-minute timeout, so its verdict has never been read.

This is the class the release gate exists to catch, and it is the one thing v5 cannot ship over. `README.md:399` says acceptance criteria "are executable and get run". For stories that is nearly true - 0.9% are unparseable, per BG0530's corpus scan - but 106 of the ones that DO parse are red, so the sentence is true of the mechanism and false of the corpus.

The failures look like ordinary rot rather than one cause: verifiers naming tests that were renamed or removed (`test_rfc.py::DigestTests::test_ready_when_recommendation_and_no_open`), shell verifiers whose commands have moved (`shell npm run lint:links`, `shell python3 tools/check_links.py`), and a coverage gate pinned at `--fail-under=80`. Each was green when its story closed; nothing has re-run them since, because the only lane that does is the one that never completes.

A second lane failed beside it: `conformance`, on 1 non-conformant unit.

## Steps to Reproduce

1. `python3 .claude/skills/sdlc-studio/scripts/gate.py --root . --release`. 2. Allow at least 30 minutes - the verify lane alone took 1666.9s, 940% over its 166s baseline, and a shorter timeout kills it before it reports (exit 124, which reads exactly like a failure if the code is not checked). 3. It exits 1 with `[FAIL] verify: 106 red AC(s)` and `[FAIL] conformance: 1 non-conformant unit(s)`.

## Proposed Fix

Two separable problems, and the second is why the first accumulated.

The RED criteria need triage rather than a blanket repair: a verifier naming a test that no longer exists is a different defect from one whose assertion now fails, and only the second says anything about the code. `verify_ac lint` and CR0508's `selector_resolves` already distinguish them - run those first and split the 106 before touching any of them.

The lane must become runnable. At 1667s against a 600s budget it is outside any usable timeout, so nothing runs it and the corpus rots unobserved between releases. Either it runs on a schedule the way `lint:corpus` does - `.github/workflows/lint.yml` already has that shape, gated on `schedule` and `workflow_dispatch` - or the verify lane is sharded so a partial answer arrives regularly. A gate whose cost puts it beyond every practical invocation is a gate nobody runs, which is how 106 red criteria accumulated without anyone seeing one.

## Acceptance Criteria

Narrowed by the recorded ruling of 2026-08-11: this bug closes on the two things that stop the
rot - the write-time guard and a lane that reads the count between releases. The stale-selector
repairs are v5.1 work, because a repair that merely makes a criterion pass is worse than the red
it replaced: it turns a visible stale selector into an invisible vacuous one, and each of the 58
has to still discriminate for the criterion it was written for.

The guard half of this bug is NOT restated here as a criterion. It is US0667's, whose
criterion already says both writers refuse a selector naming a test that does not exist,
and BG0570's, which narrowed that refusal to a typo. A criterion here would share their
verifier, and two criteria sharing a verifier cannot both discriminate - a regression in
either fails both and neither says which. What this bug closes on that nothing else does
is the LANE: the count is now read between releases instead of never.

### AC1: the count is read between releases, and a rise blocks

- **Given** the reason these criteria rotted unobserved - the release verify lane costs ~2,145s
  against a 600s budget, so nothing ran it and its verdict was never read
- **When** the scheduled corpus lane runs and finds MORE than the recorded baseline
- **Then** it BLOCKS, naming the rise, so a new dead selector is caught by the lane rather than by
  the next release.

- **Verify:** pytest tools/tests/test_verify_corpus.py -k a_count_above_the_baseline_blocks
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/verify-corpus.sh`, compare only for a fall so a rise passes.

### AC2: a fall blocks too, so the baseline empties

- **Given** a baseline that only ever tolerates, which is one that never empties
- **When** the lane finds FEWER than the recorded baseline
- **Then** it BLOCKS as well, requiring the figure to be lowered in the same commit, so a repair is
  banked rather than left as tolerance available to admit a different defect later.

- **Verify:** pytest tools/tests/test_verify_corpus.py -k a_count_below_the_baseline_also_blocks
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/verify-corpus.sh`, return early when the observed count is under baseline.

### AC3: the lane reads the tool's own total

- **Given** that the first version of this lane counted output rows containing `::` and reported 3
  for a corpus of 5, because a `-k` pattern and a bare file target carry no node address
- **When** the lane needs the count
- **Then** it reads the total the tool itself printed, because the number a lane prints is the one
  nobody re-derives - and a lane that miscounts is worse than no lane.

- **Verify:** pytest tools/tests/test_verify_corpus.py -k the_count_is_the_tools_own_total_not_a_count_of_node_shaped_rows
- **Verified:** yes (2026-08-11)
- **Mutant:** in `tools/verify-corpus.sh`, count rows matching the node separator instead of parsing the total.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `tools/verify-corpus.sh`, compare only for a fall so a rise passes | the count is read between releases, and a rise blocks |
| AC2 | in `tools/verify-corpus.sh`, return early when the observed count is under baseline | a fall blocks too, so the baseline empties |
| AC3 | in `tools/verify-corpus.sh`, count rows matching the node separator instead of parsing the total | the lane reads the tool's own total |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
