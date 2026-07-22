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

**On the two `Verified: yes` stamps above.** Both criteria were run and passed on
2026-07-22 (`verify_ac run --story` against this file, 2/2). The stamps are a dated
record, NOT a live guarantee: `walk_stories` yields only `US` records, so no routine
sweep re-runs a bug's verifier and these will read green forever regardless of what
happens to the tests they name. That is BG0256, open in this same batch, and this
artefact is an instance of it rather than an exception to it.

**What this guard still does NOT close, after the round-1 repair.** Named here rather than
left for the next reader to find, because the first version of this fix shipped believing it
was complete.

- A `shell`-prefixed grep bypasses it entirely. `shell` is the documented escape hatch and
  narrowing it is a separate decision.
- An expression whose resolved files are a MIX of markdown and code is allowed, by the same
  all-or-nothing rule that keeps the guard from second-guessing a legitimate verifier.
- The resolved reading depends on the filesystem the lint runs on. The written reading is
  kept as a floor for exactly that reason, and a test pins a case that distinguishes them.
  **Withdrawn from an earlier version of this list:** the claim that a directory is "dropped
  without `-r`". That was false - `_build_command` always emits a recursive runner - and the
  guard no longer behaves that way. It is named here rather than quietly deleted, because
  this artefact asserted the deleted rule as shipped for one round after it was withdrawn.
- The walk is derived from `rg --files` where rg is present, so it honours .gitignore, hidden
  files and symlinks exactly as the runner does. Without rg the runner reads everything and
  so does the fallback. A guard that walked differently from the runner was round 3's escape.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
| 2026-07-22 | sdlc-studio | Fixed. Acceptance criteria added after the engagement floor refused the commit: two source files with an `Affects` field but no criterion is unplanned work, which is the floor's whole point and this run's own bar for a bug. |
| 2026-07-22 | sdlc-studio | Round 2 REJECT repaired: a FOURTH escape (a bare directory) traced to a comment restating grep's semantics rather than deriving this DSL's, which always recurses. The guard now reads `_build_command`'s argv, so guard and runner share one parse. |
| 2026-07-22 | sdlc-studio | Round 3 REJECT repaired, and UNREVIEWED - `review.max_rounds` is 3 and the ceiling is spent. An EIGHTH escape, verified passing: the guard shared the runner's parse but not its WALK, so one hidden, gitignored or symlinked non-markdown file made an all-prose directory read as mixed and pass. The walk now derives from `rg --files`. A surviving mutant that flipped a nested all-markdown directory from refused to allowed is also closed; every directory fixture had been flat, so the tests and the mutant agreed by construction. |
| 2026-07-22 | sdlc-studio | REPAIRED after the closing review REJECTED. The guard judged only the tokens as WRITTEN and was defeated three ways: a directory glob (`sdlc-studio/reviews/*`), a flag read as the pattern (`grep -c "x" a.md`), and a bare recursive directory. It now judges the files actually READ - flags split from the pattern, globs expanded, directories walked under `-r` and dropped without it - with the written tokens kept as a floor. The claim that the previously surviving mutant was EQUIVALENT was FALSE and is withdrawn; that mutant is now killed, along with four others. The repair plan itself was attacked before execution and REFUTED: the first proposed fix closed none of the three escapes. |
