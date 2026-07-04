# CR-0148: name the close-of-sprint adversarial critic pass as a hard sprint step (re-verify against the critic's own repros)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

In both of today's sprints, the highest-value defects were caught by neither unit tests, nor per-unit review, nor the gate - but by a full-diff adversarial critic pass at sprint close: the BG0046 sibling-parser escape (a closed bug still reproducible in the field shape) and the mutation gate's unviable-as-killed false evidence (6.2% of mutants). Both passes went request-changes -> fix-test-first -> the critic re-ran ITS OWN repros -> approve. reference-sprint.md's close currently names reconcile + review; the adversarial full-diff pass with repro re-verification is where the catches actually happened and it deserves to be a named, non-optional step.

**Not a second gate.** This sharpens the critic step the sprint loop already runs (the
conformance `critiqued` stage and the close's review leg) - it does not bolt a parallel
critic ceremony beside them. The delta is precisely: full-diff scope at close, refute-not-
confirm framing, and the SAME critic instance re-running its own repros before approve.

## Acceptance Criteria

- [ ] reference-sprint.md's sprint-review step names the adversarial full-diff critic pass: independent instance, refute-not-confirm framing, findings with repros, fixes seen RED, the SAME critic re-verifies each repro before approve
- [ ] the conformance critiqued stage's guidance and help/sprint.md point at it; the retro template carries a 'critic loop observed' section
- [ ] CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Operator review applied: framed explicitly as sharpening the existing critic step, guarding against process-for-its-own-sake |
