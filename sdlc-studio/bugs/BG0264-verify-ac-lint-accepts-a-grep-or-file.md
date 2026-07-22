# BG0264: verify_ac lint accepts a grep or file verifier pointing at markdown, which is how four acceptance criteria passed on prose asserting the opposite of their own wording

> **Status:** Fixed
> **Verification depth:** functional - 7 new unit tests over lint_markdown_evidence and cmd_lint's exit code, plus the full 199-test verify_ac suite green; the guard's own mutation run killed 4 of 5 hand-applied mutants (all>any, always-authoring, case-folding, refusal-returns-0) and the fifth is equivalent, recorded as such in the docstring rather than forced
> **Severity:** High
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py,.claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Raised by the QA seat in the RUN-01KY5EJX plan review, as the single cheapest guard on a Sprint Goal all three seats judged otherwise self-asserted.

`lint_verifier` (`verify_ac.py`:371) flags an expression that would fall through to `shell` and looks like a mis-written runner call. It says nothing about a `grep` or `file` verifier whose target is a markdown file. That combination is the escape this project has already paid for: in RUN-01KY3MFX, US0310's four `grep` verifiers all PASSED against prose asserting the exact opposite of their criteria, and the published count of verified criteria was four higher than the evidence supported. Recorded as L-0208 - grep cannot verify a claim about meaning.

The mechanism is that the author writes the documentation line and the verifier that greps for it in the same sitting, so the assertion is true of the line just written and tells nobody anything about the behaviour. It is self-confirming by construction, and it is the cheapest verifier to write, so it is what an author under batch pressure reaches for.

The QA seat's framing is worth keeping: a bar phrased as a counterfactual - would this fail if the behaviour were absent - cannot be evaluated by any run, because it is a claim about a program that does not exist. A path-suffix test needs no counterfactual and kills the class mechanically. A legitimate documentation criterion remains expressible: it says `manual` and is visible as such.

Urgent now because RUN-01KY5EJX is about to author roughly 32 sets of criteria for behaviour that does not exist yet, which is precisely the condition under which only `grep` and `file` over existing text can go green.

## Steps to Reproduce

1. Author a story AC with `- **Verify:** grep "the guard refuses an unresolvable path" .claude/skills/sdlc-studio/reference-sprint.md`. 2. Write that sentence into that reference file. 3. Run `verify_ac` lint, then `verify_ac` run. Observed: lint is silent and the AC passes, having proven only that the author wrote a sentence. Expected: lint refuses the verifier for a behavioural AC on a Draft or Ready story, and names `manual` as the honest alternative for a genuine documentation criterion.

## Proposed Fix

Add a path-suffix check to the lint: a `grep` or `file` verifier whose resolved target is `*.md` is refused for an AC on a Draft or Ready story. Keep it a REFUSAL rather than an advisory - `lint_verifier`'s existing nudges are advisory and this class has already shipped four false passes past a human review. A documentation criterion says `manual` and is then visible in the manual count rather than hidden in the passing one. Prove the guard with the bug it defends against (LL0010): the test asserts that US0310's actual shipped verifier expressions would have been refused.

## Acceptance Criteria

### AC1: the four verifiers that actually escaped are refused, and a behavioural one is not

- **Given** the verifier expressions US0310 shipped in `e1bc477`, recovered from git rather
  than reconstructed
- **When** `lint_markdown_evidence` judges each, alongside a `pytest` verifier, a `manual`
  one, a `grep` over a Python file, and a mixed target list naming both markdown and code
- **Then** all four originals are refused and none of the others is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k "test_every_verifier_us0310_shipped_is_refused or test_a_behavioural_verifier_is_untouched or test_a_mixed_target_list_is_not_refused or test_file_verb_on_markdown_is_refused"
- **Verified:** yes (2026-07-22)

### AC2: the refusal fails the command while authoring, and lifts once the story has shipped

- **Given** one story carrying a markdown-only `grep` verifier
- **When** `verify_ac lint` runs against it at `Draft`, then again at `Done`
- **Then** the first exits non-zero and the second exits zero, so authoring is interrupted
  and a lint over shipped history still runs
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py -k "test_lint_exits_non_zero_on_a_draft_story_and_zero_once_done or test_uppercase_extension_is_refused"
- **Verified:** yes (2026-07-22)

## Resolution

Fixed in `lint_markdown_evidence` and `cmd_lint` (`verify_ac.py`). Seven tests added, the
full 199-test `verify_ac` suite green.

Mutation: five mutants hand-applied with `__pycache__` purged and the suite run under
`python3 -B`. Four killed - `all`→`any`, always-authoring, dropped case folding, and the
refusal returning 0. The fifth, swapping the textual target read for the glob-expanding
one, SURVIVED and is equivalent: `_expand_globs` passes an unmatched glob through literally
(`verify_ac.py`:516), so both forms judge every case here identically. That mutant also
falsified the docstring written beside it, which had justified the choice by a scenario the
code rules out; the stated reason is corrected and the equivalence recorded rather than a
test contrived to kill it. **No claim of mutation coverage is made for that line.**

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed. Acceptance criteria added after the engagement floor refused the commit: two source files with an `Affects` field but no criterion is unplanned work, which is the floor's whole point and this run's own bar for a bug. |
