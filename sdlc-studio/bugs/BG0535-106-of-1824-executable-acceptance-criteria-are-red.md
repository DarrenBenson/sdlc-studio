# BG0535: 106 of 1824 executable acceptance criteria are RED across stories already marked Done, and the lane that would have said so has never run to completion

> **Status:** Open
> **Severity:** High
> **Points:** 8
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01KZCAJX, first completed `--release` run, 2026-08-07. `[FAIL] verify [1666.9s]: 106 red AC(s) ... [645 story/stories, 1824 executable AC(s) in 1666s (batched) - OVER the 600s declared budget]`; `[FAIL] conformance [50.9s]: 1 non-conformant unit(s)`; `gate cost: 1726.7s - OVER the 45s budget by 1681.7s; dominant lane: verify at 1666.9s; 940% slower than the 166.0s baseline`. An earlier attempt the same session died at exit 124 under a 1700s timeout.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

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

- [ ] **AC1** The behaviour described is corrected: The first completed run of `gate.py --release` reports **106 red acceptance criteria out of 1824** across 645 stories - every one on a story already at Done.
- [ ] **AC2** The proposed fix lands, pinned by a test: Two separable problems, and the second is why the first accumulated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
