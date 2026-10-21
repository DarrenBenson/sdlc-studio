# BG1091: US1084's document tests still pass three phrasings they exist to refuse

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_gate_docs.py, changelog.d/BG1091.md
> **Evidence:** US1084 QA review, round 2 (APPROVE), qa-seat-US1084-r1, 2026-10-19, at 69c8c210: [new] items 1 and 3, [pre-existing] item 2.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T19:12:42Z

## Summary

Each survives in isolation at 69c8c210. AC4: a denial of the gate's writes whose subject is a pronoun or a code span ('It writes nothing.', 'It is read-only.', 'The gate (`gate.py`) is read-only.'), because the subject pattern needs the word gate followed by plain words. AC3: 'On a tag push, CI performs `release_cut.py tag-check`.' (verb outside RUNS), 'Tagging a release runs `gate.py --release`.' (outside `TAG_PUSH)`, and a sentence carrying any negation ('..., not a branch push.'). AC2: the TSD framework row at tsd.md:192 names `gate.py --boundary push` beside a push, so a push stage rewritten to run --boundary release still passes. The commit that claimed AC3 refuses such a sentence 'however worded' over-claimed.

## Steps to Reproduce

Apply each phrasing named in the summary to the TRD or TSD and run tools/tests/`test_lean_gate_docs.py`: green.

## Proposed Fix

Scope the AC4 denial check to the gate's own sections, widen AC3's verbs and tag phrases and require the negation to govern the run verb, and judge AC2 on the push stage's own sentences.

## Acceptance Criteria

- [ ] **AC1** Each phrasing named in the summary turns tools/tests/`test_lean_gate_docs.py` red
  - **Verify:** pytest tools/tests/test_lean_gate_docs_phrasings.py::GateDocsPhrasingTests

## Impact

A later edit can restore a false claim about the gate with the document tests green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): Won't Fix, not beneficial (LL0056): it widens prose regexes, which RETRO0135 records as never converging |
