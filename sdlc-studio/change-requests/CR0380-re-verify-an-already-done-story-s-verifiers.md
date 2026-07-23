# CR-0380: re-verify an already-Done story's verifiers, so a stale green is caught between closes not only at a manual sweep

> **Status:** Superseded
> **Triage:** Superseded by BG0256 (RUN-01KY5Y3W): selector_resolves (collection-only) + unresolvable_stamps + conformance dead-stamp refusal + verify_ac stamps deliver the stale-green catch repo-wide; only a transition-hook sliver remains
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py,.claude/skills/sdlc-studio/scripts/conformance.py,.claude/skills/sdlc-studio/scripts/verify_ac.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0231 has two halves. The detection half - an unresolved pytest verifier (deleted node exits 4, stale -k exits 5) is attributed as vacuous with the re-point remedy rather than misreported as a code failure - is fixed in `verify_ac.` This is the trigger half: nothing re-runs an already-Done storys verifiers, so a green annotation persists until something forces a full sweep. US0097 read Verified: yes for weeks because its named test had been deleted and no re-run was ever triggered - the AC text was unchanged, so the fingerprint-based freshness check saw nothing stale. The Done freshness gate in transition.py only fires at the transition INTO Done, and conformance trusts the stored **Verified:** annotation rather than re-resolving the verifier. So a story Done today can have its test deleted tomorrow and stays green.

## Impact

This is the root cause behind BG0231s headline. Deferred deliberately from the bug rather than crammed in under close-time pressure, because the fix is a WHEN-to-re-verify decision across the whole repo and interacts directly with the sprint-cost concern in RFC0048: re-running every verifier at every close or gate is exactly the kind of cost addition to weigh, not add reflexively. A cheap static resolution (does the named file exist; for a ::node, does the name appear in it) at the Done freshness gate and in conformance would catch the deleted-test class without executing anything, and is the likely shape - but it needs its own tests, mutation-check and a decision on where it runs.

## Acceptance Criteria

- [ ] the Done freshness gate treats a story whose verifier no longer statically resolves as stale, requiring re-verification, without executing the verifier
- [ ] conformance reports a Done story whose named verifier cannot be resolved, distinctly from one that never carried a verifier
- [ ] the static resolution adds no test execution to the gate path, so it does not grow the per-commit cost RFC0048 is bounding
- [ ] the check is mutation-verified: a deleted node and a stale -k pattern are both caught, and a live verifier is not false-flagged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
