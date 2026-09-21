# BG0721: the duplicate lens cannot tell one change filed twice from one method applied to several disjoint scopes

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py, .claude/skills/sdlc-studio/scripts/tests/test_backlog_triage.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`backlog_triage`'s duplicate lens pairs units by shared `Affects` plus wording similarity. RUN-01M306PY split an audit across four cluster stories - same method, four disjoint sets of requests - and the lens flagged US0849/US0850, US0849/US0851 and US0850/US0851 as likely the same change filed twice, at 60% similarity over a shared `Affects` of `sdlc-studio/change-requests, sdlc-studio/rfcs`. They are not duplicates; they are one method applied to four scopes that do not overlap at all, which is the shape any deliberately parallelised sweep takes. The lens is not wrong about what it measures - the wording IS similar and the declared surface IS shared - it is that neither signal can see the SCOPE a story carries in its body. The practical harm is that a run which parallelises by scope generates false duplicates proportional to how well it parallelised, and a verifier written against 'no duplicate findings' becomes unsatisfiable, which is how this was found.

## Steps to Reproduce

1. Create three or more stories that apply the same method to disjoint scopes, each declaring the same folder in `Affects` - the natural shape when a sweep is split for parallel agents. 2. Run `backlog_triage.py check`. 3. Every pair is reported as a likely duplicate. Observed on RUN-01M306PY with US0849, US0850 and US0851.

## Proposed Fix

Give the lens a way to see that two units cover disjoint work. The cheapest signal already present is the body: these stories each enumerate the ids they rule, and the sets are disjoint - two units whose enumerated scopes do not intersect are not duplicates however similar their prose. Failing that, let a unit declare `Scope:` explicitly and exempt pairs with disjoint scopes, or treat a shared `Affects` that names a DIRECTORY rather than a file as weaker evidence than a shared file, since a directory is shared by everything that touches it. Add a criterion covering three stories with identical wording and disjoint enumerated scopes, asserting no duplicate finding.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `backlog_triage`'s duplicate lens pairs units by shared `Affects` plus wording similarity.
- [ ] **AC2** The proposed fix lands, pinned by a test: Give the lens a way to see that two units cover disjoint work.

## A second shape, found in the same run

The cluster stories were the loud instance; the sharper one is a DEFECT CASE AND ITS PAIRED POSITIVE CONTROL. US0793 asserts that a row whose kill node is not named reads `killed-elsewhere`; US0794 asserts that a row whose kill node IS named still reads `killed`. The lens reports them as likely the same change filed twice, at 50% similarity over four shared files.

They will ALWAYS look like duplicates, because a control is defined by differing from its case in exactly one respect. This project's own testing practice demands that pairing - `a positive control beside each refusal` - so the lens penalises the discipline the repo requires, and it penalises it most precisely where the discipline is followed best. Any fix must let these two coexist without a per-pair exemption, or the exemption list becomes the real backlog.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
