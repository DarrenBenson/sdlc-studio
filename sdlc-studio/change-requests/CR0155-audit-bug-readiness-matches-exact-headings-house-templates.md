# CR-0155: audit bug-readiness matches exact headings; house templates (Symptom/Root cause/Fix (proposed)) read as underspecified

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Depends on:** CR-0158
> **Affects:** scripts/audit.py (`_bug_underspecified`, lines ~72-83)
> **Found by:** a consuming project running the sprint design rung

## Summary

`audit.py._bug_underspecified` decides a bug is ready by exact-substring heading match:

```python
has_repro = "## steps to reproduce" in low or "## reproduction steps" in low
has_fix   = "## proposed fix" in low or "## fix description" in low
```

A consuming project's house bug template documents bugs as **`## Symptom` -> `## Root cause` ->
`## Fix (proposed)` -> `## Verify`** - a root-cause analysis that is *richer* than bare repro steps,
plus a proposed fix. But none of those strings match: `Symptom`/`Root cause` are not `Steps to
Reproduce`, and `## Fix (proposed)` is the same two words as `Proposed Fix` merely reordered. So the
tranche audit flagged **all 6 bugs in the sprint as `underspecified`** ("add Steps to Reproduce and a
Proposed Fix") when every one carries a full symptom, root cause, proposed fix, and verify line. On
the design rung this reads as `0/6 ready` - a false gate on a well-groomed tranche.

This is the **third instance this session of one root pattern** (with CR0153 - reconcile's exact
`Status` column match - and CR0154 - the single `-consultations` companion suffix): a check hard-codes
an exact string and every project whose legitimate template varies gets a false negative. The pattern
is worth naming, not just patching three times.

## Proposed change

1. **Recognise the semantic equivalents** in `_bug_underspecified`:
   - repro evidence: `Steps to Reproduce` / `Reproduction Steps` **or** `Symptom` + `Root cause`
     (a documented symptom and cause is stronger evidence than repro steps, not weaker).
   - fix: `Proposed Fix` / `Fix Description` / `Fix (proposed)` / `Fix` - match on the heading
     *containing* the word `fix` in a proposal sense, not an exact ordered string.
2. **Or make required sections configurable** in `sdlc-studio/.config.yaml`
   (`bug_ready_sections: {repro: [...], fix: [...]}`), defaulting to today's set for back-compat, so a
   project declares its own template vocabulary once.
3. **Consider the general lesson (cross-ref CR0153/CR0154):** the skill has several exact-string
   convention gates (status-column name, companion suffix, section headings). A shared, tolerant
   convention layer (config-declared or normalised match) would retire the whole class instead of
   patching each site. Worth an RFC if a fourth instance appears.

## Acceptance Criteria

- [ ] A bug documented as `## Symptom` / `## Root cause` / `## Fix (proposed)` is **ready** (not
      `underspecified`); a bug with only a title and no symptom/cause/fix is still flagged.
- [ ] `## Fix (proposed)` and `## Proposed Fix` are treated identically; matching does not depend on
      word order.
- [ ] The default behaviour for the existing `Steps to Reproduce` + `Proposed Fix` template is
      unchanged; a regression test pins the house-template variant now passing and a genuinely-empty
      bug still failing (mutation-checked).

## Notes / provenance

Found running `audit.py check --ids ...` (the sprint design-rung pre-flight) over a 6-bug tranche in a
consuming project: `0/6 ready, all underspecified`, though each bug carried Symptom + Root cause + Fix
(proposed) + Verify. The false gate would push an operator to pad already-complete bugs to satisfy the
checker rather than the reader - the same backwards incentive noted in CR0147 (doc_freshness test
count). Sibling exact-match gates: CR0153 (reconcile Status column), CR0154 (companion suffix).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-project dogfooding) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-project dogfooding) | Filled in from the sprint design-rung audit: exact heading match flags a richer house bug template (Symptom/Root cause/Fix (proposed)) as underspecified; propose semantic-equivalent or config-driven section matching. Third instance of the exact-string-gate pattern (CR0153/CR0154). |
