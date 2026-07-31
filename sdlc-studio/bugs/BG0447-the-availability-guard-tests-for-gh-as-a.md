# BG0447: the availability guard tests for `gh` as a bare substring, so `nightly`, `highlighted` and `though` all satisfy the half of the contract that names the tool

> **Status:** Fixed
> **Verification depth:** functional (tests red-first, both directions; BG0454's fix exposed a false allowlist exemption the rotted-entry guard then caught)
> **Severity:** High
> **Points:** 2
> **Affects:** tools/tests/test_availability_contract.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees); agent; v5.0.0
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`states_fail_loud` returns `bool(_STATES_FAIL_LOUD.search(passage)) and "gh" in passage.lower()`. The second half is a substring test on two of the commonest letter pairs in English prose. Its own docstring states the reason it exists - 'a passage naming `gh` proves nothing about the abort ... requiring both in the same located block is what stops an unrelated sentence elsewhere in the file satisfying it' - and the implementation is satisfied by any passage containing `nightly`, `highlighted`, `though`, `walkthrough` or `high`. The guard was written against exactly this class (its round-1 REJECT was that a whole-file `assertRegex` for the letters `fail` could not discriminate) and the repair reintroduced the identical defect in the half that was added to fix it.

## Steps to Reproduce

Executed at d7a1ad8f, 2026-07-30:

```text
python3 -c "print('gh' in 'sync aborts non-zero on any highlighted error'.lower())"
True
```

The round-2 reviewer demonstrated the consequence by gutting the live documents in an isolated worktree: replacing the personas bullet with `- Offline-capable core pipeline; sync aborts non-zero on any highlighted error` - every mention of `gh` removed - left the suite green at 6 tests. Replacing the whole PRD Availability clause with `The nightly job aborts non-zero on error.`, which names neither `gh` nor sync, also left it green.

Mutant M1 (drop the `"gh" in passage` half entirely) SURVIVED against the full 555-test tools suite: the clause can be deleted with nothing going red, so it is unpinned as well as wrong. The three negative probes in the test file never exercise it.

## Proposed Fix

Match `gh` as a token, not a substring - a word boundary, or better, the actual form the contract uses (a backticked `gh`, or `gh` followed by a subcommand). Then pin it with a mutant-shaped test: a passage that states the abort but names no tool must be REFUSED, and one containing `nightly` but not `gh` must also be refused. The current negative probes pass without ever reaching this half of the conjunction, which is why M1 survived.

Two sibling findings from the same reviewer belong in the same slice, since they are the same defect class in the same file: the graceful denylist is scoped to the single located line, so a contradicting 'degrades gracefully' bullet elsewhere in `personas.md` passes (the file can hold both answers to the one question the guard exists to unify); and the fixture list at :191 passes for the wrong reason - `'...soft no-op in the absence of gh'` is caught by `soft no-op`, not by `in the absence of`, so the comment claiming all four named spellings are covered is false. Unbundled, `gracefully-degrades` and `in the absence of gh, sync is skipped` both miss.

## Acceptance Criteria

### AC1: the `gh` half matches the TOOL, not two letters

- **Given** a passage stating the fail-loud contract about something else entirely, containing `nightly`, `highlighted`, `though`, `walkthrough`, `high` or `eight`
- **When** the guard judges it
- **Then** it is refused - `"gh" in passage.lower()` is a substring test on one of the commonest letter pairs in English, so the half ADDED to make this guard discriminate discriminated no better than the whole-file letter match its own round-1 REJECT was about
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_the_gh_half_matches_the_TOOL_not_two_letters
- **Verified:** yes (2026-07-31)

### AC2: the forms the docs actually use are still accepted

- **Given** the tool named bare, backticked, possessive and parenthesised
- **When** the guard judges each
- **Then** all are accepted - word-bounding must not trade a guard that cannot discriminate for one that fails on correct documentation
- **Verify:** pytest tools/tests/test_availability_contract.py::AvailabilityContractAgrees::test_the_gh_half_still_accepts_the_forms_the_docs_USE
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | amigo seat review of RUN-01KYPZ1G (independent, isolated worktrees) | Filed |
